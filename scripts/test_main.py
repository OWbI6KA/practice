from datetime import datetime
import zoomVideoDownloader
import pandas as pd
from YandexDiskUploader import YandexDiskUploader


def dateParseFromString(dateTimeStr: str):
    try:
        return datetime.strptime(dateTimeStr, "%d/%m/%Y").date()
    except ValueError:
        print('ERROR')


def getAccountsFromFile(fileName: str):
    return list(map(lambda x: x.strip(';'), pd.read_csv(fileName).iloc[:, 0].to_numpy()))


token_yandex = input('Введите токен яндекс диска: ')
token_zoom = input('Введите токен zoom: ')
dateFrom = dateParseFromString(input('От: '))
dateTo = dateParseFromString(input('До: '))
pathToFileWithAccounts = input('Путь к файлу с аккаунтами: ')
mode = input('Режим загрузки (да - загрузка через ссылки / нет - загрузка через локальную папку)')

if mode == 'нет':
    print(zoomVideoDownloader.ZoomDownloader.downloadVideosToFolder(token_zoom, dateFrom, dateTo,
                                                                pathToFileWithAccounts))
    disk = YandexDiskUploader(token=token_yandex)
    print(disk.UploadVideosFromFolder('temp'))
else:
    print(zoomVideoDownloader.ZoomDownloader.uploadVideosToDisk(token_yandex, token_zoom, dateFrom, dateTo,
                                                            pathToFileWithAccounts))
