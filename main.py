#!/usr/bin/env python

import argparse
import json
import os

from os.path import join

from utils import *
from program import Program, TestCase, TestResult
from smartGrader import SmartGrader

if __name__ == '__main__':
    parser = argparse.ArgumentParser()

    # Take a path to the configuration file
    parser.add_argument('-c', '--config', type=str, default=None, help='The relative filepath to the config.json you would like to use')

    # Take a path to the student's source directory
    parser.add_argument('-s', '--student-directory', type=str, default=None, help='Selects a specific student directory for grading. Overrides the value set in config')

    # Flag to disable printing student directory stuff
    parser.add_argument('-n', '--no-cat', action='store_true', help='Disable catting student files')

    args = parser.parse_args()

    # Load in the configuration file
    configs = {}
    with open(join(args.config), 'r') as testCasesFile:
        configs = json.loads(testCasesFile.read())  

    
    test_cases = TestCase.load_from_array(configs['tests'])
    language = configs['settings']['language'] if 'language' in configs['settings'] else 'java'

    # Generate the grader outputs
    print("Generating grader outputs...")
    config_dir = os.path.dirname(args.config)
    grader_directory = join(config_dir, configs["settings"]["grader_directory"])
    print(grader_directory)
    grader_program = Program(grader_directory, language)
    print(grader_program.compile())
    print(grader_program.find_main_executable())
    grader_outputs = grader_program.run_tests(test_cases)

    print("Done")   

    student_programs = []
    student_grades = []
    student_projects_directory = join(config_dir, configs["settings"]["student_directory"])


    if args.student_directory is None:
        for sub_directory in sorted(os.listdir(student_projects_directory)):
            student_directory = os.path.join(student_projects_directory, sub_directory)
            if os.path.isdir(student_directory) and student_directory != grader_directory:
                student_programs.append(Program(student_directory, language))

    else: 
        student_programs.append(Program(args.student_directory, language))
        

    if not args.no_cat:
        for i in student_programs:

            i.print_source_files()

            print_formatted_text('\033[1;4mProject Directory Listing\033[0m')
            i.print_directory_listing()

            continue_grading = input('\nGrade Student Submission? [Y/n] ')

            i.skip_grading = 'n' in continue_grading.lower()


    for student in student_programs:
        if not student.skip_grading:
            compilation_successful = student.compile()

            if not compilation_successful:
                print('Compilation failed')
                continue


            student.find_main_executable()
            student_outputs = student.run_tests(test_cases, description=f'Testing Student {student.directory.split(os.sep)[-1]} Submission')

            sg = SmartGrader(configs['settings'], grader_outputs, student_outputs)
            sg.analyze()
            student_grades.append((student.directory.split(os.sep)[-1], sg))

        else:
            student_grades.append((student.directory.split(os.sep)[-1], None))

    if len(student_grades) > 1:
        while True:
            print_formatted_text('\033[2J\033[H', end="")
            print_table(student_grades, test_cases)

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

            print_test_cases(sg, configs["tests"], studentName)

            if False in [sg.get_test_grade(i) >= sg.pass_threshold for i in range(len(configs["tests"]))]:
                # Check to see if you want to continue grading
                giveFullOutput = input('Would you like to view the student output for the failed test cases? [Y/n] ')
                if 'n' not in giveFullOutput.lower():
                    print_test_case_results(sg, configs["tests"])

            input("Press enter to continue...")
    else:
        studentName, sg = student_grades[0]
        print_test_cases(sg, configs["tests"], studentName)

        # Check to see if you want to continue grading
        giveFullOutput = input('Would you like to view the student output for the failed test cases? [Y/n] ')
        if 'n' not in giveFullOutput.lower():
            print_test_case_results(sg, configs["tests"])