from threading import Thread
import requests
from datetime import datetime
import pandas as pd
import numpy as np
import os
import Recording
from YandexDiskUploader import YandexDiskUploader
from status import Status


class User:
    def __init__(self, name, id):
        self.name = name
        self.id = id

    def __hash__(self):
        return self.name.__hash__()

    def __eq__(self, other):
        if not isinstance(other, User):
            return False
        return self.name == other.name


class ZoomDownloader:
    __host__ = 'https://api.zoom.us/v2/users'

    @staticmethod
    def getHeaders(token: str) -> dict:
        return {'content-type': 'application/json', 'authorization': f'Bearer {token}'}

    @staticmethod
    def getUserAccountsFromZoom(token: str):
        availableUsers = set()

        try:
            for i in range(1, 26):
                url = ZoomDownloader.__host__ + f'?page_size=300&page_number={i}'
                request = requests.get(url=url, headers=ZoomDownloader.getHeaders(token))
                jsonDict = request.json()
                users = np.vectorize(lambda x: User(x['email'], x['id']))(jsonDict['users'])
                availableUsers.update(users)
        except KeyError:
            return Status.GET_ACCOUNTS_ERROR

        return availableUsers

    @staticmethod
    def getAccountsFromFile(fileName: str):
        try:
            return set(map(lambda x: x.strip(';'), pd.read_csv(fileName).iloc[:, 0].to_numpy()))
        except:
            return Status.GET_ACCOUNTS_ERROR

    @staticmethod
    def getFinalAccounts(zoomAccounts, fileAccounts):
        return list(filter(lambda x: x.name in fileAccounts, zoomAccounts))

    @staticmethod
    def getMeetingsUrls(accounts, dateFrom: str, dateTo: str, token: str):
        meetingsUrls = list()
        for user in accounts:
            url = ZoomDownloader.__host__ + f'/{user.id}/recordings?from={dateFrom}&to={dateTo}'
            request = requests.get(url=url, headers=ZoomDownloader.getHeaders(token))
            jsonDict = request.json()
            try:
                for meeting in jsonDict['meetings']:
                    if meeting['recording_count'] == 0 and meeting['total_size'] < 41943040:
                        continue
                    vec = np.vectorize(
                        lambda x: Recording.Recording(meeting['topic'], x['download_url'] + f'?access_token={token}',
                                                      user.name, x['recording_type'], x['recording_start']))
                    meeting['recording_files'] = list(filter(
                        lambda x: x['file_type'] == 'MP4' and x['recording_type'] == 'shared_screen_with_speaker_view',
                        meeting['recording_files']))
                    if len(meeting['recording_files']) != 0:
                        meetingsUrls.extend(vec(meeting['recording_files']).tolist())
            except:
                continue

        return meetingsUrls

    @staticmethod
    def downloadMeeting(isCorrect, i, filename: str, url: str, token: str):
        try:
            r = requests.get(url, stream=True)
            with open(filename + '.mp4', 'wb') as f:
                for chunk in r.iter_content(chunk_size=1024 * 1024):
                    if chunk:
                        f.write(chunk)
        except:
            isCorrect[i] = False

    @staticmethod
    def downloadAllMeeting(token: str, meetings: list) -> list:
        isCorrect = [True] * len(meetings)
        directory = 'temp'
        threads = []
        if not os.path.exists(directory):
            os.mkdir(directory)
        for i in range(len(meetings)):
            fileName = f'{os.path.join(directory, meetings[i].topic)} {meetings[i].startTime.replace(":", "-")}'
            t = Thread(target=ZoomDownloader.downloadMeeting, args=(isCorrect, i, fileName, meetings[i].url, token))
            threads.append(t)
            t.start()

            if (len(threads) > 100):
                for t in threads:
                    t.join()
                threads.clear()

        for t in threads:
            t.join()
        return isCorrect

    @staticmethod
    def downloadVideosToFolder(token: str, dateFrom: datetime.date, dateTo: datetime.date,
                               pathToFileWithAccounts: str) -> Status:

        zoomAccounts = ZoomDownloader.getUserAccountsFromZoom(token)
        fileAccounts = ZoomDownloader.getAccountsFromFile(pathToFileWithAccounts)
        if zoomAccounts == Status.GET_ACCOUNTS_ERROR or fileAccounts == Status.GET_ACCOUNTS_ERROR:
            return Status.GET_ACCOUNTS_ERROR
        accounts = ZoomDownloader.getFinalAccounts(zoomAccounts, fileAccounts)

        meetings = ZoomDownloader.getMeetingsUrls(accounts, dateFrom, dateTo, token)
        if meetings == Status.GET_MEETINGS_ERROR:
            return Status.GET_MEETINGS_ERROR

        isCorrect = ZoomDownloader.downloadAllMeeting(token, meetings)
        if False in isCorrect:
            return Status.DOWNLOAD_ERROR
        return Status.OK

    @staticmethod
    def uploadVideosToDisk(yandex_token: str, zoom_token: str, dateFrom: datetime.date, dateTo: datetime.date,
                           pathToFileWithAccounts: str) -> Status:

        zoomAccounts = ZoomDownloader.getUserAccountsFromZoom(zoom_token)
        fileAccounts = ZoomDownloader.getAccountsFromFile(pathToFileWithAccounts)
        if zoomAccounts == Status.GET_ACCOUNTS_ERROR or fileAccounts == Status.GET_ACCOUNTS_ERROR:
            return Status.GET_ACCOUNTS_ERROR
        accounts = ZoomDownloader.getFinalAccounts(zoomAccounts, fileAccounts)

        meetings = ZoomDownloader.getMeetingsUrls(accounts, dateFrom, dateTo, zoom_token)
        if meetings == Status.GET_MEETINGS_ERROR:
            return Status.GET_MEETINGS_ERROR

        disk = YandexDiskUploader(token=yandex_token)
        uploadStatus = disk.UploadVideosByLinks(meetings)
        return uploadStatus
