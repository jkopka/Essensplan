from datetime import date
from datetime import time
from datetime import datetime
from datetime import timedelta


def getMonday(choosenDate):
    """ 
    getMonday() gibt das Datum des letzten Montag des gegebenen Datum zurück
    """
    choosenDate
    today = choosenDate.weekday()
    dateMonday = choosenDate-timedelta(days=today)
    return dateMonday
