from pymediainfo import MediaInfo
import subprocess
import os

mode = 1
fromdir = r'E:\2019\Bokutachi wa Benkyou ga Dekinai - AniLibria.TV [WEBRip 1080p]\\'     # Папка, из которой будем брать файлы.
tmp_dir = r'C:\temp\\'   # Папка, в которую будут писаться временные файлы.
todir = r'D:\2019\Bokutachi wa Benkyou ga Dekinai - AniLibria.TV [WEBRip 1080p HEVC]\\'  # Папка, в которую будем записывать готовое.
ffmpeg = r'C:\Program Files\ffmpeg\bin\ffmpeg.exe'
mkvpropedit = r'C:\Program Files\MKVToolNix\mkvpropedit.exe'     # Путь к mkvpropedit.exe
mkvmerge = r'C:\Program Files\MKVToolNix\mkvmerge.exe'   # Путь к mkvmerge.exe
# В данном случае важно экранировать слэши (\\)


# Удаление тегов. На вход - путь к файлу mkv.
def del_tags(mkv):
    # Удаление тегов делается через ключ "--tags all: ". Пробел на конце важен.
    subprocess.run('"{mkvpropedit}"'.format(mkvpropedit=mkvpropedit)+' {mkv} --tags all: '.format(mkv=mkv), shell=True)
    return None


def encode_video(from_dir, to_dir):
    if not os.path.isdir(to_dir):
        os.makedirs(to_dir)
    files = os.listdir(from_dir)
    mkvs = filter(lambda x: x.endswith('.mkv'), files)
    for file in mkvs:
        media_info = MediaInfo.parse(from_dir + file)
        fr_den = media_info.tracks[1].framerate_den
        fr_num = media_info.tracks[1].framerate_num
        ffmpeg_param = '-hide_banner ' \
                       '-i "{input}" ' \
                       '-preset medium ' \
                       '-c:v libx265 ' \
                       '-vf format=yuv420p10le ' \
                       '-x265-params "level=5.1:crf=23:ref=6" ' \
                       '-acodec copy ' \
                       '-map 0 ' \
                       '-r {framerate_num}/{framerate_den} ' \
                       '-f matroska "{output}"'.format(input=from_dir+file, output=to_dir+file,
                                                       framerate_num=fr_num, framerate_den=fr_den)
        process = subprocess.run('"{ffmpeg}" '.format(ffmpeg=ffmpeg)+ffmpeg_param, shell=True)
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
        del_tags(from_dir+mkv)   # Удаляем теги
        rel = []    # Сюда будем складывать задержку аудио
        sub_count = 0
        media_info = MediaInfo.parse(from_dir+mkv)   # Получаем информацию о конкретном файле
        for track in media_info.tracks:
            if track.track_type == 'Audio':     # Берём только аудио
                rel.append(-track.delay_relative_to_video)  # Берём значение задержки и меняем её знак
            if track.track_type == 'Text':
                sub_count += 1
        # А дальше начинается магия. Для каждого потока в mkv прописываются свои значения.
        # Важно, чтобы потоки шли в таком порядке:
        # 1. Видео
        # 2. Русская звуковая дорожка
        # 3. Японская звуковая дорожка
        # 4. Субтитры с надписями на русском языке
        # 5. Полные субтитры на русском языке
        # Переменная cmd - это строка, которую мы потом передадим в subprocess.
        if sub_count == 2:
            subs = '--track-name 3:"Надписи [AniLibria.TV]" --language 3:rus --default-track 3:yes --forced-track 3:yes --sub-charset 3:UTF-8 ' \
                   '--track-name 4:"Полные [AniLibria.TV]" --language 4:rus --default-track 4:no --forced-track 4:no --sub-charset 4:UTF-8 '
        elif sub_count == 1:
            subs = '--track-name 3:"Полные [AniLibria.TV]" --language 3:rus --default-track 3:no --forced-track 3:no --sub-charset 3:UTF-8 '
        else:
            subs = None

        cmd = '"{mkvmerge}"'.format(mkvmerge=mkvmerge)+' -o "{output}" ' \
                       '--track-name 0:"Original [GeeKaZ0iD]" --language 0:jpn --default-track 0:yes --forced-track 0:yes '\
                       '--track-name 1:AniLibria.TV --language 1:rus --default-track 1:yes --forced-track 1:yes --sync 1:{rel1} '\
                       '--track-name 2:Original --language 2:jpn --default-track 2:no --forced-track 2:no --sync 2:{rel2} '.format(
                                        output=to_dir+mkv.replace('].mkv', '_HEVC].mkv'),
                                        rel1=rel[0], rel2=rel[1]) \
                       + subs + \
                       '"{input}"'.format(input=from_dir+mkv)
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
            os.remove(from_dir+mkv)
    # Если видим сообщение "Multiplexing took 4 seconds.", то всё идёт хорошо.
    return None


encode_video(fromdir, tmp_dir)
fix_files(tmp_dir, todir)
