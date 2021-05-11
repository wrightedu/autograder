#!/usr/bin/env python

# A quick start at a smart grading program
import json
import re as re
from difflib import ndiff
from math import exp
from subprocess import Popen, PIPE
from time import sleep

import traceback
import logging

DEBUG = False
PRINT_COMBINED = False
PRINT_LINES = False
PRINT_OUTPUTS = False
PRINT_TOKENS = False

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

        if "tokenCountMismatch" in settings["penalties"]:
            self.tokenCountMismatchPenalty = settings["penalties"]["tokenCountMismatch"]
        else:
            self.tokenCountMismatch = 50

        if "numericMismatch" in settings["penalties"]:
            self.numericMismatchPenalty = settings["penalties"]["numericMismatch"]
        else:
            self.numericMismatch = 10

        if "characterMismatch" in settings["penalties"]:
            self.characterMismatchPenalty = settings["penalties"]["characterMismatch"]
        else:
            self.characterMismatch = 5

        if "runFailure" in settings["penalties"]:
            self.runFailurePenalty = settings["penalties"]["runFailure"]
        else:
            self.runFailure = 100

        if "compileFailure" in settings["penalties"]:
            self.compileFailurePenalty = settings["penalties"]["compileFailure"]
        else:
            self.compileFailure = 100

        # More stuff from settings
        if "penaltyWeight" in settings:
            self.penaltyWeight = settings["penaltyWeight"]
        else:
            self.penaltyWeight = 0.001

        if "passThreshold" in settings:
            self.passThreshold = settings["passThreshold"]
        else:
            self.passThreshold = 95

        if "collapseWhitespace" in settings:
            self.collapseWhitespace = settings["collapseWhitespace"]
        else:
            self.collapseWhitespace = True

        if "enforceFloatingPoint" in settings:
            self.gradeForIntFloat = settings["enforceFloatingPoint"]
        else:
            self.gradeForIntFloat = False

        if "unifiedDifferenceChecking" in settings:
            self.combineDifferences = settings["unifiedDifferenceChecking"]
        else:
            self.combineDifferences = True

        ###### Store the output vectors ######
        self.graderOutputs = graderOutputs
        self.studentOutputs = studentOutputs

        ###### More variables that will be used later ######

        # These will be two square matrices of vectors
        self.graderTokens = None
        self.studentTokens = None


    def convertPenaltyToGrade(self, penalty):
        """Uses an exponential decay to convert the student's accumulated penalty to a letter grade

        Arguments:
            penalty {float} -- The accumulated penalty

        Returns:
            float -- The grade associated with that penalty
        """
        return 100 * exp(-self.penaltyWeight * penalty)

    def analyze(self):
        """Performs a full grading analysis of the provided inputs and outputs

        Raises:
            ValueError: Raised if there are a different number of grader and student outputs
        """
        
        # First, make sure that we have the same number of test cases from the grader and the student
        if len(self.graderOutputs) != len(self.studentOutputs):
            raise ValueError("Grader and Student must have the same number of test cases")

        if DEBUG or PRINT_OUTPUTS:
            print('\n ----- GRADER OUTPUTS -----')
            for i in self.graderOutputs:
                print(i)
            print('\n ----- STUDENT OUTPUTS -----')
            for i in self.studentOutputs:
                print(i)
            print('\n\n')

        # Fill in the arrays with empty values
        self.graderTokens = [None] * len(self.graderOutputs)
        self.studentTokens = [None] * len(self.studentOutputs)

        for i in range(len(self.graderOutputs)):
            self.graderTokens[i] = [None] * len(self.graderOutputs)
            self.studentTokens[i] = [None] * len(self.studentOutputs)

        # Generate all of the token vectors
        for i in range(len(self.graderOutputs)):
            if DEBUG:
                print(f'\n\n\n ---------- TEST CASE {i} ----------\n\n')
            for j in range(len(self.graderOutputs)):
                self.graderTokens[i][j] = self.getTokenVectorsByLine(self.graderOutputs[i][0], self.graderOutputs[j][0])
                self.studentTokens[i][j] = self.getTokenVectorsByLine(self.studentOutputs[i][0], self.studentOutputs[j][0])

        if DEBUG or PRINT_TOKENS:
            print(' -------- GRADER TOKENS --------')
            for i in range(len(self.graderOutputs)):
                print(f'  Test case {i}')
                for j in range(len(self.graderOutputs)):
                    print('    [', end='')
                    for t in self.graderTokens[i][j]:
                        print(f'{str(t)}', end=', ')
                    print(']')

            print(' -------- STUDENT TOKENS --------')
            for i in range(len(self.graderOutputs)):
                print(f'  Test case {i}')
                for j in range(len(self.graderOutputs)):
                    print('    [', end='')
                    for t in self.studentTokens[i][j]:
                        print(f'{str(t)}', end=', ')
                    print(']')

            print('\n\n')

    def getCombinedVectors(self, testCaseNum, mask=None):
        combinedGraderVectors = []
        combinedStudentVectors = []

        for i, vect in enumerate(self.graderTokens[testCaseNum]):
            if mask is None or mask[i]:
                combinedGraderVectors += vect

        for i, vect in enumerate(self.studentTokens[testCaseNum]):
            if mask is None or mask[i]:
                combinedStudentVectors += vect

        combinedGraderVectors = list(set(combinedGraderVectors))
        combinedStudentVectors = list(set(combinedStudentVectors))

        combinedGraderVectors.sort(key=lambda x: x.start)
        combinedStudentVectors.sort(key=lambda x: x.start)

        if DEBUG or PRINT_COMBINED:
            for i in combinedGraderVectors:
                print(str(i), end=',')
            print()
            for i in combinedStudentVectors:
                print(str(i), end=',')
            print()

        return combinedGraderVectors, combinedStudentVectors

    def _gradeTokenVectors(self, graderTokenVector, studentTokenVector, testCaseNum, ignoreTokenCount=False, compareIndex=-1):
        totalError = 0
        feedback = []

        if self.studentOutputs[testCaseNum][1] != 0 and self.graderOutputs[testCaseNum][1] == 0:
            feedback.append("Student program encountered an unexpected runtime exception")
            totalError += self.runFailurePenalty

        if len(graderTokenVector) != len(studentTokenVector) and not ignoreTokenCount:
            totalError += self.tokenCountMismatchPenalty

            # Convert the token vector into easily readable strings
            graderVectorString = '['
            studentVectorString = '['

            for i in graderTokenVector:
                graderVectorString += '\''
                graderVectorString += str(i)
                graderVectorString += '\', '

            for i in studentTokenVector:
                studentVectorString += '\''
                studentVectorString += str(i)
                studentVectorString += '\', '

            if len(graderVectorString) > 1:
                graderVectorString = graderVectorString[0:-2]
            if len(studentVectorString) > 1:
                studentVectorString = studentVectorString[0:-2]

            graderVectorString += ']'
            studentVectorString +=']'

            if compareIndex != -1:
                feedback.append(f"When comparing to test case {compareIndex} expected {graderVectorString}, got {studentVectorString}")
            else:
                feedback.append(f"Expected {graderVectorString}, got {studentVectorString}")

        tokenCount = min(len(graderTokenVector), len(studentTokenVector))

        for i in range(tokenCount):

            graderVal = graderTokenVector[i].value
            studentVal = studentTokenVector[i].value

            # If the two tokens are of different type, nightmare bad
            # bad nightmare nightmare nightmare nightmare nightmare nightmare bad nightmare nightmare
            # nightmare nightmare nightmare nightmare nightmare bad nightmare nightmare nightmare
            # nightmare nightmare nightmare nightmare nightmare nightmare nightmare nightmare nightmare nightmare
            if type(graderVal) != type(studentVal):
                # Before supplying any feedback, check to make sure these weren't both numeric types
                if not (isinstance(graderVal, (float, int)) and isinstance(studentVal, (float, int)) and not self.gradeForIntFloat):
                    totalError += self.typeMismatchPenalty
                    feedback.append(f"Expected a {type(graderVal)} ({graderVal}), got a {type(studentVal)} ({studentVal})")

            # If the grader and the student vectors are different, 
            #   also bad
            elif graderVal != studentVal:

                feedback.append(f"Expected '{graderVal}', got '{studentVal}'")

                # If they are floats, the penalty will be proportional to the
                #   percentage difference between them
                if isinstance(graderVal, (float, int)):
                    if graderVal != 0:
                        totalError += self.numericMismatchPenalty * abs(
                            (graderVal - studentVal) / graderVal)

                    else:
                        totalError += self.numericMismatchPenalty * abs(studentVal)

                # If they are strings, the penalty will be proportional to
                #   the number of characters that are different
                else:
                    charDiffs = list(ndiff(graderVal, studentVal))
                    for diff in charDiffs:
                        if diff[0] in '+-':
                            totalError += self.characterMismatchPenalty

        return totalError, feedback

    def _getGradeIgnoringTokenCount(self, testCaseNum):
        """Internal function used to get a rough hack at which 
            solutions are "incorrect" before doing a full comparison
        """
        if testCaseNum >= len(self.studentOutputs):
            raise IndexError("Test case number must be less than the number of test cases")
        
        totalError = 0

        for i in range(len(self.graderOutputs)):
            
            graderTokenVector = self.graderTokens[testCaseNum][i]
            studentTokenVector = self.studentTokens[testCaseNum][i]
            
            error, _ = self._gradeTokenVectors(graderTokenVector, studentTokenVector, testCaseNum, True)
            totalError += error

        totalError /= len(self.studentOutputs)

        return self.convertPenaltyToGrade(totalError)

    def getGrade(self, testCaseNum):
        """ Gets the computed grade that the student received for a given test case

        Arguments:
            testCaseNum {int} -- The test case to get the grade for

        Raises:
            IndexError: Raised if the specified test case is larger than the number of test cases

        Returns:
            float -- The grade received for the specified test case
        """

        if testCaseNum >= len(self.studentOutputs):
            raise IndexError("Test case number must be less than the number of test cases")

        totalError = 0

        testCasePassed = []
        if not self.combineDifferences:
            # Get whether or not each of the individual test cases was passing
            for i in range(len(self.graderOutputs)):
                testCasePassed.append(self._getGradeIgnoringTokenCount(i) >= self.passThreshold)

            for i in range(len(self.graderOutputs)):

                graderTokenVector = self.graderTokens[testCaseNum][i]
                studentTokenVector = self.studentTokens[testCaseNum][i]

                error, _ = self._gradeTokenVectors(graderTokenVector, studentTokenVector, testCaseNum, not testCasePassed[i])
                totalError += error

            totalError /= len(self.studentOutputs)

        else:
            for i in self.studentOutputs:
                testCasePassed.append(i[1] == 0)
            graderTokenVector, studentTokenVector = self.getCombinedVectors(testCaseNum, testCasePassed)
            totalError, _ = self._gradeTokenVectors(graderTokenVector, studentTokenVector, testCaseNum, False)


        return self.convertPenaltyToGrade(totalError)

    def getFeedback(self, testCaseNum):
        """Gets some basic feedback on what the student got wrong for a certain test case

        Arguments:
            testCaseNum {int} -- The test case to get feedback for

        Raises:
            IndexError: Raised if the specified test case index is out of bounds

        Returns:
            list -- A list of strings containing the feedback
        """
        
        if testCaseNum >= len(self.studentOutputs):
            raise IndexError("Test case number must be less than the number of test cases")

        feedback = []

        testCasePassed = []
        if not self.combineDifferences:
            # Get whether or not each of the individual test cases was passing
            for i in range(len(self.graderOutputs)):
                testCasePassed.append(self._getGradeIgnoringTokenCount(i) >= self.passThreshold)

            for i in range(len(self.graderOutputs)):
                graderTokenVector = self.graderTokens[testCaseNum][i]
                studentTokenVector = self.studentTokens[testCaseNum][i]

                _, newFeedback = self._gradeTokenVectors(graderTokenVector, studentTokenVector, testCaseNum, not testCasePassed[i], i)
                feedback += newFeedback

        else:
            for i in self.studentOutputs:
                testCasePassed.append(i[1] == 0)
            graderTokenVector, studentTokenVector = self.getCombinedVectors(testCaseNum, testCasePassed)
            _, feedback = self._gradeTokenVectors(graderTokenVector, studentTokenVector, testCaseNum, False)

        feedback = list(set(feedback))
        feedback.sort()

        return feedback

    def getTokenVectorsByLine(self, fromStr, toStr):
        """A better way of getting difference tokens if the output contains more than one line

        Arguments:
            fromStr {str} -- The string to get the changes in
            toStr {str} -- The base string to compare fromStr to

        Returns:
            list -- A list containing all of the differences
        """
        tokens = []

        # Get a list of line by line differences
        diffs = ''.join(list(ndiff([i + '\n' for i in fromStr.splitlines()], [i + '\n' for i in toStr.splitlines()])))
        
        if DEBUG:
            print(diffs)

        # Get a set of lines 
        matchedLines = [(m.group(1), m.group(2), m.start(0)) for m in re.finditer(r'(?:^|\n)\- (.*)\n(?:\? .*\n)?\+ (.*)', diffs)]
        unmatchedLines = [(m.group(1), '''''', m.start(0)) for m in re.finditer(r'(?:^|\n)\- (.*)\n(\-|$)', diffs)]
        duplicateLines = [(m.group(1), m.group(1), m.start(0)) for m in re.finditer(r'(?:^|\n)  (.*)(?=\n|$)', diffs)]

        diffLines = matchedLines + unmatchedLines + duplicateLines
        diffLines.sort(key=lambda x: x[2])

        lineStart = 0

        # Get the difference tokens from each of the individual lines
        for line in diffLines:
            if DEBUG or PRINT_LINES:
                print(line)
            newTokens = self.getTokenVector(line[0], line[1]) if line[0] != line[1] else []
            if DEBUG:
                for t in newTokens:
                    print(f'    {t}')
            for token in newTokens:
                token.offset(lineStart)
                tokens.append(token)
            lineStart += len(line[0]) + 1

        if DEBUG:
            print('\n')
        return tokens

    def getTokenVector(self, fromStr, toStr):
        """ Gets a smart token difference vector. Any words or numbers that change between
            the two strings will be included in the vector, with adjacent words that have all 
            been changed merged into a single string

        Arguments:
            fromStr {string} -- The string to get the changes in
            toStr {string} -- The base string to be compared to
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

        alphaTokens = [{"start": m.start(0), "end": m.end(0), "type": "word", "diff": False} for m in filter(lambda x: x.group(0) != '.', re.finditer(r'([^\s\d-]|-(?!\d))+', fromStr))]
        numberTokens = [{"start": m.start(0), "end": m.end(0), "type": "number", "diff": False} for m in re.finditer(r'-?\d*\.?\d+', fromStr)]

        # Find the start and end of all blocks of whitespace if we aren't collapsing whitespace
        whitespaceTokens = [] if self.collapseWhitespace else [{"start": m.start(0), "end": m.end(0), "type": "space", "diff": False} for m in re.finditer(r'\s+', fromStr)]

        possibleTokens = alphaTokens + numberTokens + whitespaceTokens

        possibleTokens.sort(key=lambda x: x["start"])

        # Perform a "first pass" over the strings to remove any large chunk of text that might 
        # be the same between the two strings
        firstPassDiffs = list(ndiff(fromStr, toStr))

        firstDiff = 0

        for i, diff in enumerate(firstPassDiffs):
            if diff[0] != ' ':
                firstDiff = i
                break

        # We now know where the first difference occurs, but since we're interested in differences
        #   by token, we're mostly interested in where the token containing this first 
        #   difference starts
        for token in possibleTokens:
            if firstDiff in range(token["start"], token["end"]):
                firstDiff = token["start"]
                break


        diffs = list(ndiff(fromStr[firstDiff:], toStr[firstDiff:]))

        if DEBUG:
            print (diffs)
            stringA = ""
            stringB = ""

            for i in diffs:
                if i[0] == '-':
                    stringA += i[-1]
                elif i[0] == '+':
                    stringB += i[-1]
                else:
                    while len(stringA) < len(stringB):
                        stringA += 'V'
                    while len(stringB) < len(stringA):
                        stringB += '^'
                    stringA += i[-1]
                    stringB += i[-1]

            for i in range(0,len(stringA), 100):
                print(stringA[i:min(len(stringA)-1,i+100)])
                print(stringB[i:min(len(stringB)-1,i+100)])
                print()

        charNum = firstDiff
        for i in range(len(diffs)):
            if diffs[i][0] == "-":
                for possibleToken in possibleTokens:
                    if charNum in list(
                        range(possibleToken["start"], possibleToken["end"])
                    ):
                        possibleToken["diff"] = True
                charNum += 1

            elif diffs[i][0] == '+':
                for tokenNum, token in enumerate(possibleTokens):
                    if charNum in list(range(token["start"], token["end"])):
                        possibleTokens[tokenNum]["diff"] = True
                    elif charNum - 1 in list(range(token["start"], token["end"])):
                        # TODO This sometimes causes false positives (see issue #9)
                        # TODO This if statement will solve some of the issues, but not all of them
                        # TODO This should only cause issues when charNum and charNum - 1are in two different tokens
                        if charNum - 1 >= firstDiff:
                            possibleTokens[tokenNum]['diff'] = True

            elif diffs[i][0] == " ":
                charNum += 1

        tokenVector = []
        tokenNum = 0
        tokenStr = ""
        tokenStart = -1

        for i, token in enumerate(possibleTokens):
            nextToken = possibleTokens[i+1] if i+1 < len(possibleTokens) else {"start": -1, "end": -1, "type": None, "diff": False}

            if token["diff"]:
                if token["type"] == "number":
                    tokenStr = fromStr[token["start"]:token["end"]]
                    # If this was an integer, cast as integer before creating the new token
                    tokenVal = int(tokenStr) if tokenStr.count('.') == 0 else float(tokenStr)
                    # Create and append the new token
                    if self.numericMismatchPenalty != 0:
                        tokenVector.append(Token(tokenVal, token["start"], token["end"]))
                    tokenStr = ""

                else:
                    # If this is the start of a new token
                    if tokenStr == "":
                        tokenStart = token["start"]


                    tokenStr += fromStr[token["start"]:token["end"]]

                    # If this is the end of a token
                    if not nextToken["diff"] or nextToken["type"] == "number":
                        if self.characterMismatchPenalty != 0:
                            tokenVector.append(Token(tokenStr, tokenStart, token["end"]))
                        tokenStr = ''

                    # If we're collapsing whitespace, we have to add it manually
                    elif self.collapseWhitespace:
                        tokenStr += ' '

        return tokenVector

class Token:
    def __init__(self, value, start, end):
        self.value = value
        self.start = start
        self.end = end

    def offset(self, delta):
        self.start += delta
        self.end += delta
        return self

    def __str__(self):
        return f'{self.value}'

    def __hash__(self):
        return (self.value, self.start, self.end).__hash__()

    def __eq__(self, other):
        return (self.value, self.start, self.end).__eq__((other.value, other.start, other.end))

    def __cmp__(self, other):
        if self.start < other.start:
            return -1
        if self.start > other.start:
            return 1
        if self.end < other.end:
            return -1
        if self.end > other.end:
            return 1
        return 0