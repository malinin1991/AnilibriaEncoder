from pymediainfo import MediaInfo
from config import *
import subprocess
import multiprocessing
import os


# Удаление тегов. На вход - путь к файлу mkv.
def del_tags(mkv):
    # Удаление тегов делается через ключ "--tags all: ". Пробел на конце важен.
    subprocess.run('"{mkvpropedit}"'.format(mkvpropedit=mkvpropedit) + ' {mkv} --tags all: '.format(mkv=mkv),
                   shell=True)
    return None


def smart_opus(media_info, active):
    smart_opus_dict = {
        160: '160k',
        144: '144k',
        128: '128k',
        112: '112k'
    }
    if active:
        opus_bitrate = smart_opus_dict[160]
        for track in media_info.tracks:
            if track.track_type == 'Audio':
                try:
                    bitrate = int(int(track.fromstats_bitrate) / 1000)
                    if bitrate < opus_bitrate:
                        opus_bitrate = bitrate
                except TypeError:
                    return smart_opus_dict[160]
        for key in smart_opus_dict:
            if key < opus_bitrate:
                opus_bitrate = smart_opus_dict[key]
                break
    else:
        opus_bitrate = smart_opus_dict[160]
    return opus_bitrate


def command_generator(from_dir, to_dir, del_data=False, del_subs=False,
                      opus=False, opus_from_51=False, opus_smart_activate=False):
    commands = []
    str_commands = []
    files = filter(lambda x: x.endswith('.mkv'), os.listdir(from_dir))
    for file in files:
        media_info = MediaInfo.parse(from_dir + file)
        fr_den = media_info.tracks[1].framerate_den
        fr_num = media_info.tracks[1].framerate_num
        if fr_den is None or fr_num is None:
            rate = media_info.tracks[1].frame_rate
        else:
            rate = f'{fr_num}/{fr_den}'
        command = {'-hide_banner': '',
                   '-i': f'"{from_dir + file}"',
                   '-preset': 'medium',
                   '-c:v': 'libx265',
                   '-vf': '"format=yuv420p10le"',
                   '-x265-params': '"level=5.1:crf=23:ref=6"',
                   '-r': f'{rate}'}
        if del_data:
            command['-dn'] = ''
        if del_subs:
            command['-sn'] = ''
        if opus:
            command['-b:a'] = f'{smart_opus(media_info, opus_smart_activate)}'
            command['-c:a'] = 'libopus'
            command['-vbr'] = 'on'
            if opus_from_51:
                command['-af'] = '"pan=stereo|FL < 1.0*FL + 0.707*FC + 0.707*BL|FR < 1.0*FR + 0.707*FC + 0.707*BR"'
        else:
            command['-acodec'] = 'copy'
        command['-map'] = '0'
        command['-f'] = f'matroska "{to_dir + file}"'
        commands.append(command)
    for command in commands:
        str_command = f'"{ffmpeg}" '
        for key in command:
            str_command += f'{key} {command[key]} '
        str_commands.append(str_command)
    return str_commands


def fix_files(from_dir, to_dir, fix_delay=False):
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
        else:
            subs = ['']
        if fix_delay:
            if audio_count == 1:
                audio = [
                    '--track-name !num:AniLibria.TV --language !num:rus --default-track !num:yes --forced-track !num:yes --sync !num:!rel ']
            elif audio_count == 2:
                if create_opus:
                    audio = [
                        '--track-name !num:AniLibria.TV --language !num:rus --default-track !num:yes --forced-track !num:yes --sync !num:!rel ',
                        '--track-name !num:"Original{nick}" --language !num:{lang} --default-track !num:no --forced-track !num:no --sync !num:!rel '.format(
                            lang=lang, nick=suffix)]
                else:
                    audio = [
                        '--track-name !num:AniLibria.TV --language !num:rus --default-track !num:yes --forced-track !num:yes --sync !num:!rel ',
                        '--track-name !num:Original --language !num:{lang} --default-track !num:no --forced-track !num:no --sync !num:!rel '.format(
                            lang=lang)]
        else:
            if audio_count == 1:
                audio = [
                    '--track-name !num:AniLibria.TV --language !num:rus --default-track !num:yes --forced-track !num:yes ']
            elif audio_count == 2:
                if create_opus:
                    audio = [
                        '--track-name !num:AniLibria.TV --language !num:rus --default-track !num:yes --forced-track !num:yes ',
                        '--track-name !num:"Original{nick}" --language !num:{lang} --default-track !num:no --forced-track !num:no '.format(
                            lang=lang, nick=suffix)]
                else:
                    audio = [
                        '--track-name !num:AniLibria.TV --language !num:rus --default-track !num:yes --forced-track !num:yes ',
                        '--track-name !num:Original --language !num:{lang} --default-track !num:no --forced-track !num:no '.format(
                            lang=lang)]
        video = [
            '--track-name !num:"Original {nickname}" --language !num:{lang} --default-track !num:yes --forced-track !num:yes '.format(
                nickname=suffix, lang=lang)]
        tags = ['--no-track-tags --no-global-tags ']
        params = video + audio + subs + tags
        track_num = 0
        cmd_param = ''
        for param in params:
            cmd_param += param.replace('!num', str(track_num)).replace('!rel', str(rel.get(track_num + 1)))
            track_num += 1
        cmd = '"{mkvmerge}"'.format(mkvmerge=mkvmerge) + ' -o {output}'.format(
            output='"' + to_dir + mkv.replace(rename_mask_from,
                                              rename_mask_to)) + '" ' + cmd_param + ' --title "" ' + '"{input}"'.format(
            input=from_dir + mkv)
        print(cmd)

        process = subprocess.run(cmd, shell=True)
        if process.returncode == 0:
            os.remove(from_dir + mkv)
    return None


def create_dirs():
    if not os.path.isdir(todir):
        os.makedirs(todir)
    if not os.path.isdir(tmp_dir):
        os.makedirs(tmp_dir)
    if not os.path.isdir(f"{tmp_dir}source\\"):
        os.makedirs(f"{tmp_dir}source\\")
    return None


def worker(cmd):
    subprocess.call(cmd, creationflags=subprocess.CREATE_NEW_CONSOLE)


if __name__ == "__main__":
    cmds = command_generator(fromdir, tmp_dir, del_data=False, del_subs=False, opus=create_opus,
                             opus_smart_activate=True)
    create_dirs()
    # запускаю его после точки входа и никаких проблем.
    pool = multiprocessing.Pool(processes=runners_count)
    result = pool.map(worker, cmds)
    pool.close()
    pool.join()
    if need_fix:
        fix_files(tmp_dir, todir, delay)

# def merge_hevc(from_dir, to_dir):
#     if not os.path.isdir(to_dir):
#         os.makedirs(to_dir)
#     # Получаем список файлов в папке
#     files = os.listdir(from_dir)
#     # Оставляем тольео mkv
#     mkvs = filter(lambda x: x.endswith('.mkv'), files)
#     for mkv in mkvs:
#         if mkv[0] == 'o':
#             continue
#         del_tags(from_dir + mkv)  # Удаляем теги
#         rel = {}  # Сюда будем складывать задержку аудио
#         sub_count = 0
#         media_info = MediaInfo.parse(from_dir + mkv)  # Получаем информацию о конкретном файле
#         audio_count = 0
#         for track in media_info.tracks:
#             if track.track_type == 'Audio':  # Берём только аудио
#                 rel[track.track_id] = -track.delay_relative_to_video  # Берём значение задержки и меняем её знак
#                 audio_count += 1
#             if track.track_type == 'Text':
#                 sub_count += 1
#                 sub_default = track.default
#         if sub_count == 3:
#             subs = ['--subtitle-tracks 4,5 ',
#                     '--track-name 4:"Надписи" --language 4:rus --default-track 4:yes --forced-track 4:yes --sub-charset 4:UTF-8 ',
#                     '--track-name 5:"Полные" --language 5:rus --default-track 5:no --forced-track 5:no --sub-charset 5:UTF-8 ']
#             order = ['--track-order 1:0,0:1,0:2,0:4,0:5 ']
#         elif sub_count == 2:
#             subs = ['--track-name 3:"Надписи" --language 3:rus --default-track 3:yes --forced-track 3:yes --sub-charset 3:UTF-8 ',
#                    '--track-name 4:"Полные" --language 4:rus --default-track 4:no --forced-track 4:no --sub-charset 4:UTF-8 ']
#             order = ['--track-order 1:0,0:1,0:2,0:3,0:4 ']
#         elif sub_count == 1:
#             if sub_default == 'No':
#                 subs = ['--track-name !num:"Полные" --language !num:rus --default-track !num:no --forced-track !num:no --sub-charset !num:UTF-8 ']
#             elif sub_default == 'Yes':
#                 subs = ['--track-name !num:"Надписи" --language !num:rus --default-track !num:yes --forced-track !num:yes --sub-charset !num:UTF-8 ']
#             order = ['--track-order 1:0,0:1,0:2,0:3 ']
#         else:
#             subs = ['']
#             order = ['--track-order 1:0,0:1,0:2 ']
#         if audio_count == 1:
#             audio = ['--track-name !num:AniLibria.TV --language !num:rus --default-track !num:yes --forced-track !num:yes --sync !num:!rel ']
#         elif audio_count == 2:
#             if create_opus:
#                 audio = ['--track-name !num:AniLibria.TV --language !num:rus --default-track !num:yes --forced-track !num:yes --sync !num:!rel ',
#                     '--track-name !num:"Original{nick}" --language !num:{lang} --default-track !num:no --forced-track !num:no --sync !num:!rel '.format(lang=lang, nick=suffix)]
#             else:
#                 audio = ['--track-name !num:AniLibria.TV --language !num:rus --default-track !num:yes --forced-track !num:yes --sync !num:!rel ',
#                     '--track-name !num:Original --language !num:{lang} --default-track !num:no --forced-track !num:no --sync !num:!rel '.format(lang=lang)]
#         video = [' --no-video ']
#         source1 = ['"{input}" '.format(input=from_dir + mkv)]
#
#         video2 = ['--track-name 0:"Original {nickname}" --language 0:{lang} --default-track 0:yes --forced-track 0:yes "{from_dir}{mkv}" '.format(from_dir=from_dir + r'source\\', mkv=mkv, nickname=suffix, lang=lang)]
#         tags = ['--no-track-tags --no-global-tags ']
#         params = video + audio + subs +source1 + video2 + tags + order
#         track_num = 0
#         cmd_param = ''
#         for param in params:
#             cmd_param += param.replace('!num', str(track_num)).replace('!rel', str(rel.get(track_num+1)))
#             track_num += 1
#         cmd = '"{mkvmerge}"'.format(mkvmerge=mkvmerge) + ' -o {output} '.format(output='"' + to_dir + mkv.replace(rename_mask_from, rename_mask_to)) + '"' + cmd_param
#         process = subprocess.run(cmd, shell=True)
#         if process.returncode == 0:
#             os.remove(from_dir + mkv)
#         else:
#             print(cmd)
#     # Если видим сообщение "Multiplexing took 4 seconds.", то всё идёт хорошо.
#     return None
#
#
# if need_encode:
#     encode_video(fromdir, tmp_dir, prepare, create_opus)
# if need_merge:
#     merge_hevc(tmp_dir, todir)
# if need_fix:
#     fix_files(tmp_dir, todir, delay)
