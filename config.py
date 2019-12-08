nickname = 'GeeKaZ0iD'      # Никнейм, который будет подставлен, как автор дорожки

fromdir = r'D:\AniLibria.TV\2019\No Guns Life - Anilibria.TV [WEBRip 1080p]\\'     # Папка, из которой будем брать файлы.
todir = r'C:\\temp\\No Guns Life - Anilibria.TV [WEBRip 1080p HEVC]\\'  # Папка, в которую будем записывать готовое.

tmp_dir = r'C:\temp2\\'   # Папка, в которую будут писаться временные файлы.
# В данном случае важно экранировать слэши (\\)

ffmpeg = r'C:\Program Files\ffmpeg\bin\ffmpeg.exe'  # Путь до ffmpeg.exe
mkvpropedit = r'C:\Program Files\MKVToolNix\mkvpropedit.exe'     # Путь к mkvpropedit.exe
mkvmerge = r'C:\Program Files\MKVToolNix\mkvmerge.exe'   # Путь к mkvmerge.exe

need_encode = True      # Требуется ли кодирование видео?
need_fix = True        # Требуется ли исправление дорожжек и переименовывание
create_opus = True      # Требуется ли сделать аудио opus
prepare = False         # Необходимо ли подготовить файлы без звука. Только видеодорожка.

need_merge = False      # Требуется ли объединить скодированную заранее видеодорожку с готовым релизом от технарей?

rename_mask_from = '].mkv'
rename_mask_to = '_HEVC].mkv'
is51 = False
lang = 'jpn'
