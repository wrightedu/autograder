#!/usr/bin/env python

import argparse
import json
import os

from os.path import join

from utils import *
from program import Program, TestCase

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
    parser.add_argument('-l', '--language', type=str, default='java', choices=['java', 'c', 'c++', 'cpp', 'python', 'bash', 'shell'], help='The language of the assignment being graded')

    args = parser.parse_args()

    # Load in the configuration file
    configs = {}
    with open(join(args.config), 'r') as testCasesFile:
        configs = json.loads(testCasesFile.read())  

    # Generate the grader outputs
    print("Generating grader outputs...")
    config_dir = os.path.dirname(args.config)
    grader_path = join(config_dir, configs["settings"]["graderProgram"])

    test_cases = TestCase.load_from_array(configs['tests'])

    grader_outputs = generateOutputs(config_dir, configs["settings"]["graderProgram"], configs['tests'], noBin=True)
    print("Done")
    

    student_programs = []
    student_grades = []


    if args.project_directory is not None:
        student_programs.append(Program(args.project_directory, args.language))
        # if student_programs.project_directory[-1] == os.sep:
        #     args.project_directory = args.project_directory[:-1]
        # sg = gradeStudentProgram(args.project_directory, graderOutputs, configs, args.language, not args.no_cat)
        # studentGrades.append((os.path.basename(args.project_directory), sg))

    else:
        # TODO Iterate over the directory in which the test case file is stored, looking at each student's directory
        for sub_directory in sorted(os.listdir(config_dir)):
            student_directory = os.path.join(config_dir, sub_directory)
            print(student_directory)
            if os.path.isdir(student_directory):
                student_programs.append(Program(student_directory, args.language))
            # if os.path.isdir(join(configDir, studentDirectory)):
            #     printFormattedText('\033[2J\033[H', end="")
            #     printFormattedText(f'\033[1;4m{studentDirectory}\033[0m\n')

            #     for dirName, subdirList, fileList in os.walk(os.path.join(configDir, studentDirectory)):
            #         if 'src' in subdirList:
                        # sg = gradeStudentProgram(dirName, graderOutputs, configs, args.language, not args.no_cat)
            #             studentGrades.append((studentDirectory, sg))

    print(student_programs)

    for i in student_programs:
        if not args.no_cat:
            i.print_source_files()

        printFormattedText('\033[1;4mProject Directory Listing\033[0m')
        i.print_directory_listing()

        continue_grading = input('\nContinue grading? [Y/n] ')

        if 'n' in continue_grading.lower():
            continue


        compilation_successful = i.compile()

        if not compilation_successful:
            print('Compilation failed')
            continue


        i.find_main_executable()
        student_outputs = i.run_tests(test_cases)

        sg = SmartGrader(configs['settings'], grader_outputs, student_outputs)
        sg.analyze()
        student_grades.append((i.directory.split(os.sep)[-1], sg))

    if len(student_grades) > 1:
        while True:
            printFormattedText('\033[2J\033[H', end="")
            printTable(student_grades, configs['tests'])

            moreFeedback = input("Enter a student name or the displayed ID number (including the #) for more feedback. Leave blank and press enter to exit: ")

            if len(moreFeedback) == 0:
                break

            if moreFeedback[0] == '#':
                studentIdx = int(moreFeedback[1:])

            else:
                studentIdx = -1

                for i, (studentName, sg) in enumerate(student_grades):
                    if studentName == moreFeedback:
                        studentIdx = i
                        break

                if studentIdx == -1:
                    try:
                        studentIdx = int(moreFeedback)
                    except:
                        pass

                if studentIdx == -1:
                    print(f'The student "{studentName}" could not be found. Please try again')
                    continue

            studentName, sg = student_grades[studentIdx]

            printTestResults(sg, configs["tests"], studentName)

            if False in [sg.getGrade(i) >= sg.passThreshold for i in range(len(configs["tests"]))]:
                # Check to see if you want to continue grading
                giveFullOutput = input('Would you like to view the student output for the failed test cases? [Y/n] ')
                if 'n' not in giveFullOutput.lower():
                    printTestOutputsWithDifferencesHighlightedInPrettyColorsAndBoldTextUnlessIfYoureOnWindowsBecauseWindowsIsBadAndDoesntLikePrettyThings(sg, configs["tests"])

            input("Press enter to continue...")
    else:
        studentName, sg = student_grades[0]
        printTestResults(sg, configs["tests"], studentName)

        # Check to see if you want to continue grading
        giveFullOutput = input('Would you like to view the student output for the failed test cases? [Y/n] ')
        if 'n' not in giveFullOutput.lower():
            printTestOutputsWithDifferencesHighlightedInPrettyColorsAndBoldTextUnlessIfYoureOnWindowsBecauseWindowsIsBadAndDoesntLikePrettyThings(sg, configs["tests"])