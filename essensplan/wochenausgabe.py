from datetime import date
from datetime import time
from datetime import datetime
from datetime import timedelta

# Monday = 0
# Tuesday = 1
# Wednesday = 2
# Thursday = 3
# Friday = 4
# Saturday = 5
# Sunday = 6

def getMonday ():
    today = date.today().weekday()
    dateMonday = date.today()-timedelta(days=today)
    return dateMonday

def main():
    print(getMonday())


if __name__ == "__main__":
    main()