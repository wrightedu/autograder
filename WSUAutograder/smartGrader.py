#!/usr/bin/env python

# A quick start at a smart grading program
import re as re
from difflib import ndiff
from enum import Enum
from math import cosh, exp, log

from lark import Lark

# from WSUAutograder import TestCase, TestResult

TOKEN_GRAMMER = '''
start: (float | int | word | space)*

INTEGER: "0".."9"+
SPACE: /[\s]+/
SIGN: "-" | "+"
DOT: "."
WORD: /[^\s\d\.+-]/+

int.2: SIGN? INTEGER
float.3: SIGN? INTEGER? DOT INTEGER
word: WORD | SIGN DOT? | DOT
space: SPACE
'''


class TokenType(Enum):
    none = 0
    word = 1
    integer = 2
    floating = 3
    whitespace = 4

    @staticmethod
    def get_type(string):
        if len(string) == 0:
            return TokenType.none
        elif string.isspace():
            return TokenType.whitespace
        elif string[0] in '-+' and string[1:].isdecimal():
            return TokenType.integer
        try:
            _ = float(string)
            return TokenType.floating
        except ValueError:
            return TokenType.word

class Token:
    def __init__(self, value, start, end, token_type=TokenType.word):
        self.value = value
        self.start = start
        self.end = end
        self.token_type = token_type
        # self.has_difference = has_difference

    def offset(self, delta):
        self.start += delta
        self.end += delta
        return self

    def __str__(self):
        return f'{self.value}'

    def __hash__(self):
        return (self.value, self.start, self.end).__hash__()

    def __eq__(self, other):
        return self.__cmp__(other) == 0

    def __gt__(self, other):
        return self.__cmp__(other) > 0

    def __lt__(self, other):
        return self.__cmp__(other) < 0

    def __ne__(self, other):
        return self.__cmp__(other) != 0

    def __cmp__(self, other):
        if self.start < other.start:
            return -1
        if self.start > other.start:
            return 1
        if self.end < other.end:
            return -1
        if self.end > other.end:
            return 1
        if self.value < other.value:
            return -1
        if self.value > other.value:
            return 1
        return 0


class SmartGrader():
    """A class that uses difference token vectors to automatically determine how well the output
        from a given student submission matches the output from a master teacher program
    """

    def __init__(self, settings={}, grader_results=[], student_results=[]):
        """ Creates a new SmartGrader object

        Keyword Arguments:
            settings {dict} -- A dictionary that stores the settings used by the SmartGrader
                                when determining grades (default: {{}})
            grader_results {list} -- An array containing the outputs of the grader program for a set of test cases
            student_results {list} -- An array containing the outputs of the student program for a set of test cases
        """
        self.load_settings(**settings)
        self.grader_results = grader_results
        self.student_results = student_results
        self.grader_tokens = None
        self.student_tokens = None
        self._lexer = Lark(TOKEN_GRAMMER, parser="lalr")


    def load_settings(self, penalties={}, penalty_weight=0.1, pass_threshold=95, collapse_whitespace=True, all_tokens_strings=False, ignore_nonnumeric_tokens=False, enforce_floating_point=False,  language='java', connect_adjacent_words=False, grader_directory='Grader', student_directory='Student', **kwargs):
        self.load_penalties(**penalties)
        self.penalty_weight = penalty_weight
        self.pass_threshold = pass_threshold
        self.collapse_whitespace = collapse_whitespace
        self.all_tokens_strings = all_tokens_strings
        self.ignore_nonnumeric_tokens = ignore_nonnumeric_tokens
        self.enforce_floating_point = enforce_floating_point
        self.language = language
        self.connect_adjacent_words = connect_adjacent_words
        _ = grader_directory
        _ = student_directory

        for i in kwargs:
            print(f'Configuration setting {i} was not recognized')


    def load_penalties(self, type_penalty=20, token_count_penalty=50, numeric_penalty=10, character_penalty=50, run_failure_penalty=100, compile_failure_penalty=1000, timeout_penalty=100, missing_string_penalty=100, **kwargs):
        self.type_penalty = type_penalty
        self.token_count_penalty = token_count_penalty
        self.numeric_penalty = numeric_penalty
        self.character_penalty = character_penalty
        self.run_failure_penalty = run_failure_penalty
        self.compile_failure_penalty = compile_failure_penalty
        self.timeout_penalty = timeout_penalty
        self.missing_string_penalty = missing_string_penalty


        for i in kwargs:
            print(f'Configuration setting penalties.{i} was not recognized')


    def convert_penalty_to_grade(self, penalty):
        """Uses an exponential decay to convert the student's accumulated penalty to a letter grade

        Arguments:
            penalty {float} -- The accumulated penalty

        Returns:
            float -- The grade associated with that penalty
        """
        return 100 * exp(-self.penalty_weight * penalty)


    # TODO Add in support for checking for required strings
    def analyze(self):
        """Performs a full grading analysis of the provided inputs and outputs

        Raises:
            ValueError: Raised if there are a different number of grader and student outputs
        """
        
        # First, make sure that we have the same number of test cases from the grader and the student
        if len(self.grader_results) != len(self.student_results):
            raise ValueError("Grader and Student must have the same number of test cases")

        # Fill in the arrays with empty values
        self.grader_tokens = [None] * len(self.grader_results)
        self.student_tokens = [None] * len(self.student_results)

        for i in range(len(self.grader_results)):
            self.grader_tokens[i] = [None] * len(self.grader_results)
            self.student_tokens[i] = [None] * len(self.student_results)

        # Generate all of the token vectors
        for i in range(len(self.grader_results)):
            for j in range(len(self.grader_results)):
                self.grader_tokens[i][j] = self.token_vectors_by_line(self.grader_results[i].stdout, self.grader_results[j].stdout)
                self.student_tokens[i][j] = self.token_vectors_by_line(self.student_results[i].stdout, self.student_results[j].stdout)

    def get_combined_vectors(self, test_case_num, mask_array=None):
        if mask_array is None:
            mask_array = [True] * len(self.grader_results)

        grader_vector = self.grader_tokens[test_case_num]
        combined_grader_vectors = []
        for vect in (vect for mask, vect in zip(mask_array, grader_vector) if mask):
            combined_grader_vectors.extend(vect)
        combined_grader_vectors = list(set(combined_grader_vectors))
        combined_grader_vectors.sort()

        student_vector = self.student_tokens[test_case_num]
        combined_student_vectors = []
        for vect in (vect for mask, vect in zip(mask_array, student_vector) if mask):
            combined_student_vectors.extend(vect)
        combined_student_vectors = list(set(combined_student_vectors))
        combined_student_vectors.sort()

        return combined_grader_vectors, combined_student_vectors


    def _grade_token_vectors(self, test_num):
        total_error = 0
        feedback = []

        test_case_passed = [i.exit_code == 0 for i in self.student_results]
        grader_tokens, student_tokens = self.get_combined_vectors(test_num, test_case_passed)

        student_result = self.student_results[test_num]

        if student_result.exit_code != 0 and self.grader_results[test_num].exit_code == 0:
            feedback.append("Student program encountered an unexpected runtime exception")
            total_error += self.run_failure_penalty

        for i in [i for i in student_result.test_case.required_strings if i not in student_result.stdout]:
            feedback.append(f'Missing string \'{i}\' in standard output')
            total_error += self.missing_string_penalty

        for i in [i for i in student_result.test_case.required_strings_stderr if i not in student_result.stderr]:
            feedback.append(f'Missing string \'{i}\' in standard error')
            total_error += self.missing_string_penalty


        if len(grader_tokens) != len(student_tokens):
            total_error += self.token_count_penalty

            # Convert the token vector into easily readable strings
            grader_string = '[' + ', '.join(f'\'{i}\'' for i in grader_tokens) + ']'
            student_string = '[' + ', '.join(f'\'{i}\'' for i in student_tokens) + ']'
            # student_string = '[]'

            feedback.append(f"Expected {grader_string}, got {student_string}")

        token_count = min(len(grader_tokens), len(student_tokens))

        for i in range(token_count):
            grader_value = grader_tokens[i].value
            student_value = student_tokens[i].value

            # If the two tokens are of different type, this is bad
            if type(grader_value) != type(student_value):
                # Before supplying any feedback, check to make sure these weren't both numeric types
                if any(not isinstance(i, (float, int)) for i in (grader_value, student_value)) or self.enforce_floating_point:
                    total_error += self.type_penalty
                    feedback.append(f"Expected a {type(grader_value)} ({grader_value}), got a {type(student_value)} ({student_value})")

            # If the grader and the student vectors are different, this is also bad
            elif grader_value != student_value:
                feedback.append(f"Expected '{grader_value}', got '{student_value}'")

                # If the student values were numeric the penalty will be proportional to the difference
                #   between the two values, scaled down by the magnitude of the expected value
                # Note that log(cosh(x)) is equal to 0 at x=0 and will asymptotically approach abs(x) as x 
                #   approaches plus or minus infinity. Add one to this and we have a nice scaling factor that 
                #   will almost be the same as the percent difference, but doesn't have the unfortunate side effect
                #   of blowing up in a nasty way as it gets close to zero
                if isinstance(grader_value, (float, int)):
                    scale = log(cosh(grader_value)) + 0.25 if abs(grader_value) < 0.292055305409401 else abs(grader_value)
                    total_error += self.numeric_penalty * abs(grader_value - student_value) / scale

                # If they are strings, the penalty will be proportional to the number of characters that are different
                else:
                    total_error += self.character_penalty * len(list(i for i in ndiff(grader_value, student_value) if i[0] in '-+'))

        return total_error, feedback


    def get_test_grade(self, test_num):
        """ Gets the computed grade that the student received for a given test case

        Arguments:
            test_num {int} -- The test case to get the grade for

        Raises:
            IndexError: Raised if the specified test case is larger than the number of test cases

        Returns:
            float -- The grade received for the specified test case
        """

        if test_num >= len(self.student_results):
            raise IndexError("Test case number must be less than the number of test cases")

        total_error, _ = self._grade_token_vectors(test_num)

        return self.convert_penalty_to_grade(total_error)


    def get_test_feedback(self, test_num):
        """Gets some basic feedback on what the student got wrong for a certain test case

        Arguments:
            testCaseNum {int} -- The test case to get feedback for

        Raises:
            IndexError: Raised if the specified test case index is out of bounds

        Returns:
            list -- A list of strings containing the feedback
        """
        
        if test_num >= len(self.student_results):
            raise IndexError("Test case number must be less than the number of test cases")

        _, feedback = self._grade_token_vectors(test_num)

        feedback = sorted(set(feedback))

        return feedback


    # TODO This needs to be more rigorous. It currently has issues with edge cases where a floating point numbers starting with a .
    def _split_tokens(self, string):
        """Splits a string into individual tokens

        Args:
            string (str): The string to split into tokenStr

        Returns:
            list(str): A list of tokens representing the string
        """

        tokens = []
        token_start = 0

        lark_tokens = self._lexer.parse(string)

        for i in lark_tokens.children:
            if i.data == 'word':
                token_type = TokenType.word
            elif i.data == 'int':
                token_type = TokenType.integer
            elif i.data == 'float':
                token_type = TokenType.floating
            elif i.data == 'space':
                token_type = TokenType.whitespace
            else:
                token_type = TokenType.none

            token_value = ''.join(t.value for t in i.children)

            tokens.append(Token(token_value, token_start,  token_start + len(token_value), token_type))
            token_start += len(token_value)

        return tokens


    def _get_first_diff(self, a, b, tokens):
        # Find the first character that is different between the two strings
        first_difference = 0

        while a[first_difference] == b[first_difference]:
            first_difference += 1
            if first_difference >= len(a) or first_difference >= len(b):
                break

        # We now know where the first difference occurs, but since we're interested in differences
        #   by token, we're more interested in where the token containing this first 
        #   difference starts
        for token in tokens:
            if first_difference in range(token.start, token.end):
                first_difference = token.start
                break

        return first_difference


    def _get_last_diff(self, a, b, tokens):
        # Now do the same thing, only for the last difference
        last_difference = -1

        while a[last_difference] == b[last_difference]:
            last_difference -= 1

            if -last_difference > len(a) or -last_difference > len(b):
                break

        last_difference += len(a) + 1

        for token in reversed(tokens):
            if last_difference in range(token.start, token.end):
                last_difference = token.end - len(a)
                break

        return last_difference


    def token_vectors_by_line(self, output_a, output_b):
        """A better way of getting difference tokens if the output contains more than one line

        Arguments:
            output_a {str} -- The string to get the changes in
            output_b {str} -- The base string to compare fromStr to

        Returns:
            list -- A list containing all of the differences
        """

        # If the outputs are the same, there will be no differences between them
        if output_a == output_b:
            return []

        # Get a list of line by line differences
        diffs = ndiff([i + '\n' for i in output_a.splitlines()], [i + '\n' for i in output_b.splitlines()])
        diff_lines = []

        # Generate matched pairs of lines from both outputs
        for diff in diffs:
            prefix = diff[:2]
            line = diff[2:]

            if prefix == '  ':
                diff_lines.append([line, line])
            elif prefix == '+ ' and len(diff_lines) > 0 and diff_lines[-1][1] is None:
                diff_lines[-1][1] = line
            elif prefix == '+ ':
                diff_lines.append(['', line])
            elif prefix == '- ':
                diff_lines.append([line, None])

        diff_lines = list(map(lambda x: (x[0].replace('\n', ''), '' if x[1] is None else x[1].replace('\n', '')), diff_lines))

        line_start = 0
        tokens = []

        # Get the difference tokens from each of the individual lines
        for line in diff_lines:
            newTokens = self.get_token_vector(line[0], line[1]) if line[0] != line[1] else []
            for token in newTokens:
                token.offset(line_start)
                tokens.append(token)
            line_start += len(line[0]) + 1

        return tokens


    def get_token_vector(self, line_a, line_b):
        """ Gets a smart token difference vector. Any words or numbers that change between
            the two strings will be included in the vector, with adjacent words that have all 
            been changed merged into a single string

        Arguments:
            line_a {string} -- The string to get the changes in
            line_b {string} -- The base string to be compared to
        """
        # If the strings are identical, there will be no tokens
        if line_a == line_b or len(line_a) == 0:
            return []

        possible_tokens = list(filter(lambda x: not(x.token_type == TokenType.whitespace and self.collapse_whitespace), self._split_tokens(line_a)))
        possible_tokens = list(filter(lambda x: x.token_type in (TokenType.integer, TokenType.floating) or not self.ignore_nonnumeric_tokens, possible_tokens))

        first_difference = self._get_first_diff(line_a, line_b, possible_tokens)
        last_difference = self._get_last_diff(line_a, line_b, possible_tokens)

        if last_difference == 0:
            trimmed_line_a = line_a[first_difference:]
            trimmed_line_b = line_b[first_difference:]
        else:
            trimmed_line_a = line_a[first_difference:last_difference]
            trimmed_line_b = line_b[first_difference:last_difference]

        raw_diffs = list(ndiff(trimmed_line_a, trimmed_line_b))
        diffs = []

        for diff in raw_diffs:
            if diff[0] == '-':
                diffs.append(True)
            elif diff[0] == ' ':
                diffs.append(False)
            elif diff[0] == '+' and len(diffs) > 0:
                diffs[-1] = True

        token_vector = []

        for token in possible_tokens:
            start = max(token.start - first_difference, 0)
            end = max(token.end - first_difference, 0)
            if any(i for i in diffs[start:end] if i):
                if self.connect_adjacent_words and token_vector:
                    if token_vector[-1].token_type == TokenType.word and token.token_type == TokenType.word:
                        start = token_vector[-1].start
                        end = token.end
                        token_vector[-1] = Token(line_a[start:end], start, end, TokenType.word)
                    else:
                        token_vector.append(token)
                else:
                    token_vector.append(token)

        for token in token_vector:
            if token.token_type == TokenType.integer:
                token.value = int(token.value)
            elif token.token_type == TokenType.floating:
                token.value = float(token.value)


        # TODO Maybe make it so that adjacent words can be combined into a single token?
        return token_vector
