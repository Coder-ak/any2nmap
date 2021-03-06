# Any2Nmap converter

Конвертер GPX, KML, KMZ, JPG, JSON или CSV форматов в формат json для Блокнота народного картографа Народных Карт.

![alt tag](https://github.com/Coder-ak/gpx2nmap/blob/master/gpx2nmapgui-screen.png?raw=true)

Выберите исходный файл, выберите директорию, куда будет сохранён результат, нажмите RUN.

Например, выберите папку Яндекс.Диска, где сохраняются данные Блокнота Картографа (Яндекс.Диск/Приложения/Блокнот картографа Народной карты/), создайте папку с произвольными именем (например, 2016-08-17), скопируйте в неё фото сделанные при создании точек. В эту папку будет сохранён созданный index.json.

При обработке KMZ файлов, находящиеся внутри архива фотографии будут также распакованы в выходную папку. К пути файлов будет добавлена папка по названию KMZ файла из которого они были извлечены.

В CSV файлах может присутствовать заголовок с названиями полей [Latitude], [Longitude]. Если заголовок не найден, первая колонка похожая на координаты станет Latitude, следующая Longitude.

Из JPG будут извлечены данные EXIF GPS.

Можно выбрать одновременно несколько файлов, все они будут обработаны и результат объединён в выходном файле index.json.

Автор не несет ответственности за результаты работы программы, вы используете её на свой страх и риск.

Фото из GPX берутся из расширения extensions:picture

Пример GPX файла
```
<?xml version="1.0" encoding="UTF-8"?>
<gpx xmlns="http://www.topografix.com/GPX/1/1" version="1.1" creator="AlpineQuest 1.4.22" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:schemaLocation="http://www.topografix.com/GPX/1/1 http://www.topografix.com/GPX/1/1/gpx.xsd">
<wpt lat="46.4542527" lon="30.7308448">
<time>2016-08-04T05:20:23Z</time>
<name>Название метки</name>
<desc>Описание метки</desc>
<cmt>Комментарий метки</cmt>
<extensions>
<aq:picture xmlns:aq="http://www.psyberia.net/res/GPX/1/1/">2016-07-03_10-01-07.JPG</aq:picture>
</extensions>
</wpt>
<rte>
<name>пеш</name>
<rtept lat="46.4519739" lon="30.7377532">
</rtept>
<rtept lat="46.4522297" lon="30.7372664">
</rtept>
</rte>
<trk>
<name>вокруг дома</name>
<trkseg>
<trkpt lat="46.4537109" lon="30.7331238">
</trkpt>
<trkpt lat="46.4536108" lon="30.7332947">
</trkpt>
<trkpt lat="46.4535843" lon="30.7333732">
</trkpt>
</trkseg>
</trk>
</gpx>
```

Консольная версия утилиты gpx2nmap
```
usage: gpx2nmap.py [-h] [-f FOLDER_NAME] [-t FILE_TYPE] [-p] input_file

positional arguments:
  input_file            Input file name

optional arguments:
  -h, --help            show this help message and exit
  -f FOLDER_NAME, --folder-name FOLDER_NAME
                        Folder name in Yandex.Disk
  -t FILE_TYPE, --file-type FILE_TYPE
                        Set file type to FILE_TYPE. Ex.: -t gpx
  -p, --print           Print output to stdout
```
input_file - исходный GPX файл, folder_name - название папки, которое будет добавлено к пути фотографии из GPX extensions. Если что-то пошло не так, напишите автору: alexcoder@gmail.com.

Например, выберите папку Яндекс.Диска, где сохраняются данные Блокнота Картографа (/Приложения/Блокнот картографа Народной карты/), создайте папку с текущей датой, положите в неё фото из GPX файла и скопируйте туда созданный index.json.

В работе утилиты используются сторонние модули gpxpy: https://github.com/tkrajina/gpxpy, pykml и lxml.
```
pip install gpxpy pykml lxml
```
