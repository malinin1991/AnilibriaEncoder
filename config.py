nickname = 'GeeKaZ0iD'      # Никнейм, который будет подставлен, как автор дорожки

fromdir = r'E:\2019\Kenja no Mago - AniLibria.TV [WEBRip 1080p]\\'     # Папка, из которой будем брать файлы.
todir = r'D:\2019\Kenja no Mago - AniLibria.TV [WEBRip 1080p HEVC]\\'  # Папка, в которую будем записывать готовое.
tmp_dir = r'C:\temp\\'   # Папка, в которую будут писаться временные файлы.

ffmpeg = r'C:\Program Files\ffmpeg\bin\ffmpeg.exe'  # Путь до ffmpeg.exe
mkvpropedit = r'C:\Program Files\MKVToolNix\mkvpropedit.exe'     # Путь к mkvpropedit.exe
mkvmerge = r'C:\Program Files\MKVToolNix\mkvmerge.exe'   # Путь к mkvmerge.exe
# В данном случае важно экранировать слэши (\\)

prepare = False         # Необходимо подготовить файлы без звука. Только видеодорожка.
need_encode = True      # Требуется ли кодирование видео?
need_merge = False      # Требуется ли объединить скодированную заранее видеодорожку с готовым релизом от технарей?