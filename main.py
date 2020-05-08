
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


def tree(rootDir, catFiles=True, language='java', recursionLevel=0):
    if catFiles:
        for file in os.listdir(rootDir):
            if os.path.isdir(join(rootDir, file)):
                tree(join(rootDir, file), catFiles=catFiles, language=language, recursionLevel=recursionLevel + 1)
            else:
                if not isBinary(join(rootDir, file)):
                    ext = file[file.rfind('.'):]
                    if ext in ['.java', '.py', '.c', '.cpp', '.sh', '.bash']:
                        print('\033[1;4m' + join(rootDir, file), '\033[0m')
                        with open(join(rootDir, file)) as f:
                            text = f.read()
                            text = text.replace('\t', '    ')
                            lexer = get_lexer_by_name(language, stripall=True)
                            formatter = TerminalFormatter(linenos=True)
                            print(highlight(text, lexer, formatter))
                        print('\n\n\n')
                
    else:
        if recursionLevel == 0:
            print('\033[1;4mProject Directory Listing\033[0m')
        print(recursionLevel * '    ' + os.path.basename(rootDir) + '/')
        for file in os.listdir(rootDir):
            if os.path.isdir(join(rootDir, file)):
                tree(join(rootDir, file), catFiles=catFiles, language=language, recursionLevel=recursionLevel + 1)
            else:
                print((recursionLevel + 1) * '    ' + file)


def compile(fromDir, toDir, language='java'):
    if language == 'java':
        for dirName, subdirList, fileList in os.walk(fromDir):
            for fname in fileList:
                if re.match(r'.*\.java$', fname):
                    compResults = subprocess.run(['javac', '-cp', fromDir, '-d', toDir, join(dirName, fname)])
                    if compResults.returncode != 0:
                        return False
        return True
    elif language in ['c', 'cpp', 'c++']:
        pass
    elif language == 'python':
        for dirName, subdirList, fileList in os.walk(fromDir):
            for fname in fileList:
                if re.match(r'.*\.py$', fname):
                    # Ignore any part of the dir name that is part of fromdir
                    shortDirName = dirName[len(os.path.commonpath(fromDir, dirName)):]
                    copyfile(join(dirName, fname), join(toDir, shortDirName, fname))
    return False

def generateOutputs(binDir, programPath, testCases, language='java', timeout=5):
    if language == 'java':
        if programPath[-6:] == '.class':
            programPath = programPath[:-6]
        command = ['java', '-cp', binDir, programPath]
        outputs = []
        for test in testCases:
            inputPipe = subprocess.Popen(["cat",  "-"], stdin=subprocess.PIPE, stdout=subprocess.PIPE)
            processPipe = subprocess.Popen(command, stdin=inputPipe.stdout, stdout=subprocess.PIPE)

            inputPipe.stdin.write(test["input"].encode("utf-8"))

            inputPipe.stdin.close()

            if processPipe.wait(timeout) is None:
                processPipe.terminate()

            testResult = processPipe.stdout.read().decode('utf-8')
            outputs.append(testResult)
        return outputs
    else:
        return []

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
    parser.add_argument('-l', '--language', type=str, default='java', choices=['java', 'c', 'c++', 'cpp', 'python'], help='The language of the assignment being graded')
    
    args = parser.parse_args()

    # Print student directory contents
    tree(args.project_directory, not args.no_cat)
    tree(args.project_directory, False)

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
    if 'makefile' in [filename.lower() for filename in os.listdir(args.project_directory)]:
        print('\nAttempting to build with student makefile')
        makeResults = subprocess.run('make', capture_output=True)
        if makeResults.returncode != 0:
            print("STUDENT MAKEFILE FAILED\n")
            print(makeResults.stdout.decode('utf-8'))
    else:
        print('\nNo makefile found, attempting to build with internal compiler')
        compilationSuccessful = compile(join(args.project_directory, 'src'), join(args.project_directory, 'bin'), language=args.language)
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
            if 'bin/' in program:
                program = program[program.find('bin/') + 4:]
                studentPrograms.append(program)
    studentProgramPath = studentPrograms[0]
    if len(studentPrograms) > 1:
        for i, program in enumerate(studentPrograms):
            print(i + 1, program)
        selection = input("Which program would you like to run? (enter number) ").strip()
        studentProgramPath = studentPrograms[int(float(selection)) - 1]

    
    # Get student outputs
    studentOutputs = generateOutputs(join(args.project_directory, 'bin'), studentProgramPath, configs["tests"])

    # Generate the grader outputs
    configDir = os.path.dirname(args.config)
    graderPath = join(configDir, configs["settings"]["graderProgram"])
    
    graderOutputs = generateOutputs(configDir, configs["settings"]["graderProgram"], configs['tests'])
    

    sg.graderOutputs = graderOutputs
    sg.studentOutputs = studentOutputs
    sg.analyze()
    
    # TODO Have it only grade certain test cases maybe? Add a flag?

    totalGrade = 0
    testsPassed = 0

    print('\033[1;4mTest Case Results\033[0m\n')
    for i, test in enumerate(configs["tests"]):
        grade = sg.getGrade(i)

        totalGrade += grade

        if grade == 100:
            print(f'\033[32;1m✔\033[0m ({i}) {test["description"]}:')
            testsPassed += 1
            print (f'\033[2;3m{grade:-3.0f}%\033[0m')
            # TODO Maybe print out what the correct output was?
        elif grade >= sg.passThreshold:
            print(f'\033[32;1m✔\033[0m ({i}) {test["description"]}:')
            testsPassed += 1
            print (f'\033[2;3m{min(grade, 99):-3.0f}%\033[0m', end='')
            feedback = sg.getFeedback(i)
            firstFeedback = True
            for f in feedback:
                print(f'    {f}' if firstFeedback else f'        {f}')
                firstFeedback = False
        else:
            print(f'\033[31;1m✘\033[0m ({i}) {test["description"]}:')
            print (f'\033[2;3m{min(grade, 99):-3.0f}%\033[0m', end='')
            feedback = sg.getFeedback(i)
            firstFeedback = True
            for f in feedback:
                print(f'    {f}' if firstFeedback else f'        {f}')
                firstFeedback = False
        print()

    averageGrade = totalGrade / len(configs["tests"])

    print(f'\033[1mTests Passed: [{testsPassed}/{len(configs["tests"])}]')
    print(f'Overall Grade: {averageGrade:.02f}%\033[0m\n')


    if averageGrade >= sg.passThreshold:
        exit(0)
    else:
        exit(1)