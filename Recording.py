class Recording:
    def __init__(self, topic, url, accountName, fileType, startTime):
        self.url = url
        self.accountName = accountName
        self.fileType = fileType
        self.startTime = startTime
        self.topic = topic
