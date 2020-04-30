# A quick start at a smart grading program
import json
import re as re
from difflib import ndiff
from math import exp
from subprocess import Popen, PIPE
from time import sleep

import traceback
import logging

testCasesPath = "samplePrograms/fahrenheitToCelsius/testCases/tests.json"
command = "java"

classPath = "samplePrograms/fahrenheitToCelsius"
graderClassPath = "samplePrograms/fahrenheitToCelsius"

outputDir = "outputs"

graderProgram = "MasterGrader"
studentProgram = "Student01"


class SmartGrader():
    """A class that uses difference token vectors to automatically determine how well the output
        from a given student submission matches the output from a master teacher program
    """

    def __init__(self, settings={}, graderOutputs=[], studentOutputs=[]):
        """ Creates a new SmartGrader object

        Keyword Arguments:
            settings {dict} -- A dictionary that stores the settings used by the SmartGrader
                                when determining grades (default: {{}})
            graderOutputs {list} -- An array containing the outputs of the grader program for a set of test cases
            studentOutputs {list} -- An array containing the outputs of the student program for a set of test cases
        """

        ###### Read in penalties from the setting ######
        # TODO Maybe make these defaults be globals or some-such?
        # TODO, also it might be better to write this up as a ternary operator or something. This is a big block
        # TODO      of code to just read in some settings
        if "typeMismatch" in settings["penalties"]:
            self.typeMismatchPenalty = settings["penalties"]["typeMismatch"]
        else:
            self.typeMismatchPenalty = 20

        if "tokenCountMismatch" in settings["tokenCountMismatch"]:
            self.tokenCountMismatchPenalty = settings["penalty"]["tokenCountMismatch"]
        else:
            self.tokenCountMismatch = 50

        if "numericMismatch" in settings["numericMismatch"]:
            self.numericMismatchPenalty = settings["penalty"]["numericMismatch"]
        else:
            self.numericMismatch = 10

        if "characterMismatch" in settings["characterMismatch"]:
            self.characterMismatchPenalty = settings["penalty"]["characterMismatch"]
        else:
            self.characterMismatch = 5

        if "gradingException" in settings["gradingException"]:
            self.gradingExceptionPenalty = settings["penalty"]["gradingException"]
        else:
            self.gradingException = 50

        if "runFailure" in settings["runFailure"]:
            self.runFailurePenalty = settings["penalty"]["runFailure"]
        else:
            self.runFailure = 100

        if "compileFailure" in settings["compileFailure"]:
            self.compileFailurePenalty = settings["penalty"]["compileFailure"]
        else:
            self.compileFailure = 100

        if "penaltyScale" in settings:
            self.penaltyScale = settings["penaltyScale"]
        else:
            self.penaltyScale = 0.001

        # More stuff from settings
        if "collapseWhitespace" in settings:
            self.collapseWhitespace = settings["collapseWhitespace"]
        else:
            self.collapseWhitespace = True

        ###### Store the output vectors ######
        self.graderOutputs = graderOutputs
        self.studentOutputs = studentOutputs

        ###### More variables that will be used later ######

        # These will be two square matrices of vectors
        self.graderTokens = None
        self.studentTokens = None

    def analyze(self):
        # TODO Implement this. It will generate the token vector matrices for both
        # TODO  the student and the grader
        raise NotImplementedError("Give me a minute on this one")

    def _getTokenVector(self, fromStr, toStr):
        """ Gets a smart token difference vector. Any words or numbers that change between
            the two strings will be included in the vector, with adjacent words that have all 
            been changed merged into a single string

        Arguments:
            fromStr {string} -- [description]
            toStr {string} -- [description]
        """

        # TODO Maybe add a way to force text that matches a certain regular
        # TODO   expression to be considered important?

        # I'm changing how this works slightly from the first few versions. Instead of
        #   going through character by character, it will first find word and number
        #   breaks within the string to generate a list of possible tokens, then go
        #   over the ranges specified by the beginning and end of the possible tokens
        #   to see if they contain an "important change." If they do contain an important
        #   change, it will mark that token. After all of the possible tokens have been
        #   checked, it will go over them and create the difference token string from the
        #   list of possible tokens, concatenating together any adjacent word tokens

        possibleTokens = []

        alphaTokens = [{"start": m.start(0), "end": m.end(0), "type": "word", "diff": False} for m in filter(lambda x: x.group(0) != '.', re.finditer(r'[^\s\d]+', fromStr))] 
        numberTokens = [{"start": m.start(0), "end": m.end(0), "type": "number", "diff": False} for m in re.finditer(r'-?\d*\.?\d+', fromStr)]

        # Find the start and end of all blocks of whitespace if we aren't collapsing whitespace
        whitespaceTokens = [] if self.collapseWhitespace else \
            [{"start": m.start(0), "end": m.end(0), "type": "space", "diff": False}
             for m in re.finditer(r'\s+', fromStr)]

        possibleTokens = alphaTokens + numberTokens + whitespaceTokens

        possibleTokens.sort(key=lambda x: x["start"])

        diffs = list(ndiff(fromStr, toStr))

        charNum = 0
        for i in range(len(diffs)):
            if diffs[i][0] == "-":
                for tokenNum in range(len(possibleTokens)):
                    if charNum in list(range(possibleTokens[tokenNum]["start"], possibleTokens[tokenNum]["end"])):
                        possibleTokens[tokenNum]["diff"] = True
                charNum += 1

            elif diffs[i][0] == " ":
                charNum += 1

        print(possibleTokens)
        for i in possibleTokens:
            if i["diff"]:
                print(fromStr[i["start"]:i["end"]])

        tokenVector = []
        tokenNum = 0
        tokenStr = ""

        while tokenNum < len(possibleTokens):
            token = possibleTokens[tokenNum]
            if token["diff"]:
                tokenStr = fromStr[token["start"]:token["end"]]
                if token["type"] == "word" or token["type"] == "space":
                    tokenNum += 1
                    token = possibleTokens[tokenNum]
                    while tokenNum < len(possibleTokens) and ((token["type"] == "word" and token["diff"]) or token["type"] == "space"):
                        if self.collapseWhitespace:
                            tokenStr += " "
                        tokenStr += fromStr[token["start"]:token["end"]]
                        tokenNum += 1
                        token = possibleTokens[tokenNum]

                    tokenVector.append(tokenStr)

                    if token["type"] == "number" and token["diff"]:
                        tokenVector.append(fromStr[token["start"]:token["end"]])
                else:
                    tokenVector.append(tokenStr)
            tokenNum += 1

        # TODO you now have a range of where tokens should begin and end


##############################################################################
######                      END SMART_GRADER CLASS                      ######
##############################################################################


# # Penalties to apply to mismatches
TYPE_MISMATCH_PENALTY = 20
# TODO: Provide a smart way of accounting for token vector length mismatches
KEY_NUM_MISMATCH_PENALTY = 50
CHAR_MISMATCH_PENALTY = 5
NUMERIC_MISMATCH_PENALTY = 10
EXCEPTION_PENALTY = 100
# Grade scale. The smaller the more leniant the grades will be
PENALTY_SCALING = 0.001

# TODO mark a flag if this run has a non zero exit code?


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
                try:
                    aDiffs[i][j][k] = float(aDiffs[i][j][k])
                except ValueError:
                    pass

            for k in range(len(bDiffs[i][j])):
                try:
                    bDiffs[i][j][k] = float(bDiffs[i][j][k])
                except ValueError:
                    pass

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
                                numericDiffs[i][j] += abs(
                                    (aDiffs[i][j][k] - bDiffs[i][j][k]) / aDiffs[i][j][k]) * NUMERIC_MISMATCH_PENALTY
                            else:
                                numericDiffs[i][j] += bDiffs[i][j][k] * \
                                    NUMERIC_MISMATCH_PENALTY
                        # Apply a penalty based on the number of changed characters
                        else:
                            charDiffs = list(
                                ndiff(aDiffs[i][j][k], bDiffs[i][j][k]))
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
                else:
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

    for studentNum in range(26):
        graderOutputs = []
        studentOutputs = []

        studentProgram = f"Student{studentNum:02}"
        print(f"Grading student {studentNum}: ", end='', flush=True)
        i = 0
        for test in testCases["tests"]:
            # print(test["description"])

            graderOutputs.append(genOutput(graderProgram, i, test["description"], test["input"], [
                                 'java', '-classpath', graderClassPath, graderProgram]).decode("utf-8"))
            studentOutputs.append(genOutput(studentProgram, i, test["description"], test["input"], [
                                  'java', '-classpath', classPath, studentProgram]).decode("utf-8"))

            i += 1

        # print(graderOutputs)
        # print(studentOutputs)
        # round()

        print(
            f" grade = {computeGrade(smartDiff(graderOutputs, studentOutputs)):2f}")
