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
 
#Adding a New Task
def newTask():
    name = input("\nTask Name: ")
    newPrio = inputRatingInRange("Priority (1-5): ",1,5)
    newDiff = inputRatingInRange("Difficulty (1-5): ",1,5)
    newworkhours = inputRatingInRange("Duration (1-5 hours): ",1,5)
    addedTask = Task(name, newPrio, newworkhours, newDiff)
    tasklist.append(addedTask)

#JSON THINGS
def tasksToDict():
    listofdics = [item.__dict__ for item in tasklist]
    for dic in listofdics:
        dic['day'] = dic['day'].__dict__
        dic['day']['date'] = str(dic['day']['date'])
        dic['day']['worklist'] = [str(i) for i in dic['day']['worklist']]
    return listofdics
def tasksToJSON():
    with open('listoftasks.json', mode='w') as file:
        json.dump(tasksToDict(), file, indent=4)

# Class Setup
class Task:
    def __init__(self, name, prio, workhours, diff):
        self.name = name
        self.prio = int(prio)
        self.workhours = datetime.timedelta(hours=workhours).seconds / 3600
        self.diff = int(diff)
        self.day = theday
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
        "Will be done on:", self.day.dayname)
        if self.overage > 0:
            print("   *"+str(self.overage), "hours over*\n")

class Day:
    #Need to implement actual datetime stuff in here lol
    def __init__(self, date, worklist):
        self.date = date
        self.worklist = worklist
        self.workhours = sumOfDeltas(worklist).seconds / 3600
        self.dayname = date.strftime('%A')

#--MAIN FLOW OF THE PROGRAM--#

#Parse JSON from dict into task class
with open('listoftasks.json', mode='r') as file:
    JSONtasks = json.load(file)
    if not JSONtasks:
        tasklist = []
tasklist = [Task(i['name'], i['prio'], i['workhours'], i['diff']) for i in JSONtasks]

#Create new tasks
createNewTasks = input('Create new tasks? (y/n): ')
if createNewTasks == 'y':
    while exittasks == 'n':
        newTask()
        exittasks = input("Exit task entry stage? (y/n): ")

#Create new days
#NEED TO FIX SUPPORT FOR CROSS-MONTH RANGES!!
if week == []:
    for i in range(2):
        week.append(Day(theday+datetime.timedelta(days=i+1), findGaps(theday+datetime.timedelta(days=i+1))))

#Sort entries by Importance and slot them into available work-hours
tasklist.sort(key=lambda x: x.importanceIndex, reverse=True)
totalWorkHours = sum([i.workhours for i in week])
if sum([i.workhours for i in tasklist]) > sum([i.workhours for i in week]):
    print("Shit too damn big bruh\n")
    overflow = True #deal with this later
else:
    #Start fitting tasks in days:
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
<<<<<<< HEAD
    tasksToJSON()
=======

    tasksToJSON() #doesn't work with datetime, need to find fix
>>>>>>> db86e87d41513d131a85d21b6e8a9a93ea1cf88f
