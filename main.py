import argparse
import json
import os

import re as re
import subprocess
from math import exp
from os.path import join
from shutil import copyfile

from binaryornot.check import is_binary as isBinary
from smartGrader import SmartGrader

from pygments import highlight
from pygments.lexers import get_lexer_by_name
from pygments.formatters import TerminalFormatter


def printFormattedText(text, end='\n'):
    """Used to print ansi formatted text in a cross-platform way
        Basically, this strips all ansi formatting if the program is being run
        on Windows, because windows doesn't really like ansi by default


    Arguments:
        text {str} -- The text to print

    Keyword Arguments:
        end {str} -- The text to print at the end of the print, like 'end' for print (default: {'\n'})
    """
    if os.name == 'nt':
        print(re.sub(r'\033\[.*?m', '', text), end=end)
    else:
        print(text, end=end)

def printTree(rootDir, recursionLevel=0):
    """Recursively prints the file tree of a given directory

    Arguments:
        rootDir {str,Path} -- The path of the directory to print out

    Keyword Arguments:
        recursionLevel {int} -- The recursion depth. To be used internally (default: {0})
    """

    # Prints this directory name 
    print(recursionLevel * '    ' + os.path.basename(rootDir) + os.sep)

    # Iterate over every file and sub directory, printing file names
    #   and recursing into sub-directories
    for file in os.listdir(rootDir):
        if os.path.isdir(join(rootDir, file)):
            printTree(join(rootDir, file), recursionLevel=recursionLevel + 1)
        else:
            print((recursionLevel + 1) * '    ' + file)

def printSourceFiles(rootDir, language='java'):
    """Recursively finds and prints all the supported source files in a given directory

    Arguments:
        rootDir {str,Path} -- The directory to search for search files in

    Keyword Arguments:
        language {str} -- The language to give syntax highlighting for (default: {'java'})
    """

    for file in os.listdir(rootDir):
        if os.path.isdir(join(rootDir, file)):
            printSourceFiles(join(rootDir, file), language=language)

        # TODO Better handling of language selection for syntax highlighting
        elif os.path.splitext(file)[1] in ['.java', '.py', '.c', '.cpp', '.sh', '.bash']:
            printFormattedText(f'\033[1;4m{join(rootDir, file)}\033[0m')

            # Open the file and print it with purty colors
            # But not on windows. Windows doesn't like colors
            with open(join(rootDir, file)) as f:
                text = f.read()
                text = text.replace('\t', '    ')
                lexer = get_lexer_by_name(language, stripall=True)
                formatter = TerminalFormatter(linenos=True)
                printFormattedText(highlight(text, lexer, formatter))
            print('\n\n\n')


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
        if makeResults.returncode != 0:
            print("STUDENT MAKEFILE FAILED\n")
            print(makeResults.stdout.decode('utf-8'))
        else:
            return True

    print('\nMake unsuccesful, attempting to build with internal compiler')

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
                if os.path.splitext(fname)[1] in ['.py', '.sh', '.bash', '.pl', '']:
                    # Ignore any part of the dir name that is part of fromdir
                    shortDirName = dirName[len(os.path.commonpath(fromDir, dirName)):]
                    copyfile(join(dirName, fname), join(toDir, shortDirName, fname))

    # If the specified language is unsupported, compilation fails
    return False

def generateOutputs(projectDir, programPath, testCases, language='java', timeout=5, noBin=False, args=()):
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
            command = ('python', os.path.join('bin', programPath)) + tuple(args)

    else:
        return []

    outputs = []

    # Run the program for each of the test cases and get the results
    for test in testCases:
        processPipe = subprocess.Popen(command, stdin=subprocess.PIPE, stdout=subprocess.PIPE, cwd=projectDir)

        processPipe.stdin.write(test["input"].encode("utf-8"))

        processPipe.stdin.close()

        if processPipe.wait(timeout) is None:
            processPipe.terminate()

        testResult = processPipe.stdout.read().decode('utf-8')
        exitCode = processPipe.returncode
        outputs.append((testResult, exitCode))

    return outputs

if __name__ == '__main__':
    # TODO: Add support for grading multiple students simultaneously
    parser = argparse.ArgumentParser()

    # Take a path to the configuration file
    parser.add_argument('-c', '--config', type=str, default=None, help='The relative filepath to the config.json you would like to use')
    
    # Take a path to the student's source directory
    parser.add_argument('-d', '--project-directory', type=str, default=None, help='The relative filepath to the project directory of the student code')

    # Flag to disable printing student directory stuff
    parser.add_argument('-n', '--no-cat', action='store_true', help='Disable catting student files')
    
    # Flag to select what language is being graded
    parser.add_argument('-l', '--language', type=str, default='java', choices=['java', 'c', 'c++', 'cpp', 'python', 'bash'], help='The language of the assignment being graded')
    
    args = parser.parse_args()

    # Print student directory contents
    if not args.no_cat:
        printSourceFiles(args.project_directory, language=args.language)


    printFormattedText('\033[1;4mProject Directory Listing\033[0m')
    printTree(args.project_directory)

    # Check to see if you want to continue grading
    continueGrading = input('\n\n\n\n\nContinue grading? [Y/n] ')
    if 'n' in continueGrading.lower():
        print('Exiting')
        exit(0)
    
    # Load in the configuration file
    with open(join(args.config), 'r') as testCasesFile:
        configs = json.loads(testCasesFile.read())

    sg = SmartGrader(configs["settings"])
    
    
    # Check for makefile
    compilationSuccessful = compile(args.project_directory, language=args.language)
    # If we can't build with the student-supplied makefile and we can't build with our methods, exit because it's broken code
    if not compilationSuccessful:
        print('INTERNAL BUILD FAILED, EXITING')
        if args.language in ['c', 'cpp', 'c++']:
            print('Note, it is very difficult to automatically build C/C++. Makefiles are strongly recommended for C/C++\n')
        exit(1)
    else:
        print('Build successful\n')
    
    # Figure out which of the student's programs to run
    print('Running test cases...\n')
    studentPrograms = []
    for dirName, subdirList, fileList in os.walk(args.project_directory):
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
    studentOutputs = generateOutputs(args.project_directory, studentProgramPath, configs["tests"])

    # Generate the grader outputs
    configDir = os.path.dirname(args.config)
    graderPath = join(configDir, configs["settings"]["graderProgram"])
    
    graderOutputs = generateOutputs(configDir, configs["settings"]["graderProgram"], configs['tests'], noBin=True)
    
    sg.graderOutputs = graderOutputs
    sg.studentOutputs = studentOutputs
    sg.analyze()
    
    # TODO Have it only grade certain test cases maybe? Add a flag?

    totalGrade = 0
    testsPassed = 0

    printFormattedText('\033[1;4mTest Case Results\033[0m\n')
    for i, test in enumerate(configs["tests"]):
        grade = sg.getGrade(i)

        totalGrade += grade

        if grade == 100:
            printFormattedText(f'\033[32;1m✔\033[0m ({i}) {test["description"]}:')
            testsPassed += 1
            printFormattedText (f'\033[2;3m{grade:-3.0f}%\033[0m')
            # TODO Maybe print out what the correct output was?
        elif grade >= sg.passThreshold:
            printFormattedText(f'\033[32;1m✔\033[0m ({i}) {test["description"]}:')
            testsPassed += 1
            printFormattedText (f'\033[2;3m{min(grade, 99):-3.0f}%\033[0m', end='')
            feedback = sg.getFeedback(i)
            firstFeedback = True
            for f in feedback:
                print(f'    {f}' if firstFeedback else f'        {f}')
                firstFeedback = False
        else:
            printFormattedText(f'\033[31;1m✘\033[0m ({i}) {test["description"]}:')
            printFormattedText (f'\033[2;3m{min(grade, 99):-3.0f}%\033[0m', end='')
            feedback = sg.getFeedback(i)
            firstFeedback = True
            for f in feedback:
                print(f'    {f}' if firstFeedback else f'        {f}')
                firstFeedback = False
        print()

    averageGrade = totalGrade / len(configs["tests"])

    printFormattedText(f'\033[1mTests Passed: [{testsPassed}/{len(configs["tests"])}]')
    printFormattedText(f'Overall Grade: {averageGrade:.02f}%\033[0m\n')

    # Check to see if you want to continue grading
    continueGrading = input('Would you like to view the student output for the failed test cases? [Y/n] ')
    if 'n' not in continueGrading.lower():
        for i, test in enumerate(configs["tests"]):
            if sg.getGrade(i) < sg.passThreshold:
                printFormattedText(f'\n\033[1m{test["description"]}:\033[0m\n')

                graderTokens, studentTokens = sg.getCombinedVectors(i)

                lastTokenEnd = 0

                for tokenNum, token in enumerate(studentTokens):
                    graderToken = graderTokens[min(tokenNum, len(graderTokens) - 1)]

                    graderStr = graderOutputs[i][0][graderToken.start:graderToken.end]
                    studentStr = studentOutputs[i][0][token.start:token.end]

                    colorCode = '32' if graderStr == studentStr else '31'

                    print(studentOutputs[i][0][lastTokenEnd:token.start], end='')
                    printFormattedText(f'\033[1;{colorCode}m{studentStr}\033[0m', end='')

                    if graderStr != studentStr:
                        printFormattedText(f'\033[2;3m[{graderStr}]\033[0m', end='')

                    lastTokenEnd = token.end

                print(studentOutputs[i][0][lastTokenEnd:])



    if averageGrade >= sg.passThreshold:
        exit(0)
    else:
        exit(1)