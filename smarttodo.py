import json
import datetime
import importlib
from calendargaps import *

#Importance Parameters
a = 0.5
b = 0.3
c = 0.2

#Input Variables
prio = 0
workhours = 0
diff = 0

#Other Setup
tasklist = []
workingTaskList = []
week = []
exittasks = 'n'
overflow = False
eachDayTotal = 0
weeklyOverage = 0

#Error Handling
def inputRatingInRange(message,low,high):
    while True:
        try:
            x = int(input(message))
            if x < low or x > high:
                raise TypeError
            break
        except (TypeError, ValueError):
            print("\nInvalid input. Please try again.")
            print("----------------")
    return x

#JSON THINGS
def tasksToDict():
    listofdics = [item.__dict__ for item in tasklist]
    for dic in listofdics:
        dic['day'] = dic['day'].__dict__
    return listofdics
def tasksToJSON():
    with open('listoftasks.json', mode='w') as file:
        json.dump(tasksToDict(), file, indent=4)
def daysToJSON():
    with open('listofdays.json', mode='w') as file:
        json.dump([i.__dict__ for i in week], file, indent=4)

# Class Setup
class task:
    def __init__(self, name, prio, workhours, diff):
        self.name = name
        self.prio = int(prio)
        self.workhours = int(workhours)
        self.diff = int(diff)
        self.day = 0
        #This is the equation determining the importance based on the input parameters. Subject to change.
        self.importanceIndex = ((a*prio) + ((workhours-2)**2 + 1)*b + ((4/9*(diff-4)**2) + 1)*c)*20
        self.isAssigned = False
        self.overage = 0

    def printsummary(self):
        print(" ----------------","\n",
        self.name,"\n",
        "Priority:", self.prio,"\n",
        "Difficulty:", self.diff,"\n",
        "Duration:", self.workhours,"\n",
        "Importance:",round(self.importanceIndex,1),"%","\n",
        "Will be done on:", self.day.dayname())
        if self.overage > 0:
            print("   *"+str(self.overage), "hours over*\n")

class Day:
    #Need to implement actual datetime stuff in here lol
    def __init__(self, dotw, workhours):
        self.dotw = int(dotw)
        self.workhours = int(workhours)

    #Change this disgusting fucking bullshit ugh
    def dayname(self):
        if self.dotw == 0: return("Monday")
        elif self.dotw == 1: return("Tuesday")
        elif self.dotw == 2: return("Wednesday")
        elif self.dotw == 3: return("Thursday")
        elif self.dotw == 4: return("Friday")
        elif self.dotw == 5: return("Saturday")
        elif self.dotw == 6: return("Sunday")
        else: return("No Day")

#Adding a New Task
def newTask():
    name = input("\nTask Name: ")
    newPrio = inputRatingInRange("Priority (1-5): ",1,5)
    newDiff = inputRatingInRange("Difficulty (1-5): ",1,5)
    newworkhours = inputRatingInRange("Duration (1-5 hours): ",1,5)
    addedTask = task(name, newPrio, newworkhours, newDiff)
    tasklist.append(addedTask)

#--MAIN FLOW OF THE PROGRAM--#

#How to parse JSON from dict into my classes???

#Create new tasks
if tasklist == []:
    while exittasks == 'n':
        newTask()
        exittasks = input("Exit task entry stage? (y/n): ")

#Create new days
#This will get removed once calendargaps.py is integrated
if week == []:
    print("\n\n----------------")
    n = 0
    while n < 7:
        newDayHours = inputRatingInRange("How many work-hours are available on "+Day(n,0).dayname()+"? ",0,16)
        newDay = Day(n,newDayHours)
        week.append(newDay)
        n += 1

#Sort entries by Importance and slot them into available work-hours
tasklist.sort(key=lambda x: x.importanceIndex, reverse=True)
totalWorkHours = sum([i.workhours for i in week])
if sum([i.workhours for i in tasklist]) > sum([i.workhours for i in week]):
    print("Shit too damn big bruh\n")
    overflow = True #deal with this later
else:
    #Start fitting tasks in days:
    #List of tasks not yet assigned
    for eachDay in week:
        workingTaskList = [i for i in tasklist if not(i.isAssigned)]
        if workingTaskList == []:
            break
        eachDayTotal += eachDay.workhours
        for item in workingTaskList:
            item.day = eachDay
            eachDayTotal -= item.workhours
            item.isAssigned = True
            if eachDayTotal <= 0:
                if eachDayTotal < 0:
                    item.overage -= eachDayTotal
                break
    #Print all entries
    for i in tasklist:
        i.printsummary()
    tasksToJSON()
    for i in range(7):
        findGaps(theday+datetime.timedelta(days=i))
