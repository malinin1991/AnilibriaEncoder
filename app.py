from pymediainfo import MediaInfo
from config import *
import subprocess
import os


# Удаление тегов. На вход - путь к файлу mkv.
def del_tags(mkv):
    # Удаление тегов делается через ключ "--tags all: ". Пробел на конце важен.
    subprocess.run('"{mkvpropedit}"'.format(mkvpropedit=mkvpropedit) + ' {mkv} --tags all: '.format(mkv=mkv),
                   shell=True)
    return None


def encode_video(from_dir, to_dir, prepare_hevc, create_opus):
    if not os.path.isdir(to_dir):
        os.makedirs(to_dir)
    files = os.listdir(from_dir)
    mkvs = filter(lambda x: x.endswith('.mkv'), files)
    for file in mkvs:
        media_info = MediaInfo.parse(from_dir + file)
        fr_den = media_info.tracks[1].framerate_den
        fr_num = media_info.tracks[1].framerate_num
        if fr_den is None or fr_num is None:
            rate = media_info.tracks[1].frame_rate
        else:
            rate = '{framerate_num}/{framerate_den}'.format(framerate_num=fr_num, framerate_den=fr_den)
        if prepare_hevc:
            ffmpeg_param = '-hide_banner ' \
                           '-i "{input}" ' \
                           '-preset medium ' \
                           '-c:v libx265 ' \
                           '-vf format=yuv420p10le ' \
                           '-x265-params "level=5.1:crf=23:ref=6" ' \
                           '-r {rate} ' \
                           '-an ' \
                           '-dn ' \
                           '-sn ' \
                           '-f matroska "{output}"'.format(input=from_dir + file, output=to_dir + 'source\\' + file,
                                                           rate=rate)
        elif create_opus:
            if is51:
                ffmpeg_param = '-hide_banner ' \
                               '-i "{input}" ' \
                               '-preset medium ' \
                               '-c:v libx265 ' \
                               '-c:a libopus -b:a 160000 -vbr on ' \
                               '-vf format=yuv420p10le ' \
                               '-af "pan=stereo|FL < 1.0*FL + 0.707*FC + 0.707*BL|FR < 1.0*FR + 0.707*FC + 0.707*BR" ' \
                               '-x265-params "level=5.1:crf=23:ref=6" ' \
                               '-map 0 ' \
                               '-r {rate} ' \
                               '-f matroska "{output}"'.format(input=from_dir + file, output=to_dir + file, rate=rate)
            else:
                ffmpeg_param = '-hide_banner ' \
                               '-i "{input}" ' \
                               '-preset medium ' \
                               '-c:v libx265 ' \
                               '-vf format=yuv420p10le ' \
                               '-x265-params "level=5.1:crf=23:ref=6" ' \
                               '-acodec libopus -b:a 160000 -vbr on ' \
                               '-map 0 ' \
                               '-r {rate} ' \
                               '-f matroska "{output}"'.format(input=from_dir + file, output=to_dir + file, rate=rate)

        else:
            ffmpeg_param = '-hide_banner ' \
                           '-i "{input}" ' \
                           '-preset medium ' \
                           '-c:v libx265 ' \
                           '-vf format=yuv420p10le ' \
                           '-x265-params "level=5.1:crf=23:ref=6" ' \
                           '-acodec copy ' \
                           '-map 0 ' \
                           '-r {rate} ' \
                           '-f matroska "{output}"'.format(input=from_dir + file, output=to_dir + file, rate=rate)
        process = subprocess.run('"{ffmpeg}" '.format(ffmpeg=ffmpeg) + ffmpeg_param, shell=True)
        if process.returncode == 0:
            print('DONE')
    return None


def fix_files(from_dir, to_dir):
    if not os.path.isdir(to_dir):
        os.makedirs(to_dir)
    # Получаем список файлов в папке
    files = os.listdir(from_dir)
    # Оставляем тольео mkv
    mkvs = filter(lambda x: x.endswith('.mkv'), files)
    for mkv in mkvs:
        del_tags(from_dir + mkv)  # Удаляем теги
        rel = {}  # Сюда будем складывать задержку аудио
        sub_count = 0
        audio_count = 0
        sub_default = None
        media_info = MediaInfo.parse(from_dir + mkv)  # Получаем информацию о конкретном файле
        for track in media_info.tracks:
            if track.track_type == 'Audio':  # Берём только аудио
                rel[track.track_id] = -track.delay_relative_to_video
                audio_count += 1
            if track.track_type == 'Text':
                sub_count += 1
                sub_default = track.default
        # А дальше начинается магия. Для каждого потока в mkv прописываются свои значения.
        # Важно, чтобы потоки шли в таком порядке:
        # 1. Видео
        # 2. Русская звуковая дорожка
        # 3. Японская звуковая дорожка
        # 4. Субтитры с надписями на русском языке
        # 5. Полные субтитры на русском языке
        # Переменная cmd - это строка, которую мы потом передадим в subprocess.
        if sub_count == 2:
            subs = [
                '--track-name !num:"Надписи" --language !num:rus --default-track !num:yes --forced-track !num:yes --sub-charset !num:UTF-8 ',
                '--track-name !num:"Полные" --language !num:rus --default-track !num:no --forced-track !num:no --sub-charset !num:UTF-8 ']
        elif sub_count == 1:
            if sub_default == 'No':
                subs = [
                    '--track-name !num:"Полные" --language !num:rus --default-track !num:no --forced-track !num:no --sub-charset !num:UTF-8 ']
            elif sub_default == 'Yes':
                subs = [
                    '--track-name !num:"Надписи" --language !num:rus --default-track !num:yes --forced-track !num:yes --sub-charset !num:UTF-8 ']
        # elif sub_count == 3:
        #     subs = '--subtitle-tracks 4,5 ' \
        #            '--track-name 4:"Надписи [AniLibria.TV]" --language 4:rus --default-track 4:yes --forced-track 4:yes --sub-charset 4:UTF-8 ' \
        #            '--track-name 5:"Полные [AniLibria.TV]" --language 5:rus --default-track 5:no --forced-track 5:no --sub-charset 5:UTF-8 '
        else:
            subs = ['']
        if audio_count == 1:
            audio = [
                '--track-name !num:AniLibria.TV --language !num:rus --default-track !num:yes --forced-track !num:yes --sync !num:!rel ']
        elif audio_count == 2:
            if create_opus:
                audio = ['--track-name !num:AniLibria.TV --language !num:rus --default-track !num:yes --forced-track !num:yes --sync !num:!rel ',
                '--track-name !num:"Original{nick}" --language !num:{lang} --default-track !num:no --forced-track !num:no --sync !num:!rel '.format(
                    lang=lang, nick=suffix)]
            else:
                audio = [
                    '--track-name !num:AniLibria.TV --language !num:rus --default-track !num:yes --forced-track !num:yes --sync !num:!rel ',
                    '--track-name !num:Original --language !num:{lang} --default-track !num:no --forced-track !num:no --sync !num:!rel '.format(lang=lang)]
        video = ['--track-name !num:"Original {nickname}" --language !num:{lang} --default-track !num:yes --forced-track !num:yes '.format(
                nickname=suffix, lang=lang)]
        tags = ['--no-track-tags --no-global-tags ']
        params = video + audio + subs + tags
        track_num = 0
        cmd_param = ''
        for param in params:
            cmd_param += param.replace('!num', str(track_num)).replace('!rel', str(rel.get(track_num+1)))
            track_num += 1
        cmd = '"{mkvmerge}"'.format(mkvmerge=mkvmerge) + ' -o {output}'.format(output='"'+to_dir + mkv.replace(rename_mask_from, rename_mask_to))+'" ' + cmd_param + ' --title "" ' + '"{input}"'.format(input=from_dir + mkv)
        print(cmd)
        # --track-name id:string - имя потока (title)
        # --language - id:string - язык потока
        # --default-track - id:boolean (yes/no) - флаг "по умолчанию" для потока
        # --forced-track - id:boolean (yes/no) - флаг "принудительно" для потока
        # --sync - id:int - cинхронизация потоков. Берём из MediaInfo значение задержки, меняем знак и подставляем.
        # Скрипт это делает автоматом и даже если у потоков будут разные задержки.
        # Пользуясь случаем, передаю привет @basegame :)
        # --sub-charset - id:string - задаёт кодировку для субтитров
        # --track-order - id:id, ... - задаёт порядок потоков
        # -o "{output}" - string - выходной файл. Куда будем сохранять. Сюда должен попастьпуть на файл
        # "{input}" - string - Входной файл. Сюда должен попастьпуть на файл

        process = subprocess.run(cmd, shell=True)
        if process.returncode == 0:
            os.remove(from_dir + mkv)
    # Если видим сообщение "Multiplexing took 4 seconds.", то всё идёт хорошо.
    return None


def merge_hevc(from_dir, to_dir):
    if not os.path.isdir(to_dir):
        os.makedirs(to_dir)
    # Получаем список файлов в папке
    files = os.listdir(from_dir)
    # Оставляем тольео mkv
    mkvs = filter(lambda x: x.endswith('.mkv'), files)
    for mkv in mkvs:
        if mkv[0] == 'o':
            continue
        del_tags(from_dir + mkv)  # Удаляем теги
        rel = {}  # Сюда будем складывать задержку аудио
        sub_count = 0
        media_info = MediaInfo.parse(from_dir + mkv)  # Получаем информацию о конкретном файле
        audio_count = 0
        for track in media_info.tracks:
            if track.track_type == 'Audio':  # Берём только аудио
                rel[track.track_id] = -track.delay_relative_to_video  # Берём значение задержки и меняем её знак
                audio_count += 1
            if track.track_type == 'Text':
                sub_count += 1
                sub_default = track.default
        if sub_count == 3:
            subs = ['--subtitle-tracks 4,5 ',
                    '--track-name 4:"Надписи" --language 4:rus --default-track 4:yes --forced-track 4:yes --sub-charset 4:UTF-8 ',
                    '--track-name 5:"Полные" --language 5:rus --default-track 5:no --forced-track 5:no --sub-charset 5:UTF-8 ']
            order = ['--track-order 1:0,0:1,0:2,0:4,0:5 ']
        elif sub_count == 2:
            subs = ['--track-name 3:"Надписи" --language 3:rus --default-track 3:yes --forced-track 3:yes --sub-charset 3:UTF-8 ',
                   '--track-name 4:"Полные" --language 4:rus --default-track 4:no --forced-track 4:no --sub-charset 4:UTF-8 ']
            order = ['--track-order 1:0,0:1,0:2,0:3,0:4 ']
        elif sub_count == 1:
            if sub_default == 'No':
                subs = ['--track-name !num:"Полные" --language !num:rus --default-track !num:no --forced-track !num:no --sub-charset !num:UTF-8 ']
            elif sub_default == 'Yes':
                subs = ['--track-name !num:"Надписи" --language !num:rus --default-track !num:yes --forced-track !num:yes --sub-charset !num:UTF-8 ']
            order = ['--track-order 1:0,0:1,0:2,0:3 ']
        else:
            subs = ['']
            order = ['--track-order 1:0,0:1,0:2 ']
        if audio_count == 1:
            audio = ['--track-name !num:AniLibria.TV --language !num:rus --default-track !num:yes --forced-track !num:yes --sync !num:!rel ']
        elif audio_count == 2:
            if create_opus:
                audio = ['--track-name !num:AniLibria.TV --language !num:rus --default-track !num:yes --forced-track !num:yes --sync !num:!rel ',
                    '--track-name !num:"Original{nick}" --language !num:{lang} --default-track !num:no --forced-track !num:no --sync !num:!rel '.format(lang=lang, nick=suffix)]
            else:
                audio = ['--track-name !num:AniLibria.TV --language !num:rus --default-track !num:yes --forced-track !num:yes --sync !num:!rel ',
                    '--track-name !num:Original --language !num:{lang} --default-track !num:no --forced-track !num:no --sync !num:!rel '.format(lang=lang)]
        video = [' --no-video ']
        source1 = ['"{input}" '.format(input=from_dir + mkv)]

        video2 = ['--track-name 0:"Original {nickname}" --language 0:{lang} --default-track 0:yes --forced-track 0:yes "{from_dir}{mkv}" '.format(from_dir=from_dir + r'source\\', mkv=mkv, nickname=suffix, lang=lang)]
        tags = ['--no-track-tags --no-global-tags ']
        params = video + audio + subs +source1 + video2 + tags + order
        track_num = 0
        cmd_param = ''
        for param in params:
            cmd_param += param.replace('!num', str(track_num)).replace('!rel', str(rel.get(track_num+1)))
            track_num += 1
        cmd = '"{mkvmerge}"'.format(mkvmerge=mkvmerge) + ' -o {output} '.format(output='"' + to_dir + mkv.replace(rename_mask_from, rename_mask_to)) + '"' + cmd_param
        process = subprocess.run(cmd, shell=True)
        if process.returncode == 0:
            os.remove(from_dir + mkv)
        else:
            print(cmd)
    # Если видим сообщение "Multiplexing took 4 seconds.", то всё идёт хорошо.
    return None


if need_encode:
    encode_video(fromdir, tmp_dir, prepare, create_opus)
if need_merge:
    merge_hevc(tmp_dir, todir)
if need_fix:
    fix_files(tmp_dir, todir)
