from pymediainfo import MediaInfo
from config import *
from random import choices
from string import ascii_uppercase, digits
from multiprocessing import Pool
import subprocess
import os

tmp_dir += ''.join(choices(ascii_uppercase + digits, k=20)) + '\\'


# Удаление тегов. На вход - путь к файлу mkv.
def del_tags(mkv):
    # Удаление тегов делается через ключ "--tags all: ". Пробел на конце важен.
    subprocess.run(f'"{mkvpropedit}" {mkv} --tags all: ', shell=True)
    return None


def smart_opus(media_info, active):
    smart_opus_dict = {
        160: '160k',
        144: '144k',
        128: '128k',
        112: '112k',
        96: '96k',
        74: '74k'
    }
    if active:
        if create_opus_lq:
            return smart_opus_dict[74]
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


def command_generator(del_data=False, del_subs=False,
                      opus=False, opus_from_51=False, opus_smart_activate=True):
    commands = []
    str_commands = []
    files = filter(lambda x: x.endswith('.mkv'), os.listdir(from_dir))
    for file1 in files:
        media_info = MediaInfo.parse(from_dir + file1)
        fr_den = media_info.tracks[1].framerate_den
        fr_num = media_info.tracks[1].framerate_num
        if fr_den is None or fr_num is None:
            rate = media_info.tracks[1].frame_rate
        else:
            rate = f'{fr_num}/{fr_den}'
        command = {'-hide_banner': '',
                   '-i': f'"{from_dir + file1}"',
                   '-c:v': 'libx265',
                   '-preset': f'{hevc_preset}',
                   '-crf': f'{hevc_crf_level}',
                   '-vf': '"format=yuv420p10le"',
                   '-x265-params': f'"level=5.1:ref=6"',
                   '-r': f'{rate}'}
        # '-x265-params': f'"level=5.1:crf={hevc_crf_level}:ref=6"',
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
        command['-f'] = f'matroska "{tmp_dir + file1}"'
        commands.append(command)
    for command in commands:
        str_command = f'"{ffmpeg}" '
        for key in command:
            str_command += f'{key} {command[key]} '
        str_commands.append(str_command)
    return str_commands


def fix_files(fix_delay=False):
    if not os.path.isdir(to_dir):
        os.makedirs(to_dir)
    # Получаем список файлов в папке
    files = os.listdir(tmp_dir)
    # Оставляем тольео mkv
    mkvs = filter(lambda x: x.endswith('.mkv'), files)
    for mkv in mkvs:
        del_tags(tmp_dir + mkv)  # Удаляем теги
        rel = {}  # Сюда будем складывать задержку аудио
        sub_count = 0
        audio_count = 0
        sub_default = None
        media_info = MediaInfo.parse(tmp_dir + mkv)  # Получаем информацию о конкретном файле
        for track in media_info.tracks:
            if track.track_type == 'Audio':  # Берём только аудио
                rel[track.track_id] = -track.delay_relative_to_video
                audio_count += 1
            if track.track_type == 'Text':
                sub_count += 1
                sub_default = track.default
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
                        f'--track-name !num:"Original{suffix}" --language !num:{lang} --default-track !num:no --forced-track !num:no --sync !num:!rel ']
                else:
                    audio = [
                        '--track-name !num:AniLibria.TV --language !num:rus --default-track !num:yes --forced-track !num:yes --sync !num:!rel ',
                        f'--track-name !num:Original --language !num:{lang} --default-track !num:no --forced-track !num:no --sync !num:!rel ']
        else:
            if audio_count == 1:
                audio = [
                    '--track-name !num:AniLibria.TV --language !num:rus --default-track !num:yes --forced-track !num:yes ']
            elif audio_count == 2:
                if create_opus:
                    audio = [
                        '--track-name !num:AniLibria.TV --language !num:rus --default-track !num:yes --forced-track !num:yes ',
                        f'--track-name !num:"Original{suffix}" --language !num:{lang} --default-track !num:no --forced-track !num:no ']
                else:
                    audio = [
                        '--track-name !num:AniLibria.TV --language !num:rus --default-track !num:yes --forced-track !num:yes ',
                        f'--track-name !num:Original --language !num:{lang} --default-track !num:no --forced-track !num:no ']
        video = [
            f'--track-name !num:"Original{suffix}" --language !num:{lang} --default-track !num:yes --forced-track !num:yes ']
        tags = ['--no-track-tags --no-global-tags --title "" ']
        params = video + audio + subs + tags
        track_num = 0
        cmd_param = ''
        for param in params:
            cmd_param += param.replace('!num', str(track_num)).replace('!rel', str(rel.get(track_num + 1)))
            track_num += 1
        mkv_hevc = mkv
        for r in (('Anilibria', 'AniLibria'),
                  (' ', '_'),
                  ('.', '_', mkv_hevc.count('.') - 1),
                  ('_Tv', '_TV'),
                  ('_tV', '_TV'),
                  ('_tv', '_TV'),
                  (rename_mask_from, rename_mask_to)):
            mkv_hevc = mkv_hevc.replace(*r)
        command = f'"{mkvmerge}" -o "{to_dir}{mkv_hevc} " {cmd_param} "{tmp_dir + mkv}"'
        print(command)

        process = subprocess.run(command, shell=True)
        if process.returncode == 0:
            os.remove(tmp_dir + mkv)
    return None


def create_dirs():
    if not os.path.isdir(to_dir):
        os.makedirs(to_dir)
    if not os.path.isdir(tmp_dir):
        os.makedirs(tmp_dir)
    # if not os.path.isdir(f"{tmp_dir}source\\"):
    #     os.makedirs(f"{tmp_dir}source\\")
    return None


def worker(cmd):
    # subprocess.call(cmd)
    subprocess.call(cmd, creationflags=subprocess.CREATE_NEW_CONSOLE)


if __name__ == "__main__":
    cmds = command_generator(del_data=False, del_subs=False, opus=create_opus,
                             opus_smart_activate=True)
    print(f'В очередь пришло файлов: {len(cmds)}\n')
    create_dirs()
    success = 0
    errors = 0
    summary = len(cmds)
    # запускаю его после точки входа и никаких проблем.
    with Pool(processes=runners_count) as pool:
        for i in pool.imap_unordered(worker, cmds):
            cmd = cmds[success + errors]
            file = cmd[cmd.find('-i "') + 4:cmd.find('" -c')]
            print(f'Завершена работа над файлом {file}')
            if i is None:
                success += 1
            else:
                print(f'Произошла ошибка в команде {cmds[success + errors]}')
                errors += 1
            summary -= 1
            print(f'Успешно: {success}')
            print(f'Ошибки: {errors}')
            print(f'Осталось: {summary}')
            print('\n')
        print('\n\n')
    if need_fix:
        fix_files(delay)

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
