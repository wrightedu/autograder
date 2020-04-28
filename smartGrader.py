# A quick start at a smart grading program
import json
import re as re
from difflib import ndiff
from math import exp
from subprocess import Popen , PIPE
from time import sleep

import traceback
import logging

testCasesPath = "samplePrograms/testCases/tests.json"
command = "java"

classPath = "samplePrograms"
graderClassPath = "samplePrograms"

outputDir = "outputs"

graderProgram = "MasterGrader"
studentProgram = "Student01"

# Penalties to apply to mismatches
TYPE_MISMATCH_PENALTY = 20
KEY_NUM_MISMATCH_PENALTY = 50
CHAR_MISMATCH_PENALTY = 5
NUMERIC_MISMATCH_PENALTY = 10
EXCEPTION_PENALTY = 100

# Grade scale. The smaller the more leniant the grades will be
PENALTY_SCALING = 0.001

def genOutput(programName, testNumber, testDescription, testInput, command, timeout=10):
    inputPipe = Popen(["cat",  "-"], stdin=PIPE, stdout=PIPE)
    processPipe = Popen(command, stdin=inputPipe.stdout, stdout=PIPE)
    
    for line in testInput:
        inputPipe.stdin.write(line.encode("utf-8"))

    inputPipe.stdin.close()

    if processPipe.wait(timeout) is None:
        processPipe.terminate()
        
    testResult = processPipe.stdout.read()
    return testResult

def smartDiff(a, b):
    """[summary]

    Arguments:
        a {[type]} -- The known good output
        b {[type]} -- The student's output
    """

    # SmartDiff will only work if the vectors are the same length
    if len(a) != len(b):
        print("Something broke")

    # Create matrices to hold the difference vector for each test case
    aDiffs = [None] * len(a) 
    bDiffs = [None] * len(a)
    numericDiffs = [None] * len(a)

    for i in range(len(a)):
        aDiffs[i] = [None] * len(a)
        bDiffs[i] = [None] * len(a)
        numericDiffs[i] = [0] * len(a)

    # Generate all the difference vectors
    for i in range(len(a)):
        for j in range(len(a)):
            aDiffs[i][j] = getDiffVector(a[i], a[j])
            bDiffs[i][j] = getDiffVector(b[i], b[j])

    # Convert the floats to floats
    for i in range(len(a)):
        for j in range(len(a)):
            for k in range(len(aDiffs[i][j])):
                try: aDiffs[i][j][k] = float(aDiffs[i][j][k])
                except ValueError: pass

            for k in range(len(bDiffs[i][j])):
                try: bDiffs[i][j][k] = float(bDiffs[i][j][k])
                except ValueError: pass

    for i in range(len(a)):
        for j in range(len(a)):

            # Apply a penalty if the student had too many or too few "important" bits
            if len(bDiffs[i][j]) != len(aDiffs[i][j]):
                numericDiffs[i][j] += KEY_NUM_MISMATCH_PENALTY

            for k in range(min(len(aDiffs[i][j]), len(bDiffs[i][j]))):
                try:

                    # Apply a penalty if the student printed a string when a num was
                    #   expected or vice versa
                    if type(aDiffs[i][j][k]) != type(bDiffs[i][j][k]):
                        numericDiffs[i][j] += TYPE_MISMATCH_PENALTY 
                    
                    if aDiffs[i][j][k] != bDiffs[i][j][k]:

                        # Apply a penalty porportional to the percent difference between
                        #   the student's number and the teacher's number
                        if isinstance(aDiffs[i][j][k], float):
                            if aDiffs[i][j][k] != 0:
                                numericDiffs[i][j] += abs((aDiffs[i][j][k] - bDiffs[i][j][k]) / aDiffs[i][j][k]) * NUMERIC_MISMATCH_PENALTY
                            else:
                                numericDiffs[i][j] += bDiffs[i][j][k] * NUMERIC_MISMATCH_PENALTY
                        # Apply a penalty based on the number of changed characters
                        else:
                            charDiffs = list(ndiff(aDiffs[i][j][k], bDiffs[i][j][k]))
                            for diff in charDiffs:
                                if diff[0] != ' ':
                                    numericDiffs[i][j] += CHAR_MISMATCH_PENALTY
                except Exception as e:
                    print("Caught an exception while grading the student's submission")
                    print(e)
                    logging.error(traceback.format_exc())
                    numericDiffs[i][j] += EXCEPTION_PENALTY

    sumPenalties = 0

    for i in range(len(a)):
        for j in range(len(a)):
            sumPenalties += numericDiffs[i][j]

    return sumPenalties
    



def getDiffVector(strA, strB):
    """ Gets a vector containing the "smart differences" between two strings

    Arguments:
        strA {string} -- The vector to find the differences in
        strB {string} -- A base vector to compare to
    """

    # print(f"Comparing {strA} to {strB}")

    # Compute the differences between the two files
    diffs = list(ndiff(strA, strB))

    # print(diffs)

    # Compute the difference vector for the first file listed
    diffVect = []

    isNumRegex = re.compile(r'^-?\d*\.?\d*$')

    # So here's where things get fun. If the differeing characters are non-numeric,
    #   We want to just parse them into the vector. If the differing characters are
    #   numeric, however, we want to parse in the _entire_ number that the characters
    #   are part of.
    diffString = ''
    diffNumericPrefix = ''
    for i in range(len(diffs)):

        # print(diffs[i] + ' ', end='')
        # If this character was the same between the two strings
        if diffs[i][0] == ' ':

            # If the non-differeing character is a digit
            if diffs[i][-1].isdigit():
                # print("Got an unchanged number")

                # If there is no diff string yet, this could be a number starting
                #   before the difference was detected
                if len(diffString) == 0:
                    if len(diffString) != 0:
                        diffVect.append(diffString)
                    diffString = ''
                    diffNumericPrefix += diffs[i][-1]

                # Else, if there is already a difference string and that difference
                #   string is a number, extend the difference string
                elif isNumRegex.match(diffString):
                    diffString += diffs[i][-1]

                # In any other case, this is to be considered the end of the difference string
                else:
                    if len(diffString) != 0:
                        diffVect.append(diffString)
                    diffString = ''
                    diffNumericPrefix = diffs[i][-1]

            # If the non-differing character was a decimal point
            elif diffs[i][-1] == '.':
                # print("Got an unchanged .")
                # If there is no diff string yet, this could be the numeric... etc
                if len(diffString) == 0:
                    # TODO Add a zero if the numeric prefix is empty
                    # TODO slice off anything before a preexisting decimal point
                    diffNumericPrefix += '.'

                # Else if the difference string is numeric, this could be 
                #   the continuation of it
                elif isNumRegex.match(diffString) and '.' not in diffString:
                    diffString += '.'

                # In any other case, this is to be considered the end of the difference string
                else:
                    if len(diffString) != 0:
                        diffVect.append(diffString)
                    diffString = ''
                    diffNumericPrefix = '.'

            # IF the non-differeing chaxcradter was a minus sign
            elif diffs[i][-1] == '-':
                # print("Got an unchanged -")
                if len(diffString) != 0:
                    diffVect.append(diffString)
                diffString = ''
                diffNumericPrefix = '-'

            # Else, the non-differing character was completly non-numeric
            else:
                # print("Got an unchanged char")
                # Which means that this should be considered the end of the difference string
                if len(diffString) != 0:
                    diffVect.append(diffString)
                diffString = ''
                diffNumericPrefix = ''

        # If this character existed in string a but not string b
        elif diffs[i][0] == '-':
            # If this chacrater was a digit, it has to be handled specially
            if diffs[i][-1].isdigit():
                # print("Got a changed number")
                # If there is currently no difference string, the difference string will be
                #   initialized with this digit and whatever is in the numeric prefix
                if len(diffString) == 0:
                    diffString = diffNumericPrefix + diffs[i][-1]
                    diffNumericPrefix = ''

                # Else if the existing diff string is non-numeric, start a new diff string
                elif not isNumRegex.match(diffString):
                    if len(diffString) != 0:
                        diffVect.append(diffString)
                    diffString = diffs[i][-1]
                    diffNumericPrefix = ''

                # In any other case, just continue reading in the number
                else:
                    diffString += diffs[i][-1]

            # If this character was a decimal point, handle it specially too
            elif diffs[i][-1] == '.':
                # print("Got a changed .")
                # If the current diffString is empty and the numeric prefix doesn't 
                #   contain a '.' this could be the start of a number
                if len(diffString) == 0 and not '.' not in diffNumericPrefix:
                    diffString = diffNumericPrefix + '.'
                    diffNumericPrefix = ''
                
                # If the existing diff is a number with a decimal point already in it,
                #   this would mark the end of that number
                elif isNumRegex.match(diffString) and '.' not in diffString:
                    if len(diffString) != 0:
                        diffVect.append(diffString)
                    diffString = '.'
                    diffNumericPrefix = ''

                # In any other case, continue on with life as usual
                else:
                    diffString += '.'
        
            # If the new character is neither a number or a .
            else:
                # print("Got a changed char")
                # If there is nothing in the difference string yet, flush the number
                if len(diffString) == 0:
                    diffString += diffs[i][-1]
                    diffNumericPrefix = ''

                # If the difference string up until this point is a number, this is the 
                #   end of that number
                elif isNumRegex.match(diffString):
                    if len(diffString) != 0:
                        diffVect.append(diffString)
                    diffString = diffs[i][-1]
                    diffNumericPrefix = ''

                # in any other case, business as usual
                else :
                    diffString += diffs[i][-1]
        # else:
        #     print("Got a char to skip")

    # If there is any left over difference string that was never added, add it now
    if len(diffString) != 0:
        diffVect.append(diffString)

    # print(f"The result was {diffVect}\n\n\n")

    return diffVect

def computeGrade(raw):
    return 100 * exp(-PENALTY_SCALING * raw)

if __name__ == '__main__':
    with open(testCasesPath, 'r') as testCasesFile:
        testCases = json.loads(testCasesFile.read())

    print(testCases)

    for studentNum in range(1):
        graderOutputs = []
        studentOutputs = []

        studentProgram = f"Student{studentNum:02}"
        print(f"Grading student {studentNum}: ", end='', flush=True)
        i = 0
        for test in testCases["tests"]:
            # print(test["description"])

            graderOutputs.append(genOutput(graderProgram, i, test["description"], test["input"], ['java', '-classpath', classPath, graderProgram]).decode("utf-8"))
            studentOutputs.append(genOutput(studentProgram, i, test["description"], test["input"], ['java', '-classpath', classPath, studentProgram]).decode("utf-8"))

            i+=1

        # print(graderOutputs)
        # print(studentOutputs)
        #round()
        
        print(f" grade = {computeGrade(smartDiff(graderOutputs, studentOutputs)):2f}")
