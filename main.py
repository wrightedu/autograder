import argparse
import json
import os
import select

from math import exp
from smartGrader import SmartGrader
from subprocess import Popen, PIPE
from time import sleep 

def convertPenaltyToGrade(penalty, weight):
    return 100 * exp(-weight * penalty)

def genOutput(testInput, command, timeout=10):
    inputPipe = Popen(["cat",  "-"], stdin=PIPE, stdout=PIPE)
    processPipe = Popen(command, stdin=inputPipe.stdout, stdout=PIPE)

    # TODO Maybe have a new line inserted after every print in?
    processPoll = select.poll()
    for line in testInput:
        inputPipe.stdin.write(line.encode("utf-8"))


    inputPipe.stdin.close()

    if processPipe.wait(timeout) is None:
        processPipe.terminate()

    testResult = processPipe.stdout.read().decode('utf-8')
    return testResult

if __name__ == '__main__':
    parser = argparse.ArgumentParser()

    parser.add_argument('-d', '--directory', nargs=1, default='samplePrograms', help='The directory that the assignments are stored in')
    parser.add_argument('-la', '--list-assignments', action='store_true', help="Gets a list of assignments directories")
    parser.add_argument('-a', '--assignment', nargs='?', help="The name of the example assignment to be graded")
    parser.add_argument('-s', '--students', nargs='+', type=int, help='The numbers of the students to be graded')
    parser.add_argument('-f', '--full', action='store_true', help='Gives full feedback on output (NOT YET IMPLEMENTED)')
    args = parser.parse_args()
    

    if args.list_assignments:
        assignments = list([x for x in os.listdir(args.directory) if os.path.isdir(os.path.join(args.directory, x))])
        print(assignments)
    else:

        # Load in the configuration file
        with open(os.path.join(args.directory, args.assignment, 'tests.json'), 'r') as testCasesFile:
            configs = json.loads(testCasesFile.read())
        
        penaltyWeight = configs['settings']['penaltyWeight']
        passThreshold = configs['settings']['passThreshold']

        sg = SmartGrader(configs["settings"])

        classpath = os.path.join(args.directory, args.assignment)

        print("Generating grader outputs... ", end='')
        graderOutputs = []            
        graderProgram = f'MasterGrader'
        for testCase in configs["tests"]:
            graderOutputs.append(genOutput(testCase["input"], ['java', '-classpath', classpath, graderProgram]))
        print("done\n")

        for i in args.students:
            print(f'Grading Student {i}:')

            studentOutputs = []
            studentProgram = f'Student{i:02}'

            for testCase in configs["tests"]:
                studentOutputs.append(genOutput(testCase["input"], ['java', '-classpath', classpath, studentProgram]))
            
            sg.graderOutputs = graderOutputs
            sg.studentOutputs = studentOutputs
            sg.analyze()

            totalGrade = 0
            testsPassed = 0

            for i in range(len(configs["tests"])):
                grade = convertPenaltyToGrade(sg.getGrade(i), penaltyWeight)

                totalGrade += grade

                print(f'    {configs["tests"][i]["description"]}: ', end='')
                if grade == 100:
                    testsPassed += 1
                    print (f'{grade:0.02f}% \033[32;1m✔\033[0m')
                elif grade >= passThreshold:
                    testsPassed += 1
                    print (f'{min(grade, 99.99):0.02f}% \033[32;1m✔\033[0m')
                    feedback = sg.getFeedback(i)
                    for f in feedback:
                        print(f'        {f}')
                else:
                    print (f'{min(grade, 99.99):0.02f}% \033[31;1m✘\033[0m')
                    feedback = sg.getFeedback(i)
                    for f in feedback:
                        print(f'        {f}')

            averageGrade = totalGrade / len(configs["tests"])

            print(f'    \033[1mTests Passed: [{testsPassed}/{len(configs["tests"])}]')
            print(f'    Overall Grade: {averageGrade:.02f}%\033[0m')
            print('')

        # testCasesPath = "samplePrograms/{/tests.json"
    
 