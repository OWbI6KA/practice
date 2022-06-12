import eel
from scripts import get_data
eel.init("web")


@eel.expose
def recv_data(key, folderWay, dataFrom, dataTo, file):
    myDataFrom, myDataTo = get_data(userDataFrom=dataFrom, userDataTo=dataTo)
    print(myDataFrom, myDataTo)
    print(file)


eel.start('main.html', size=(800, 900))
