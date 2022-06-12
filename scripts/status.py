from enum import Enum


class Status(Enum):
    OK = 0
    DATE_PARSE_ERROR = 1
    GET_ACCOUNTS_ERROR = 2
    GET_MEETINGS_ERROR = 3
    DOWNLOAD_ERROR = 4
    INCORRECT_TOKEN = 5
    PATH_CREATION_ERROR = 6
    UPLOAD_ERROR = 7