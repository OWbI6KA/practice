def get_data(userDataFrom, userDataTo, strDataFrom='', strDataTo=''):
    dataFrom = userDataFrom.split('-')
    dataTo = userDataTo.split('-')
    dataFrom.reverse()
    dataTo.reverse()
    for i in range(3):
        strDataFrom += dataFrom[i] + '/'
        strDataTo += dataTo[i] + '/'
    return strDataFrom[:-1], strDataTo[:-1]
