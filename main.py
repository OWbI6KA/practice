import eel

eel.init("web")


@eel.expose
def recv_data(key, folderWay):
    print(key, folderWay)


eel.start('main.html', size=(800, 800))
