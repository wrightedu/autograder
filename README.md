# autograder
Automatic grading using coding and algorithms.

# Manual Auto-Grading

Manual Auto-Grading is done using the `main.py` program. It requires all student programs to be graded to be downloaded locally.

## Creating an Assignment

Assignments are simply directories with a pre-compiled known-good master grader program, a json file containing grading settings, and a set of sub-directories, each containing a single student submission. Student submissions currently _must_ have the source code for the assignment in a folder called `src`.

Note that the current structure of the auto-grader for programs whose out put is deterministically generated based on user input but is not static.

The supplied master grader program should follow the assignment description supplied to the students exactly. If it doesn't work for some cases, the validity of the grades generated can not be guaranteed.

Once the master grader program is written and compiled, the settings json will have to be created. The format/syntax/keywords/whatever used here are:

- `settings`: A dictionary containing settings to be used by the grading program.
  - `penalties`: A dictionary containing penalties to be applied when the student's program doesn't behave as expected.
    - `typeMismatch`: The penalty to be applied when the student's code outputs a string when a number is expected, or vice versa.
    - `tokenCountMismatch`: The penalty to be applied when the student's code generates the wrong number of 'important' outputs. Since it can sometimes be problematic to determine what outputs are important or not, this should usually have a comparatively low value.
    - `numericMismatch`: A penalty to be applied proportionally to the percent difference between the expected numeric output and the numeric output from the student's program.
    - `characterMismatch`: A penalty to be applied proportionally to the number of characters that differ between the expected sting output and the output from the student's program.
    - `runFailue`: The penalty to be applied when the student's program raises a run-time exception when the grader program does not. (__TODO__: Not yet implemented)
  - `penaltyWeight`: A weight used in converting the accumulated penalties to a percentage grade. The equation used is `percentGrade = 100 * exp(-penaltyWeight * accumulatedPenalties)`. The smaller this value is, the more 'lenient' the grading program will be.
  - `passTheshold`: The minimum computed grade required for any given test to be considered 'passing'. This is used to allow a little bit of wiggle room for student outputs that have a small typo or a different number of significant figures.
  - `collapseWhitespace`: A boolean value that determines whether or not the grader will consider differences in whitespace between two outputs important. (__TODO__: Not yet fully implemented and untested)
  - `graderProgram`: The location of the compiled grader program relative to the configuration file. Note that in the case of a java program, the `.class` portion of the file name should be omitted.
- `tests`: An array of dictionaries containing test case information. The dictionaries keys are as follows:
  - `description`: A short description of what the test case is testing.
  - `input`: A string that will be piped into stdin of the student's program.

## Running

To run the auto-grader locally, use the command `python main.py -c <path to configuration json> -d <path to student's project directory> [-l <langauge that project is in>]`

The auto-grader will then try to read in the configuration and student files. If that is successful, it will print out the contents of the student's files and ask if you want to continue grading. If you select yes, it will automatically run all the test cases on both the student and grader programs and analyze any differences. These differences will be printed out in a nice format :).

## Screenshots

![Screenshot showing the first part of manual auto-grading](https://cdn.discordapp.com/attachments/701797448414265405/708065450386391140/unknown.png "Screenshot 1")

![Screenshot showing the second part of manual auto-grading](https://cdn.discordapp.com/attachments/701797448414265405/708065511317045248/unknown.png "Screenshot 1")


## TODOs

- Add the ability to have test cases to require exact matches
- Add the ability to have test cases match a certain regex
- Add the ability to have test cases have files associated with them
- Add the ability to check files created by a test case
- Add the ability to have certain text to be considered important to the grader, regardless of whether the algorithm thinks it should be important