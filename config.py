suffix = ' [GeeKaZ0iD]'  # Суффикс после имени оригинальной дорожки

from_dir = r'C:\temp\\'
to_dir = r'Z:\Ongoing\Golden Kamuy 3 - AniLibria.TV [WEBRip 1080p HEVC]\\'
tmp_dir = r'C:\tedmp\\'

need_encode = True  # Видео будет скодировано
need_fix = True  # Дорожки будут исправлены и переименованы
create_opus = False  # Сейчас замутим opus
create_opus_lq = False
is51 = False  # Будет подготовлен звук из дорожки 2.0
prepare = False  # Будет полностью готовый HEVC
need_merge = False  # Собираем матрешку в штатном режиме

hevc_crf_level = 23  # default 23
hevc_preset = 'medium'  # ultrafast, superfast, veryfast, faster, fast, medium, slow, slower, veryslow, placebo.

ffmpeg = r'C:\Program Files\ffmpeg\bin\ffmpeg.exe'
mkvpropedit = r'C:\Program Files\MKVToolNix\mkvpropedit.exe'
mkvmerge = r'C:\Program Files\MKVToolNix\mkvmerge.exe'

rename_mask_from = '].mkv'
if create_opus_lq:
    rename_mask_to = '-LQ_HEVC].mkv'
else:
    rename_mask_to = '_HEVC].mkv'

lang = 'jpn'
delay = True

runners_count = 2
