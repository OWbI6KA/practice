import os

import yadisk
import posixpath
import pandas as pd
from status import Status

class YandexDiskUploader:
    def __init__(self, token):
        self.disk = yadisk.YaDisk(token=token)
        self.confirmationFolders = dict()
        self.paths = dict()
        self.links = list()

    def getPathByString(self, string: str, startTime: str = None):
        words = string.split('_')
        path = 'disk:/'
        for i in range(len(words)-1):
            path = posixpath.join(path, words[i])
            if path not in self.confirmationFolders:
                try:
                    self.disk.mkdir(path)
                    self.confirmationFolders[path] = True
                except yadisk.exceptions.PathExistsError:
                    self.confirmationFolders[path] = True
                    continue
                except Exception as e:
                    print(f'path - {path}')
                    print(e)
                    return Status.PATH_CREATION_ERROR
        if startTime is not None:
            path = posixpath.join(path, f'{words[-1]} {startTime.replace(":", "-")}') + '.mp4'
        else:
            path = posixpath.join(path, f'{words[-1]}') + '.mp4'
        return path

    def UploadVideosByLinks(self, recordings: list) -> Status:
        if not self.disk.check_token():
            return Status.INCORRECT_TOKEN
        for recording in recordings:
            path = self.getPathByString(recording.topic, recording.startTime)
            if path != Status.PATH_CREATION_ERROR:
                try:
                    self.disk.upload_url(recording.url, path)
                    self.paths[recording.topic + " " + recording.startTime] = path
                except yadisk.exceptions.PathExistsError:
                    print(f'Path already exists - {path}')
                    continue
                except Exception as e:
                    print(e)
        print("Файлы загружены на диск")
        self.getLinks()
        self.ExcelAndCSVFileCreate()
        return Status.OK

    def UploadVideosFromFolder(self, folderName: str) -> Status:
        if not self.disk.check_token():
            return Status.INCORRECT_TOKEN
        for root, dirs, files in os.walk(folderName):
            p = root.split(folderName)[1].strip(os.path.sep)
            for file in files:
                file_path = self.getPathByString(file)
                p_sys = p.replace("/", os.path.sep)
                in_path = os.path.join(folderName, p_sys, file)
                if file_path != Status.PATH_CREATION_ERROR:
                    try:
                        self.disk.upload(in_path, file_path)
                        self.disk.publish(file_path)
                        self.links.append(file.split('_') + [self.disk.get_meta(file_path)['public_url']])
                    except yadisk.exceptions.PathExistsError:
                        print(f'Path already exists - {file_path}')
                        continue
                    except Exception as e:
                        print(e)
                        return Status.UPLOAD_ERROR
        print("Файлы загружены на диск")
        self.ExcelAndCSVFileCreate()
        return Status.OK

    def getLinks(self):
        count = 0
        while count < 1000 and len(self.paths) > 0:
            used = list()

            for key in self.paths:
                try:
                    self.disk.publish(self.paths[key])
                    self.links.append(key.split('_') + [self.disk.get_meta(self.paths[key])['public_url']])
                    used.append(key)
                except Exception as e:
                    continue

            for key in used:
                self.paths.pop(key, None)
            count += 1

    def ExcelAndCSVFileCreate(self):
        data = pd.DataFrame(self.links)
        try:
            data.to_excel("links.xls")
            print("Excel файл со ссылками создан")
        except Exception as e:
            print(e)
            print("Excel файл не был создан")

        try:
            data.to_csv("links.csv")
            print("CSV файл со ссылками создан")
        except Exception as e:
            print(e)
            print("CSV файл не был создан")
