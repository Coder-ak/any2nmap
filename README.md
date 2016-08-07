# gpx2nmap

usage: gpx2nmap.py [-h] [-f FOLDER_NAME] input_file

positional arguments:
  input_file            Input file name

optional arguments:
  -h, --help            show this help message and exit
  -f FOLDER_NAME, --folder_name FOLDER_NAME
                        Folder name in Yandex.Disk

input_file - исходный GPX файл, folder_name - название папки, которое будет добавлено к фотографиям из GPX extensions. Если что-то пошло не так, напишите автору: alexcoder@gmail.com.

Например, выберите папку Яндекс.Диска, где сохраняются данные Блокнота Картографа (/Приложения/Блокнот картографа Народной карты/), создайте папку с текущей датой, положите в неё фото из GPX файла и туда же будет сохранён созданный index.json.

Автор не несет ответственности за результаты работы программы, вы используете её на свой страх и риск.
