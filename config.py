suffix = ''    # Суффикс после имени оригинальной дорожки

fromdir = r'C:\temp\\'
todir = r'A:\AniLibria.TV\Hot releases\\'
tmp_dir = r'C:\tedmp\fdsdsfdsf\\'


need_encode = True      # Видео будет скодировано
need_fix = True        # Дорожки будут исправлены и переименованы
create_opus = True      # Сейчас замутим opus
create_opus_lq = True
prepare = False          # Будет полностью готовый HEVC
need_merge = False             # Собираем матрешку в штатном режиме
is51 = True     #Будет подготовлен звук из дорожки 2.0

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


runners_count = 3
