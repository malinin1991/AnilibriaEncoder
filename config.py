nickname = 'GeeKaZ0iD'      # Никнейм, который будет подставлен, как автор дорожки

fromdir = r'C:\temp\\'     # Папка, из которой будем брать файлы.
todir = r'C:\temp\\'  # Папка, в которую будем записывать готовое.
tmp_dir = r'C:\temp\\'   # Папка, в которую будут писаться временные файлы.
# В данном случае важно экранировать слэши (\\)

ffmpeg = r'C:\Program Files\ffmpeg\bin\ffmpeg.exe'  # Путь до ffmpeg.exe
mkvpropedit = r'C:\Program Files\MKVToolNix\mkvpropedit.exe'     # Путь к mkvpropedit.exe
mkvmerge = r'C:\Program Files\MKVToolNix\mkvmerge.exe'   # Путь к mkvmerge.exe

need_encode = False      # Требуется ли кодирование видео?
need_fix = True        # Требуется ли исправление дорожжек и переименовывание
create_opus = False      # Требуется ли сделать аудио opus
prepare = False         # Необходимо ли подготовить файлы без звука. Только видеодорожка.

need_merge = False      # Требуется ли объединить скодированную заранее видеодорожку с готовым релизом от технарей?
