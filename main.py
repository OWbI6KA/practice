import eel
import wget
import pandas as pd
from datetime import date

import zoomVideoDownloader
from YandexDiskUploader import YandexDiskUploader

eel.init("web")

filePath = 'accounts.csv'


def getAccountsFromFile(fileName: str):
    return list(map(lambda x: x.strip(';'), pd.read_csv(fileName).iloc[:, 0].to_numpy()))


def fillToFile(strings):
    file = open('accounts.csv', 'w')
    arrStr = strings.split('\r')
    for i in range(len(arrStr)):
        file.write(arrStr[i])
    file.close()


@eel.expose
def main_script(tokenYDisk, tokenZoom, dataFrom, dataTo, file, uploadType, resourceType):
    fillToFile(file)
    if resourceType == "zoom":
        if uploadType == "typeLinks":
            print(zoomVideoDownloader.ZoomDownloader.downloadVideosToFolder(tokenZoom, dateFrom=dataFrom, dateTo=dataTo,
                                                                            pathToFileWithAccounts=filePath))
            disk = YandexDiskUploader(token=tokenYDisk)
            print(disk.UploadVideosFromFolder('temp'))
        else:
            print(zoomVideoDownloader.ZoomDownloader.uploadVideosToDisk(tokenYDisk, tokenZoom, dateFrom=dataFrom,
                                                                        dateTo=dataTo,
                                                                        pathToFileWithAccounts=filePath))
    else:
        print(0)


eel.start('main.html', size=(800, 900))
