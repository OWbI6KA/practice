import eel
import pandas as pd

from scripts import get_data
from scripts.YandexDiskUploader import YandexDiskUploader
from scripts.zoomVideoDownloader import ZoomDownloader

eel.init("web")


def get_data(userDataFrom, userDataTo, strDataFrom='', strDataTo=''):
    dataFrom = userDataFrom.split('-')
    dataTo = userDataTo.split('-')
    dataFrom.reverse()
    dataTo.reverse()
    for i in range(3):
        strDataFrom += dataFrom[i] + '/'
        strDataTo += dataTo[i] + '/'
    return strDataFrom[:-1], strDataTo[:-1]


def getAccountsFromFile(fileName: str):
    return list(map(lambda x: x.strip(';'), pd.read_csv(fileName).iloc[:, 0].to_numpy()))


@eel.expose
def main_script(tokenYDisk, tokenZoom, dataFrom, dataTo, file, uploadType, resourceType):
    myDataFrom, myDataTo = get_data(userDataFrom=dataFrom, userDataTo=dataTo)

    if resourceType == "zoom":
        if uploadType == "typeLinks":
            print(ZoomDownloader.downloadVideosToFolder(tokenZoom, dateFrom=dataFrom, dateTo=dataTo,
                                                        pathToFileWithAccounts=file))
            disk = YandexDiskUploader(token=tokenYDisk)
            print(disk.UploadVideosFromFolder('temp'))
        else:
            print(ZoomDownloader.uploadVideosToDisk(tokenYDisk, tokenZoom, dateFrom=dataFrom, dateTo=dataTo,
                                                    pathToFileWithAccounts=file))
    else:
        print(0)


eel.start('main.html', size=(800, 900))
