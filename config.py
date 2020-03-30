suffix =''    # Суффикс после имени оригинальной дорожки

fromdir = r'D:\source\\'
todir = r'D:\source2\\'

#fromdir = r'Y:\AniLibria.TV\2019\The Dragon Prince 3 - AniLibria.TV [WEBRip 1080p]\\'
#todir = r'Y:\AniLibria.TV\2019\The Dragon Prince 3 - AniLibria.TV [WEBRip 1080p HEVC]\\'
need_encode = True      # Видео будет скодировано
need_fix = False        # Дорожки будут исправлены и переименованы
create_opus = False      # Сейчас замутим opus
prepare = True          # Будет полностью готовый HEVC
need_merge = False             # Собираем матрешку в штатном режиме
is51 = False     #Будет подготовлен звук из дорожки 2.0
#tmp_dir = r'D:\temp\\'
tmp_dir = r'D:\!IN PROGRESS\\'
ffmpeg = r'C:\Program Files\ffmpeg\bin\ffmpeg.exe'
mkvpropedit = r'C:\Program Files\MKVToolNix\mkvpropedit.exe'
mkvmerge = r'C:\Program Files\MKVToolNix\mkvmerge.exe'
rename_mask_from = '].mkv'
rename_mask_to = '_HEVC].mkv'
lang = 'jpn'

delay = True
