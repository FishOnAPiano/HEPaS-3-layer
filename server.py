from xmlrpc.server import SimpleXMLRPCServer
import sqlite3
conn = sqlite3.connect("studentMarks.db")

#Initialise server
server = SimpleXMLRPCServer(('localhost', 3000), logRequests = True)

testingMarkListTwelve = [("CS1", 45), ("CS1", 45), ("CS1", 90), ("CS2", 85), ("CS3", 95), ("CS4", 90), ("CS5", 80), ("CS6", 80), ("CS7", 45), ("CS7", 90), ("CS8", 85), ("CS9", 95)]
testingMarkListThirty = [("CS1", 45), ("CS1", 45), ("CS1", 90), ("CS2", 85), ("CS3", 95), ("CS4", 90), ("CS5", 80), ("CS6", 80), ("CS7", 45), ("CS7", 90), ("CS8", 85), ("CS9", 95), ("CS10", 12), ("CS10", 40), ("CS10", 65), ("CS11", 65), ("CS12", 66), ("CS13", 67), ("CS14", 68), ("CS15", 69), ("CS16", 70), ("CS17", 71), ("CS18", 72), ("CS19", 73), ("CS19", 74), ("CS20", 75), ("CS21", 76), ("CS22", 77), ("CS23", 78), ("CS24", 79)]
#Contains student information in format[[personID, lastName, email, [markList]]]
database = [
            #Six failures
            ["SixF", "Fails", "sixf@EOU", [("CS1", 30), ("CS1", 20), ("CS1", 55), ("CS2", 12), ("CS2", 30), ("CS2", 60), ("CS3", 10), ("CS3", 20), ("CS3", 51), ("CS4", 55), ("CS5", 70), ("CS6", 60)]],
            #Course Average >= 70
            ["BobD", "Dylan", "bobd@EOU", testingMarkListTwelve],
            #Course Average >= 65, Best eight average >= 80
            ["EightQ", "Qualified", "eightq@EOU", [("CS1", 45), ("CS1", 50), ("CS2", 49), ("CS2", 55), ("CS3", 70), ("CS4", 80), ("CS5", 90), ("CS6", 80), ("CS7", 95), ("CS8", 85), ("CS9", 50), ("CS10", 90)]],
            #Course average >= 60, Best eight average >= 80
            ["ChanceF", "Further", "chancef@EOU", [("CS1", 10), ("CS1", 50), ("CS2", 10), ("CS2", 55), ("CS3", 70), ("CS4", 80), ("CS5", 90), ("CS6", 80), ("CS7", 95), ("CS8", 85), ("CS9", 50), ("CS10", 90)]],
            #Course Average >= 60, Best eight average < 80
            ["RheaS", "Sess", "rheas@EOU", [("CS1", 45), ("CS1", 50), ("CS2", 49), ("CS2", 55), ("CS3", 70), ("CS4", 80), ("CS5", 90), ("CS6", 80), ("CS7", 80), ("CS8", 85), ("CS9", 49), ("CS10", 51)]],
            #Course average < 60
            ["NoC", "Chance", "noc@EOU", [("CS1", 10), ("CS1", 51), ("CS2", 10), ("CS2", 55), ("CS3", 55), ("CS4", 55), ("CS5", 55), ("CS6", 55), ("CS7", 55), ("CS8", 55), ("CS9", 50), ("CS10", 55)]],
            ]

#SERVER
def printMarks(unitMarkList):
    for unitMark in unitMarkList:  
        print(unitMark[0] + ": " + str(unitMark[1]))
#Returns the average mark from unitMarkList
def calculateCourseAverage(unitMarkList):
	markSum = 0;
	for unitMarkTuple in unitMarkList:
		markSum += unitMarkTuple[1]
	if len(unitMarkList) != 0:
		markAverage = markSum/len(unitMarkList)
	return markAverage

#Returns an average mark generated from the 8 highest scores in unitMarkList
def calculateBestEightAverage(unitMarkList):
#-1 indicates empty slot; can we assume marks are positive?
	bestEight = [-1, -1, -1, -1, -1, -1, -1, -1]
	for unitMarkTuple in unitMarkList:
		for pos in range(8):
			# if mark is greater than or equal to score at pos in bestEight, and less than or equal to the next score up (I.E. if score belongs in this position)
			if unitMarkTuple[1] >= bestEight[pos] and (pos == 7 or unitMarkTuple[1] <= bestEight[pos+1]):
				bestEight.pop(0)
				bestEight.insert(pos, unitMarkTuple[1])
				break
	markSum = 0
	for mark in bestEight:
		if mark != -1:
			markSum += mark
	markAverage = markSum/(8-bestEight.count(-1))
	return markAverage


#Returns the response string that matches how qualified for honors study a student with the provided dataset is
def evaluateQualification(personID, unitMarkList):
	courseAverage = calculateCourseAverage(unitMarkList)
	bestEightAverage = calculateBestEightAverage(unitMarkList)
	numFails = 0
	for unitMarkTuple in unitMarkList:
		if unitMarkTuple[1] < 50:
			numFails += 1
	if numFails >= 6:
		return str(personID) + ", " + str(courseAverage) + ", with 6 or more Fails! DOES NOT QUALIFY FOR HONORS STUDY!"
	elif courseAverage >= 70:
		return str(personID) + ", " + str(courseAverage) + ", QUALIFIED FOR HONOURS STUDY!"
	elif courseAverage >= 65 and bestEightAverage >= 80:
		return str(personID) + ", " + str(courseAverage) + ", QUALIFIED FOR HONOURS STUDY!"
	elif courseAverage >= 60 and bestEightAverage >= 80:
		return str(personID) + ", " + str(courseAverage) + ", " + str(bestEightAverage) + ", MAY HAVE GOOD CHANCE! Need further assessment!"
	elif courseAverage >= 60 and bestEightAverage < 80:
		return str(personID) + ", " + str(courseAverage) + ", " + str(bestEightAverage) + ", MAY HAVE A CHANCE! Must be carefully reassessed and get the coordinator's permission!"
	else:
		return str(personID) + ", " + str(courseAverage) + ", DOES NOT QUALIFY FOR HONORS STUDY!"


def EOUStudentEvaluation(personID, lastName, email):
    
    unitMarkList = conn.execute("SELECT marks.unitCode, marks.mark FROM student INNER JOIN marks ON student.personID = marks.personID WHERE student.personID = '" + personID + "' AND student.lastName = '" + lastName + "' AND student.email = '" + email + "'").fetchall()
    if len(unitMarkList) > 0:
        return(evaluateQualification(personID, unitMarkList))
    else:
        return "Verification details do not match recorded values for an EOU student"
        
        

#Register RPCable functions
server.register_function(evaluateQualification)
server.register_function(EOUStudentEvaluation)

try:
    print('Server running...')
    server.serve_forever()
except KeyboardInterrupt:
    print('Server closing')
		