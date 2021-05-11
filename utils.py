import os
from os import path

import re as re
import subprocess
from tqdm import tqdm
from math import exp
from os.path import join
from shutil import copyfile

from binaryornot.check import is_binary

from pygments import highlight
from pygments.lexers import get_lexer_by_name
from pygments.formatters import TerminalTrueColorFormatter, Terminal256Formatter

from smartGrader import SmartGrader

FORCE_WINDOWS_RENDERING = False

CHECKMARK, XMARK = ('✔', '✘') if os.name != 'nt' and not FORCE_WINDOWS_RENDERING else ('A', 'X')

def compileMake():
    pass

def compile(projectDir, language='java'):
    """First searches for a makefile, if one is found, it is run
        If no make file is found, or you just want to compile without a make file. 
        If an interpreted and/or non-compiled language is being used, just copy
        the files from the src directory to the bin directory

    Arguments:
        projectDir {str} -- The path to the project that is to be compiled

    Keyword Arguments:
        language {str} -- The language that the code to be compiled is written in (default: {'java'})

    Returns:
        bool -- Whether or not the compilation was successful
    """

    if 'makefile' in [filename.lower() for filename in os.listdir(projectDir)]:
        print('\nAttempting to build with student makefile')
        makeResults = subprocess.run('make', capture_output=True, cwd=projectDir)
        if makeResults.returncode == 0:
            return True

        print("MAKEFILE FAILED\n")
        print(makeResults.stdout.decode('utf-8'))

    print('\nMake unsuccessful, attempting to build with internal compiler')

    fromDir, toDir =join(projectDir, 'src'), join(projectDir, 'bin')

    # For java, we can just call javac on every file that we find
    if language == 'java':
        for dirName, subdirList, fileList in os.walk(fromDir):
            for fname in fileList:
                if re.match(r'.*\.java$', fname):
                    compResults = subprocess.run(['javac', '-cp', fromDir, '-d', toDir, join(dirName, fname)])
                    if compResults.returncode != 0:
                        return False
        return True

    # No support for auto-compiling c and c++ files yet. Just have a makefile
    elif language in ['c', 'cpp', 'c++']:
        return False

    # For python or bash files, "compile" by copying the files
    elif language in ['python', 'bash', 'perl']:
        for dirName, subdirList, fileList in os.walk(fromDir):
            for fname in fileList:
                if path.splitext(fname)[1] in ['.py', '.sh', '.bash', '.pl', '']:
                    # Ignore any part of the directory name that is part of fromDir
                    shortDirName = dirName[len(path.commonpath(fromDir, dirName)):]
                    copyfile(join(dirName, fname), join(toDir, shortDirName, fname))

        return True

    # If the specified language is unsupported, compilation fails
    return False


def generateOutputs(projectDir, programPath, testCases, language='java', timeout=5, noBin=False, args=(), progressMark=None):
    """Runs a set of test cases on a program and returns the result

    Arguments:
        projectDir {str,path} -- The directory containing the project
        programPath {str,path} -- The name and path to the program relative to the projects bin directory
        testCases {dict} -- A dictionary containing all of the test cases to run 

    Keyword Arguments:
        language {str} -- The language that the program being tested is written in (default: {'java'})
        timeout {int} -- The maximum amount of time to wait for the program to finish after closing stdin (default: {5})
        noBin {bool} -- Whether or not the compiled code for the project is stored in a bin directory (default: {False})
        args {iterable} -- A list of arguments to pass to the program (default: {()})

    Returns:
        list -- A list containing all of the test case results
    """

    # If the language is java, remove the .class value and execute with the JRE
    if language == 'java':
        if programPath[-6:] == '.class':
            programPath = programPath[:-6]

        if noBin:
            command = ('java', programPath) + tuple(args)
        else:
            command = ('java', '-cp', 'bin', programPath) + tuple(args)

    # If the language is python, execute with the python interpreter
    elif language == 'python':
        if noBin:
            command = ('python', programPath) + tuple(args)
        else:
            command = ('python', path.join('bin', programPath)) + tuple(args)

    else:
        return []

    outputs = []

    # Run the program for each of the test cases and get the results
    for test in tqdm(testCases):
        processPipe = subprocess.Popen(command, stdin=subprocess.PIPE, stdout=subprocess.PIPE, cwd=projectDir)

        processPipe.stdin.write(test["input"].encode("utf-8"))

        processPipe.stdin.close()

        if processPipe.wait(timeout) is None:
            processPipe.terminate()

        testResult = processPipe.stdout.read().decode('utf-8')
        exitCode = processPipe.returncode
        outputs.append((testResult, exitCode))

    return outputs

# TODO Have this actually convert ansi to some windows formatting stuff maybe?
def printFormattedText(text, end='\n'):
    """Used to print ANSI formatted text in a cross-platform way
        Basically, this strips all ANSI formatting if the program is being run
        on Windows, because windows doesn't really like ANSI by default


    Arguments:
        text {str} -- The text to print

    Keyword Arguments:
        end {str} -- The text to print at the end of the print, like 'end' for print (default: {'\n'})
    """
    if os.name == 'nt' or FORCE_WINDOWS_RENDERING:
        print(re.sub(r'\033\[.*?m', '', text), end=end)
    else:
        print(text, end=end)
        

def printTree(rootDir, recursionLevel=0, indent='│   ', dir_branch='├───┐', file_branch='├── '):
    """Recursively prints the file tree of a given directory

    Arguments:
        rootDir {str,Path} -- The path of the directory to print out

    Keyword Arguments:
        recursionLevel {int} -- The recursion depth. To be used internally (default: {0})
    """
    
    
    # Prints this directory name 
    if recursionLevel == 0:
        print(f'┌ \033[1m{path.basename(rootDir)}\033[0m')
    else:
        print(f'{(recursionLevel - 1) * indent}{dir_branch}\033[1m{path.basename(rootDir)}\033[0m')

    # Iterate over every file and sub directory, printing file names
    #   and recursing into sub-directories
    for file in os.listdir(rootDir):
        if path.isdir(join(rootDir, file)):
            printTree(join(rootDir, file), recursionLevel=recursionLevel + 1)
        else:
            printFormattedText(f'{recursionLevel * indent}{file_branch}\033[3m{file}\033[0m')


def printSourceFiles(rootDir, language='java'):
    """Recursively finds and prints all the supported source files in a given directory

    Arguments:
        rootDir {str,Path} -- The directory to search for search files in

    Keyword Arguments:
        language {str} -- The language to give syntax highlighting for (default: {'java'})
    """

    for file in os.listdir(rootDir):
        if path.isdir(join(rootDir, file)):
            printSourceFiles(join(rootDir, file), language=language)

        # TODO Better handling of language selection for syntax highlighting
        elif path.splitext(file)[1] in ['.java', '.py', '.c', '.cpp', '.sh', '.bash']:
            printFormattedText(f'\033[1;4m{join(rootDir, file)}\033[0m')

            # Open the file and print it with purty colors
            # But not on windows. Windows doesn't like colors
            with open(join(rootDir, file)) as f:
                text = f.read()
                text = text.replace('\t', '    ')
                lexer = get_lexer_by_name(language, stripall=True)
                formatter = TerminalTrueColorFormatter(style='fruity')
                printFormattedText(highlight(text, lexer, formatter))


def gradeStudentProgram(studentDirectory, graderOutputs, configs, language, catSource):
    # Print student directory contents
    if catSource:
        printSourceFiles(studentDirectory, language=language)


    printFormattedText('\033[1;4mProject Directory Listing\033[0m')
    printTree(studentDirectory)

    # Check to see if you want to continue grading
    continueGrading = input('\nContinue grading? [Y/n] ')
    if 'n' in continueGrading.lower():
        print('Exiting')
        exit(0) 
    
    # Check for makefile
    compilationSuccessful = compile(studentDirectory, language=language)
    # If we can't build with the student-supplied makefile and we can't build with our methods, exit because it's broken code
    if not compilationSuccessful:
        print('INTERNAL BUILD FAILED, EXITING')
        if language in ['c', 'cpp', 'c++']:
            print('Note, it is very difficult to automatically build C/C++. Makefiles are strongly recommended for C/C++\n')
        exit(1)
    else:
        print('Build successful\n')
    
    sg = SmartGrader(configs["settings"])

    # Figure out which of the student's programs to run
    print('Running test cases', end='', flush=True)
    studentPrograms = []

    for dirName, _, fileList in os.walk(studentDirectory):
        for fname in fileList:
            program = join(dirName, fname)
            if 'bin' + os.sep in program:
                program = program[program.find('bin' + os.sep) + 4:]
                studentPrograms.append(program)
    studentProgramPath = studentPrograms[0]
    if len(studentPrograms) > 1:
        for i, program in enumerate(studentPrograms):
            print(i + 1, program)
        selection = input("Which program would you like to run? (enter number) ").strip()
        studentProgramPath = studentPrograms[int(float(selection)) - 1]

    # Get student outputs
    studentOutputs = generateOutputs(studentDirectory, studentProgramPath, configs["tests"], progressMark='.')
    
    sg.graderOutputs = graderOutputs
    sg.studentOutputs = studentOutputs
    sg.analyze()

    print("Done\n\n\n")

    return sg


def printTestResults(sg, testCases, studentName=""):
    totalGrade = 0
    testsPassed = 0

    if len(studentName) > 0:
        studentName = " for " + studentName

    printFormattedText(f'\n\033[1;4mTest Case Results{studentName}\033[0m\n')
    for i, test in enumerate(testCases):
        grade = sg.getGrade(i)

        totalGrade += grade

        if grade == 100:
            printFormattedText(f'\033[32;1m{CHECKMARK}\033[0m ({i}) {test["description"]}:')
            testsPassed += 1
            printFormattedText (f'\033[2;3m{grade:-3.0f}%\033[0m')
        elif grade >= sg.passThreshold:
            printFormattedText(f'\033[32;1m{CHECKMARK}\033[0m ({i}) {test["description"]}:')
            testsPassed += 1
            printFormattedText (f'\033[2;3m{min(grade, 99):-3.0f}%\033[0m', end='')
            feedback = sg.getFeedback(i)
            firstFeedback = True
            for f in feedback:
                print(f'    {f}' if firstFeedback else f'        {f}')
                firstFeedback = False
        else:
            printFormattedText(f'\033[31;1m{XMARK}\033[0m ({i}) {test["description"]}:')
            printFormattedText (f'\033[2;3m{min(grade, 99):-3.0f}%\033[0m', end='')
            feedback = sg.getFeedback(i)
            firstFeedback = True
            for f in feedback:
                print(f'    {f}' if firstFeedback else f'        {f}')
                firstFeedback = False
        print()

    averageGrade = totalGrade / len(testCases)

    printFormattedText(f'\033[1mTests Passed: [{testsPassed}/{len(testCases)}]')
    printFormattedText(f'Overall Grade: {averageGrade:.02f}%\033[0m\n')

def printTestOutputsWithDifferencesHighlightedInPrettyColorsAndBoldTextUnlessIfYoureOnWindowsBecauseWindowsIsBadAndDoesntLikePrettyThings(sg, testCases):
    for i, test in enumerate(testCases):
        if sg.getGrade(i) < sg.passThreshold:
            printFormattedText(f'\n\033[1m{test["description"]}:\033[0m\n')

            testCasePassed = [output[1] == 0 for output in sg.studentOutputs]
            graderTokens, studentTokens = sg.getCombinedVectors(i, testCasePassed)

            lastTokenEnd = 0

            for tokenNum, token in enumerate(studentTokens):
                graderToken = graderTokens[min(tokenNum, len(graderTokens) - 1)]

                graderStr = sg.graderOutputs[i][0][graderToken.start:graderToken.end]
                studentStr = sg.studentOutputs[i][0][token.start:token.end]

                colorCode = '32' if graderStr == studentStr else '31'

                print(sg.studentOutputs[i][0][lastTokenEnd:token.start], end='')
                printFormattedText(f'\033[1;{colorCode}m{studentStr}\033[0m', end='')

                if graderStr != studentStr:
                    printFormattedText(f'\033[2;3m[{graderStr}]\033[0m', end='')

                lastTokenEnd = token.end

            print(sg.studentOutputs[i][0][lastTokenEnd:])

def printTable(studentGrades, testCases):
    # Get the length of the longest student's name
    longestName = max([len(g[0]) for g in studentGrades] + [4])
    maxStudentNumLength = len(f'(#{len(studentGrades)-1})')

    longestTestCase = max(len(f"Test {len(testCases) - 1}"), len(f'100% {CHECKMARK}'))

    printFormattedText(f'\033[1;4m {"NAME".rjust(int((longestName + maxStudentNumLength + 1) / 2 + len("NAME") / 2)):{longestName + maxStudentNumLength + 1}}', end=' ')

    for i in range(len(testCases)):
        print(f' {f"TEST {i}".rjust(int(longestTestCase / 2 + len(f"TEST {i}") / 2)):{longestTestCase}}', end=' ')

    printFormattedText(' OVERALL GRADE \033[0m')

    for i, (studentName, sg) in enumerate(studentGrades):
        printFormattedText(f'{studentName:{longestName}} \033[2m{f"(#{i})":{maxStudentNumLength}}\033[0m ', end=' ')
        
        totalGrade = 0

        for i in range(len(testCases)):
            grade = sg.getGrade(i)

            totalGrade += grade
            if grade < sg.passThreshold:
                grade = min(grade, 99)
            
            passFailMark = f'\033[32;1m{CHECKMARK}\033[0m' if grade >= sg.passThreshold else f'\033[31;1m{XMARK}\033[0m'

            printFormattedText(f' {f"{sg.getGrade(i):-3.0f}% {passFailMark}":{longestTestCase}}', end=' ')

        totalGrade /= len(testCases)
        if totalGrade < sg.passThreshold:
                totalGrade = min(totalGrade, 99)

        finalFeedback = f"    {totalGrade:-3.0f}% {passFailMark}"

        printFormattedText(f' \033[1m{finalFeedback}\033[0m')