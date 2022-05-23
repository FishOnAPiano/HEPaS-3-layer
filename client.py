from xmlrpc.client import ServerProxy

proxy = ServerProxy('http://localhost:3000')


#CLIENT
while True:
    EOUStudent = input("Are you an EOU Student? (y/n): ")
    if EOUStudent == "y" or EOUStudent == "n":
        break
    print("Invalid input")
if EOUStudent == "y":
    #Use recorded data
    personID = ""
    lastName = ""
    email = ""
    while True:
        print("Please enter personal details for verification")
        personID = input("Person ID: ")
        lastName = input("Last name: ")
        email = input("EOU email: ")
        valid = input("Are these details correct? (y/n)")
        if valid == "y":
            break
            
    #Server call
    print(proxy.EOUStudentEvaluation(personID, lastName, email))
else:
    #Enter new data
    personID = input("Please enter your Person ID: ")
    print("Please enter 12-30 unit codes and marks, and enter 'done' when complete")
    unitMarkList = []
    while True:
        unitCode = input("Unit code: ")
        if unitCode == "done":
            break
        markString = input("Mark: ")
        mark = -1
        try:
            mark = int(markString)
        except ValueError:
            pass
        
        numPasses = 0
        numFails = 0
        for unitMark in unitMarkList:
            if unitMark[0] == unitCode:
                if unitMark[1] >= 50:
                    numPasses += 1
                else:
                    numFails +=1
        if mark < 0 or mark > 100:
            #Catches non-number input as well, as if cannot be converted to number mark will still be -1
            print("Invalid mark, please enter a number between 0 and 100")
        elif not unitCode:
            print("Please enter a valid unit code")
        elif numPasses == 1 and mark >= 50:
            print(unitCode + " has already had a passing mark recorded, only one passing mark is allowed")
        elif numFails == 2 and mark < 50:
            print(unitCode + " already has two failing marks, only two failing marks are allowed")
        else:
            unitMarkList.append((unitCode, mark))
            if len(unitMarkList) == 30:
                print("Maximum of 30 marks reached, evaluating using provided marks")
                break                    
    if len(unitMarkList) >= 12:
        #Server call
        print(proxy.evaluateQualification(personID, unitMarkList))
    else:
        print("Insufficent marks entered, at least 12 are required")
