# autograder
Automatic grading using coding and algorithms.

## Running

To run the auto-grader locally on one of the sample assignments, use the command `python main.py --assignment <assignment name> --student <student numbers...>`.
To get a list of sample assignments available, run `python main.py --list-assignments`

## Assignment Setup

Each assignment directory needs to contain a master grader program to produce known good outputs and a configuration json. The setup of the configuration file is subject to change as the project matures, but as of right now the format should be as follows:

- `settings`: A dictionary containing settings to be used by the grader.
  - `penalties`: A dictionary of penalty values to apply when a students program does not produce the expected result.
    - `typeMismatch`: The penalty to apply when the student outputs a string when a number is expected or vice versa.
    - `tokenCountMismatch`: The penalty to apply when the student has the wrong number of outputs.
    - `numericMismatch`: A penalty to be applied proportionally the the percent difference between a student generated numeric output and the expected numeric output.
    - `characterMismatch`: A penalty to be applied proportionally to the number of characters that are different between a student generated string output and the expected string output.
    - `runFailure`: The penalty to apply when the student program raises a run time exception (__TODO__: Not yet implemented)
    - `compileFailure`: The penalty to apply when the student program fails to compile (__TODO__: Not yet implemented)
  - `penaltyWeight`: Used to translate the student's accumulated penalty to a 'grade'. The equation used is `grade = 100 * exp(-weight * penalty)`
  - `passThreshold`: The minimum computed grade required for a given test case to be considered passing
  - `collapseWhitespace`: A boolean value that when true tells the grader that differences in whitespace is to be considered important. When false, all whitespace is treated as a single space.
- `tests`: An array containing a list of test cases to be run on the programs. Test cases are in the following format:
  - `description`: A human readable description of what this particular test case is testing for.
  - `input`: An array of strings to be piped into the standard input of the program one at a time.

## TODOs

- Add the ability to have test cases to require exact matches
- Add the ability to have test cases match a certain regex
- Add the ability to have test cases have files associated with them
- Add the ability to check files created by a test case
- Add the ability to have certain text to be considered important to the grader, regardless of whether the algorithm thinks it should be important
- Better handling of output comparison when the students output is in a different order or has a different number of tokens