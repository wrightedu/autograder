# A quick start at a smart grading program
import json
import re as re
from difflib import ndiff
from math import exp
from subprocess import Popen, PIPE
from time import sleep

import traceback
import logging

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
        
        # First, make sure that we have the same number of test cases from the grader and the student
        if len(self.graderOutputs) != len(self.studentOutputs):
            raise ValueError("Grader and Student must have the same number of test cases")

        # Fill in the arrays with empty values
        self.graderTokens = [None] * len(self.graderOutputs)
        self.studentTokens = [None] * len(self.studentOutputs)

        for i in range(len(self.graderOutputs)):
            self.graderTokens[i] = [None] * len(self.graderOutputs)
            self.studentTokens[i] = [None] * len(self.studentOutputs)

        # Generate all of the token vectors
        for i in range(len(self.graderOutputs)):
            for j in range(len(self.graderOutputs)):
                self.graderTokens[i][j] = self.getTokenVectorsByLine(self.graderOutputs[i], self.graderOutputs[j])
                self.studentTokens[i][j] = self.getTokenVectorsByLine(self.studentOutputs[i], self.studentOutputs[j])

    def getGrade(self, testCaseNum):
        if testCaseNum >= len(self.studentOutputs):
            raise IndexError("Test case number must be less than the number of test cases")
        
        totalError = 0

        for i in range(len(self.graderOutputs)):
            
            graderTokenVector = self.graderTokens[testCaseNum][i]
            studentTokenVector = self.studentTokens[testCaseNum][i]

            # TODO Better handling of mismatched token lengths
            # TODO Better handling of out-of-order/shuffled tokens

            if len(graderTokenVector) != len(studentTokenVector):
                totalError += self.tokenCountMismatchPenalty
            
            tokenCount = min(len(graderTokenVector), len(studentTokenVector))

            for j in range(tokenCount):

                # If the two tokens are of different type, nightmare bad
                # bad nightmare nightmare bad bad 
                if type(graderTokenVector[j]) != type(studentTokenVector[j]):
                    totalError += self.typeMismatchPenalty

                # If the grader and the student vectors are different, 
                #   also bad
                elif graderTokenVector[j] != studentTokenVector[j]:

                    # If they are floats, the penalty will be proportional to the
                    #   percentage difference between them
                    if isinstance(graderTokenVector[j], float):
                        if graderTokenVector[j] != 0:
                            totalError += self.numericMismatchPenalty * abs(
                                (graderTokenVector[j] - studentTokenVector[j]) / graderTokenVector[j])

                        else:
                            totalError += self.numericMismatchPenalty * abs(studentTokenVector[j])

                    # If they are strings, the penalty will be proportional to
                    #   the number of characters that are different
                    else:
                        charDiffs = list(ndiff(graderTokenVector[j], studentTokenVector[j]))
                        for diff in charDiffs:
                            if diff[0] in '+-':
                                totalError += self.characterMismatchPenalty

                
            # TODO I hopefully fixed things so that an error would never actually be thrown during grading
            # TODO If this is the case, the grading exception penalty can be removed

        totalError /= len(self.studentOutputs)

        return totalError

    def getFeedback(self, testCaseNum):
        
        if testCaseNum >= len(self.studentOutputs):
            raise IndexError("Test case number must be less than the number of test cases")
        
        feedback = []

        for i in range(len(self.graderOutputs)):
            
            graderTokenVector = self.graderTokens[testCaseNum][i]
            studentTokenVector = self.studentTokens[testCaseNum][i]

            # TODO Better handling of mismatched token lengths
            # TODO Better handling of out-of-order/shuffled tokens

            if len(graderTokenVector) != len(studentTokenVector):
                feedback.append(f"Expected {len(graderTokenVector)} tokens, got {len(studentTokenVector)}")
            
            tokenCount = min(len(graderTokenVector), len(studentTokenVector))

            for j in range(tokenCount):

                # If the two tokens are of different type, nightmare bad
                # bad nightmare nightmare bad bad 
                if type(graderTokenVector[j]) != type(studentTokenVector[j]):
                    if isinstance(graderTokenVector[j], str):
                        feedback.append(f"Expected a string, got a number")
                    else:
                        feedback.append(f"Expected a number, got a string")

                # If the grader and the student vectors are different, 
                #   also bad
                elif graderTokenVector[j] != studentTokenVector[j]:                   
                    feedback.append(f"Expected '{graderTokenVector[j]}', got '{studentTokenVector[j]}'")


        return list(set(feedback))

    def getTokenVectorsByLine(self, fromStr, toStr):
        tokens = []

        # In order for this to work right, both strings _must_ end in a new line
        # if len(fromStr) == 0:
        #     fromStr = '\n'
        # elif fromStr[-1] != '\n':
        #     fromStr += '\n'

        # if len(toStr) == 0:
        #     toStr = '\n'
        # elif toStr[-1] != '\n':
        #     toStr += '\n'

        fromStr += '\n'
        toStr += '\n'

        # Get a list of line by line differences
        # print([i + '\n' for i in fromStr.splitlines()])
        # print([i + '\n' for i in toStr.splitlines()], end='\n\n')
        diffs = ''.join(list(ndiff([i + '\n' for i in fromStr.splitlines()], [i + '\n' for i in toStr.splitlines()])))
        
        # print(diffs)
        # Get a set of lines 
        matchedLines = [(m.group(1), m.group(2), m.start(0)) for m in re.finditer(r'(?:^|\n)\- (.*)\n(?:\? .*\n)?\+ (.*)', diffs)]
        unmatchedLines = [(m.group(1), '''''', m.start(0)) for m in re.finditer(r'(?:^|\n)\- (.*)\n(\-|$)', diffs)]

        # print('matched', matchedLines)
        # print('unmatched', unmatchedLines)
        diffLines = matchedLines + unmatchedLines
        diffLines.sort(key=lambda x: x[2])


        # Get the difference tokens from each of the individual lines
        for line in diffLines:
            # print(line)
            newTokens = self.getTokenVector(line[0], line[1])
            # for t in newTokens:
            #     print(f'    {t}')
            tokens += newTokens

        # print('\n')
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

        alphaTokens = [{"start": m.start(0), "end": m.end(0), "type": "word", "diff": False} for m in filter(lambda x: x.group(0) != '.', re.finditer(r'[^\s\d]+', fromStr))] 
        numberTokens = [{"start": m.start(0), "end": m.end(0), "type": "number", "diff": False} for m in re.finditer(r'-?\d*\.?\d+', fromStr)]

        # Find the start and end of all blocks of whitespace if we aren't collapsing whitespace
        whitespaceTokens = [] if self.collapseWhitespace else \
            [{"start": m.start(0), "end": m.end(0), "type": "space", "diff": False}
             for m in re.finditer(r'\s+', fromStr)]

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

        # print (diffs)
        # stringA = ""
        # stringB = ""

        # for i in diffs:
        #     if i[0] == '-':
        #         stringA += i[-1]
        #     elif i[0] == '+':
        #         stringB += i[-1]
        #     else:
        #         while len(stringA) < len(stringB):
        #             stringA += 'V'
        #         while len(stringB) < len(stringA):
        #             stringB += '^'
        #         stringA += i[-1]
        #         stringB += i[-1]

        # for i in range(0,len(stringA), 100):
        #     print(stringA[i:min(len(stringA)-1,i+100)])
        #     print(stringB[i:min(len(stringB)-1,i+100)])
        #     print()

        charNum = firstDiff
        for i in range(len(diffs)):
            if diffs[i][0] == "-":
                for tokenNum in range(len(possibleTokens)):
                    if charNum in list(range(possibleTokens[tokenNum]["start"], possibleTokens[tokenNum]["end"])):
                        possibleTokens[tokenNum]["diff"] = True
                charNum += 1

            elif diffs[i][0] == '+':
                for tokenNum in range(len(possibleTokens)):
                    if charNum in list(range(possibleTokens[tokenNum]["start"], possibleTokens[tokenNum]["end"])):
                        possibleTokens[tokenNum]["diff"] = True
                    elif charNum - 1 in list(range(possibleTokens[tokenNum]["start"], possibleTokens[tokenNum]["end"])):
                        possibleTokens[tokenNum]['diff'] = True

            elif diffs[i][0] == " ":
                charNum += 1

        tokenVector = []
        tokenNum = 0
        tokenStr = ""

        while tokenNum < len(possibleTokens):
            token = possibleTokens[tokenNum]
            if token["diff"]:
                tokenStr = fromStr[token["start"]:token["end"]]
                if (token["type"] == "word" or token["type"] == "space") and tokenNum < len(possibleTokens) - 1:
                    tokenNum += 1
                    token = possibleTokens[tokenNum]
                    while tokenNum < len(possibleTokens) and ((token["type"] == "word" and token["diff"]) or token["type"] == "space"):
                        if self.collapseWhitespace:
                            tokenStr += " "
                        tokenStr += fromStr[token["start"]:token["end"]]
                        tokenNum += 1
                        if tokenNum < len(possibleTokens):
                            token = possibleTokens[tokenNum]

                    tokenVector.append(tokenStr)

                    if token["type"] == "number" and token["diff"]:
                        tokenVector.append(float(fromStr[token["start"]:token["end"]]))
                elif token["type"] == "number":
                    tokenVector.append(float(tokenStr))
                else:
                    tokenVector.append(tokenStr)
            tokenNum += 1

        return tokenVector