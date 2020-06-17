import datetime
import pickle
import pytz
import os.path
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
#importlib.import_module('smarttodo')

# If modifying these scopes, delete the file token.pickle.
SCOPES = ['https://www.googleapis.com/auth/calendar']

# AUTHENTICATION
creds = None
# The file token.pickle stores the user's access and refresh tokens, and is
# created automatically when the authorization flow completes for the first
# time.
if os.path.exists('token.pickle'):
    with open('token.pickle', 'rb') as token:
        creds = pickle.load(token)
# If there are no (valid) credentials available, let the user log in.
if not creds or not creds.valid:
    if creds and creds.expired and creds.refresh_token:
        creds.refresh(Request())
    else:
        flow = InstalledAppFlow.from_client_secrets_file(
            'credentials.json', SCOPES)
        creds = flow.run_local_server(port=0)
    # Save the credentials for the next run
    with open('token.pickle', 'wb') as token:
        pickle.dump(creds, token)
service = build('calendar', 'v3', credentials=creds)

#MAIN PROGRAM
theday = datetime.datetime.now()
def inputStartDay():
    #Make this dumbass-proof
    year = int(input('Enter a year: '))
    month = int(input('Enter a month: '))
    day = int(input('Enter a day: '))
    theday = datetime.date(year, month, day)
    return theday

def findGaps(dayofinterest):
    #Sets a lower and upper bound to the freebusy query, in UTC-4:00
    #Need to implement support for all timezones
    minTime = str(dayofinterest.year).zfill(4)+"-"+str(dayofinterest.month).zfill(2)+"-"+str(dayofinterest.day).zfill(2)+"T08:00:00-04:00"
    maxTime = str(dayofinterest.year).zfill(4)+"-"+str(dayofinterest.month).zfill(2)+"-"+str(dayofinterest.day+1).zfill(2)+"T00:00:00-04:00"

    #The following 3 lines of code are intended to pull every calendar from the user's account and plug them into the freebusy query. However, I have yet to find a way to make this work.
    calListRaw = service.calendarList().list().execute()['items']
    allCalendars = [i['id'] for i in calListRaw]
    for n,i in enumerate(allCalendars): allCalendars[n] = [{i, 'id:'}]

    #Submit a freebusy request returning the start and eng times of each busy block in the selected calendars
    busyData = service.freebusy().query(body={
      "timeMin": minTime,
      "timeMax": maxTime,
      "timeZone": "America/Toronto",
      "items": [
        {'id': "uhe04pqg66fk9c5i1ugqvv0o4k@group.calendar.google.com"},
        {'id': "ula12aupl7deg22mmljpjoer2s@group.calendar.google.com"},
        {'id': "59ht6b3q3qd6koai4khljtfkh8@group.calendar.google.com"},
        {'id': "rueie6k2psp6rpqug2jfo78hls@group.calendar.google.com"},
        {'id': "bdfk2uvju0tqp8kfs6n3i2mcjk@group.calendar.google.com"},
        {'id': "ula12aupl7deg22mmljpjoer2s@group.calendar.google.com"},
        {'id': "llvfpkhqof9v105pboo3gffnlk@group.calendar.google.com"},
        {'id': "uhe04pqg66fk9c5i1ugqvv0o4k@group.calendar.google.com"},
        {'id': "qh3devimpahajsjq9naduocaq8@group.calendar.google.com"},
        {'id': "lo9smhg22qavshr702jkimpie4@group.calendar.google.com"},
        {'id': "k51ftbcir92i5c2v4lk32gjp7k@group.calendar.google.com"},
        {'id': "l2ktkjdt1kp9hmioalr5gr4ejs@group.calendar.google.com"},
        {'id': "18jva1@gmail.com"},
        {'id': "rrja7k4b4om8si852n39ol2n40@group.calendar.google.com"},
        {'id': "en.canadian#holiday@group.v.calendar.google.com"}]
    }).execute()['calendars']

    #The following code splits the start times and end times into their own respectively opposite lists (start times into endTimes list, and vice-versa), and sorts them together by date. Then, the lower bound is added to the start times and the upper bound to the end times. The items in each list are then parsed from RFC3339 format to standard python datetime. A dictionary is created to contain the start times as keys, and the timedelta between start and end as values.
    startTimes = []
    endTimes = []
    deltaDict = {}
    for i in busyData:
        for j in busyData[i]['busy']: startTimes.append(j['end'])
        for j in busyData[i]['busy']: endTimes.append(j['start'])
    zipTimes = sorted(zip(startTimes, endTimes))
    startTimes = [x[0] for x in zipTimes]
    endTimes = [x[1] for x in zipTimes]
    startTimes.insert(0,minTime)
    endTimes.append(maxTime)
    zipTimes = sorted(zip(startTimes, endTimes))
    for n,t in enumerate(zipTimes):
        startTimes[n] = datetime.datetime.strptime(t[0],'%Y-%m-%dT%H:%M:%S-04:00')
        endTimes[n] = datetime.datetime.strptime(t[1],'%Y-%m-%dT%H:%M:%S-04:00')
        deltaDict[startTimes[n]] = (endTimes[n]-startTimes[n])

    deltaDict = {i:deltaDict[i] for i in deltaDict if deltaDict[i] > datetime.timedelta(hours=0)}

    for i in deltaDict: print(i.strftime('%A'), deltaDict[i])
    print("----------------")

if __name__ == "__main__":
    for i in range(7):
        findGaps(theday+datetime.timedelta(days=i))
