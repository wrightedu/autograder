import os

import re as re

from pygments import highlight
from pygments.lexers import get_lexer_by_name
from pygments.formatters import TerminalTrueColorFormatter

# from newSmartGrader import SmartGrader

FORCE_WINDOWS_RENDERING = False

CHECKMARK, XMARK = ('✔', '✘') if os.name != 'nt' and not FORCE_WINDOWS_RENDERING else ('A', 'X')


def print_file(file_path, language='java'):
    with open(file_path) as f:
        text = f.read()
        text = text.replace('\t', '    ')
        lexer = get_lexer_by_name(language, stripall=True)
        formatter = TerminalTrueColorFormatter(style='fruity')
        print_formatted_text(highlight(text, lexer, formatter))


# TODO Have this take a dictionary or similar with formatting information
# TODO Have this actually convert ANSI to some windows formatting stuff maybe?
def print_formatted_text(text, end='\n', force_windows_rendering=False):
    if os.name == 'nt' or force_windows_rendering:
        print(re.sub(r'\033\[.*?m', '', text), end=end)
    else:
        print(text, end=end)



def print_test_cases(sg, test_cases, student_name=""):
    total_grade = 0
    tests_passed = 0

    if len(student_name) > 0:
        student_name = " for " + student_name

    print_formatted_text(f'\n\033[1;4mTest Case Results {student_name}\033[0m\n')
    for i, test in enumerate(test_cases):
        grade = sg.get_test_grade(i)

        total_grade += grade

        if grade == 100:
            print_formatted_text(
                f'\033[32;1m{CHECKMARK}\033[0m ({i}) {test["description"]}:')
            tests_passed += 1
            print_formatted_text(f'\033[2;3m{grade:-3.0f}%\033[0m')
        elif grade >= sg.pass_threshold:
            print_formatted_text(
                f'\033[32;1m{CHECKMARK}\033[0m ({i}) {test["description"]}:')
            tests_passed += 1
            print_formatted_text(
                f'\033[2;3m{min(grade, 99):-3.0f}%\033[0m', end='')
            feedback = sg.get_test_feedback(i)
            first_feedback = True
            for f in feedback:
                print(f'    {f}' if first_feedback else f'        {f}')
                first_feedback = False
        else:
            print_formatted_text(
                f'\033[31;1m{XMARK}\033[0m ({i}) {test["description"]}:')
            print_formatted_text(
                f'\033[2;3m{min(grade, 99):-3.0f}%\033[0m', end='')
            feedback = sg.get_test_feedback(i)
            first_feedback = True
            for f in feedback:
                print(f'    {f}' if first_feedback else f'        {f}')
                first_feedback = False
        print()

    averageGrade = total_grade / len(test_cases)

    print_formatted_text(
        f'\033[1mTests Passed: [{tests_passed}/{len(test_cases)}]')
    print_formatted_text(f'Overall Grade: {averageGrade:.02f}%\033[0m\n')


def print_test_case_results(sg, testCases):
    for i, test in enumerate(testCases):
        if sg.get_test_grade(i) < sg.pass_threshold:
            print_formatted_text(f'\n\033[1m{test["description"]}:\033[0m\n')

            test_cases_passed = [output.exit_code == 0 for output in sg.student_results]
            grader_tokens, student_tokens = sg.get_combined_vectors(i, test_cases_passed)

            last_token_end = 0

            for token_num, token in enumerate(student_tokens):
                grader_token = grader_tokens[min(token_num, len(grader_tokens) - 1)]

                grader_string = sg.grader_results[i].stdout[grader_token.start:grader_token.end]
                student_string = sg.student_results[i].stdout[token.start:token.end]

                color = '32' if grader_string == student_string else '31'

                print(sg.student_results[i].stdout[last_token_end:token.start], end='')
                print_formatted_text(f'\033[1;{color}m{student_string}\033[0m', end='')

                if grader_string != student_string:
                    print_formatted_text(f'\033[2;3m[{grader_string}]\033[0m', end='')

                last_token_end = token.end

            print(sg.student_results[i].stdout[last_token_end:])


# TODO See about simplifying this one a bit. Maybe there's a module that would let you keep the pretty colors?
def print_table(student_grades, test_cases):
    # Get the length of the longest student's name
    longest_name = max([len(g[0]) for g in student_grades] + [4])
    student_count_digits = len(f'(#{len(student_grades)-1})')

    col_width = max(len(f"Test {len(test_cases) - 1}"), len(f'100% {CHECKMARK}'))

    print_formatted_text(f'\033[1;4m {"NAME".rjust(int((longest_name + student_count_digits + 1) / 2 + len("NAME") / 2)):{longest_name + student_count_digits + 1}}', end=' ')

    for i, test_case in enumerate(test_cases):
        print(f' {f"TEST {i}".rjust(int(col_width / 2 + len(f"TEST {i}") / 2)):{col_width}}', end=' ')

    print_formatted_text(' OVERALL GRADE \033[0m')

    for i, (student_name, sg) in enumerate(student_grades):
        print_formatted_text(f'{student_name:{longest_name}} \033[2m{f"(#{i})":{student_count_digits}}\033[0m ', end=' ')

        if sg is None:
            na_string = "NA  ".rjust(col_width)
            for i, _ in enumerate(test_cases):
                print_formatted_text(f' \033[2;3m{na_string}\033[0m', end=' ')

            print_formatted_text("    \033[2;3mSkipped\033[0m")

        else:
            total_grade = 0
            total_weight = 0

            for i, test_case in enumerate(test_cases):
                grade = sg.get_test_grade(i)

                total_grade += grade * test_case.weight
                total_weight += test_case.weight

                if grade < sg.pass_threshold:
                    grade = min(grade, 99)
                    pass_fail = f'\033[31;1m{XMARK}\033[0m'

                else:
                    pass_fail = f'\033[32;1m{CHECKMARK}\033[0m'

                print_formatted_text(f' {f"{grade:-3.0f}% {pass_fail}":{col_width}}', end=' ')

            if total_weight != 0:
                total_grade /= total_weight
            else:
                total_grade = 100

            if total_grade < sg.pass_threshold:
                total_grade = min(total_grade, 99)
                pass_fail = f'\033[31;1m{XMARK}\033[0m'

            else:
                pass_fail = f'\033[32;1m{CHECKMARK}\033[0m'

            final_feedback = f"    {total_grade:-3.0f}% {pass_fail}"

            print_formatted_text(f' \033[1m{final_feedback}\033[0m')
