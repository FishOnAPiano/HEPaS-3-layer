from xmlrpc.server import SimpleXMLRPCServer
import sqlite3

#Access database
conn = sqlite3.connect("studentMarks.db")

#Initialise server
server = SimpleXMLRPCServer(('localhost', 3000), logRequests = True)

#SERVER

#Prints the contents of the provided unitMarkList
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
    #-1 indicates empty slot as marks must be >= 0
	bestEight = [-1, -1, -1, -1, -1, -1, -1, -1]
	for unitMarkTuple in unitMarkList:
		for pos in range(8):
			# if mark is greater than or equal to score at pos in bestEight, and less than or equal to the next score up (Or there is no next score) then score belongs at position
			if unitMarkTuple[1] >= bestEight[pos] and (pos == 7 or unitMarkTuple[1] <= bestEight[pos+1]):
                #remove lowest score
				bestEight.pop(0)
                #Add in score at pos
				bestEight.insert(pos, unitMarkTuple[1])
				break
	markSum = 0
	for mark in bestEight:
		if mark != -1:
			markSum += mark
	markAverage = markSum/(8-bestEight.count(-1))
	return markAverage


#Returns the response string that matches how qualified for honors study a student with the provided dataset is
#Called remotely by user inputting their own marks, or called locally by EOUStudentEvaluation with data from the database
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

#Performs an evaluation using mark data from the database, returns evaluation or no matching record message if provided details do not match a recorded student
#Called remotely by user wanting an evaluation using data from database
def EOUStudentEvaluation(personID, lastName, email):
    unitMarkList = conn.execute("SELECT marks.unitCode, marks.mark FROM student INNER JOIN marks ON student.personID = marks.personID WHERE student.personID = '" + personID + "' AND student.lastName = '" + lastName + "' AND student.email = '" + email + "'").fetchall()
    if len(unitMarkList) > 0:
        return(evaluateQualification(personID, unitMarkList))
    else:
        return "Verification details do not match recorded values for an EOU student"
        
        

#Register Remote Proceure Callable functions
server.register_function(evaluateQualification)
server.register_function(EOUStudentEvaluation)

try:
    print('Server running...')
    server.serve_forever()
except KeyboardInterrupt:
    print('Server closing')
		
