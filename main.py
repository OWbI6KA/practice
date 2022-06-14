import eel
import wget
import pandas as pd
from datetime import date

import zoomVideoDownloader
from YandexDiskUploader import YandexDiskUploader

eel.init("web")


def getAccountsFromFile(fileName: str):
    return list(map(lambda x: x.strip(';'), pd.read_csv(fileName).iloc[:, 0].to_numpy()))


def get_path(file):
    wget.download(file, 'docs')
    return 'done'


@eel.expose
def main_script(tokenYDisk, tokenZoom, dataFrom, dataTo, file, uploadType, resourceType):
    print(file)
    if resourceType == "zoom":
        if uploadType == "typeLinks":
            print(zoomVideoDownloader.ZoomDownloader.downloadVideosToFolder(tokenZoom, dateFrom=dataFrom, dateTo=dataTo,
                                                                            pathToFileWithAccounts=file))
            disk = YandexDiskUploader(token=tokenYDisk)
            print(disk.UploadVideosFromFolder('temp'))
        else:
            print(zoomVideoDownloader.ZoomDownloader.uploadVideosToDisk(tokenYDisk, tokenZoom, dateFrom=dataFrom,
                                                                        dateTo=dataTo,
                                                                        pathToFileWithAccounts=file))
    else:
        print(0)


eel.start('main.html', size=(800, 900))
