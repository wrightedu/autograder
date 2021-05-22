import os
import re as re
import subprocess
from os import path
from shutil import copyfile

from binaryornot.check import is_binary
from pygments import highlight
from pygments.formatters import TerminalTrueColorFormatter
from pygments.lexers import get_lexer_by_name
from tqdm import tqdm

class TestCase:
    """Data class that stores all of the information needed to run a certain test case
    """

    @staticmethod
    def load_from_array(array):
        """Creates an array of TestCase objects based on a list of dictionaries

        Args:
            array (list): The list of dictionaries to be converted into TestCase objects

        Returns:
            list: The list of TestCase objects
        """
        return [TestCase(**i) for i in array]


    def __init__(self, stdin='', description='', timeout=5, weight=1, runner_args=[], args=[], command=None, required_strings=[], required_strings_stderr=[]):
        """Create a basic data class to store information about test cases

        Args:
            stdin (str): The data to be piped into standard in for the test case
            description (str): A description of what the test case is testing
            timeout (int, optional): The time to allow the test case to run. Defaults to 5.
            args (list, optional): Any additional arguments to pass to the program for this test case. Defaults to []].
            command (list, optional): The command to be run to execute the test case. If None 
                is specified, the default command will be used. Defaults to None.
        """
        self.stdin = stdin
        self.description = description
        self.timeout = timeout
        self.weight = weight
        self.runner_args = runner_args
        self.args = args
        self.command = command
        self.required_strings = required_strings
        self.required_strings_stderr = required_strings_stderr



class TestResult:
    """Data class that contains the results of a single test case
    """

    def __init__(self, test_case, stdout, stderr, exit_code=0, timeout=False):
        """Creates a new set of test case Results

        Args:
            test_case (TestCase): The test case that these results are for
            stdout (str): A string containing the standard output of the program that ran this test case
            stderr (str): A string containing the standard error of the program that ran this test case
            exit_code (int, optional): The exit code of the program when it ran the test cases. Defaults to 0.
            timeout (bool, optional): Whether or not the program timed out while trying to run the test case. Defaults to False.
        """
        self.test_case = test_case
        self.stdout = stdout
        self.stderr = stderr
        self.exit_code = exit_code
        self.timeout = timeout



class Program:
    _language_extensions = ['.java', '.py', '.c', '.cpp', '.sh', '.bash', ]


    def __init__(self, directory, language='java', args=[]):
        """Creates a new program objects that stores all of the necessary information to compile, run, and test that program

        Args:
            directory (str): The program's base directory
            language (str, optional): The language that the program is written in. Defaults to 'java'. 
                Currently accepted values are 'java', 'cpp', 'c++', 'c', 'python', 'bash', and 'shell' 
            args (list, optional): The arguments to be passed to the program when it's being executed. Defaults to [].
        """
        if not path.isdir(directory):
            raise ValueError(f'{directory} is not a directory')

        self.directory = directory
        self.language = language

        self.src_bin_present = path.isdir(path.join(directory, 'src')) and path.isdir(path.join(directory, 'bin'))
        self.src_dir = 'src' if self.src_bin_present else ''
        self.bin_dir = 'bin' if self.src_bin_present else ''

        self.skip_grading = False

        self._command = None
        self._args = args


    def get_directory_listing(self, directory=None):
        """Gets an dictionary containing the directory structure of the program

        Args:
            directory (str, optional): The path of the directory to get the listing of. If None, the project's root directory will be used. Defaults to None.

        Returns:
            [dict]: A dictionary containing the directory information. Keys are file names, and value will be sub directory structure for directories, None for files
        """
        directory_dict = {}

        if directory is None:
            directory = self.directory

        # Iterate over every file and sub directory, adding each entry into the dictionary
        for file in os.listdir(directory):
            new_path = os.path.join(directory, file)
            if os.path.isdir(new_path):
                directory_dict[file] = self.get_directory_listing(new_path)
            else:
                directory_dict[file] = None
                
        return directory_dict


    def get_source_files(self):
        """Recursively finds all source files in the project directory tree

        Args:
            directory (str, optional): The subdirectory to print all of the source files for. 
                Defaults to None, which will start printing from the project base directory
        Returns:
            [list]: A list of all of the source files
        """

        files = []

        for dir_name, _, file_list in os.walk(self.directory):
            for fname in file_list:
                file_extension = os.path.splitext(fname)[-1]
                
                # TODO Add makefiles in here probably
                if file_extension in Program._language_extensions:
                    files.append(os.path.join(dir_name, fname))

        return files


    def set_command(self, command):
        """Manually sets the command to be run while executing test cases

        Args:
            command (tuple): A tuple containing the command and all of the arguments, in the form taken by subprocess.Popen
        """

        self._command = command


    def set_main_executable(self, executable_path):
        """Manually sets the executable path to be used when running the program

        Args:
            executable_path (str): The path to the executable file, relative to the project base directory
        """
        self._main_executable = executable_path
        self.generate_command(executable_path)


    def compile(self):
        """Compiles the program if necessary. If a makefile is available it will be used, otherwise 
                a fall back option will be used depending on the language being used.

        Returns:
            bool: True if the compilation was successful, false if an error was encountered.
        """

        # Check to see if there's a makefile in the program root directory
        if self._compile_make():
            print('Compilation with makefile successful')
            return True

        elif self.src_bin_present and self._compile_make():
            print('Compilation with makefile successful')
            return True

        print('Compilation with makefile failed, falling back to internal compilers')

        if self.language == 'java':
            return self._compile_java()

        elif self.language in ['c', 'cpp', 'c++']:
            return self._compile_c()

        else:
            return self._compile_scripts()


    def find_main_executable(self):
        """Iterates over the project directory and finds any potential executable files.
            Once all possible executable files have been found, a list will be displayed to the,
            who will then select one

        Returns:
            bool: True if an executable was found
        """ 

        potential_executables = []

        for dir_name, _, file_list in os.walk(path.join(self.directory, self.bin_dir)):
            for fname in file_list:
                file_path = path.join(dir_name, fname)
                if self._is_executable(file_path):
                    potential_executables.append(file_path)

        if len(potential_executables) > 1:
            print('Multiple potential executable files were found:')
            for i, executable_path in enumerate(potential_executables):
                print(f'  ({i}): {executable_path}')

            selection = int(input("Enter the numeric ID for the proper executable: ").strip())
            self._executable_path = potential_executables[selection]

        elif len(potential_executables) == 0:
            return False

        else:
            self._executable_path = potential_executables[0]

        self.generate_command(self._executable_path)

        return True


    def generate_command(self, executable_path, args=None):
        """Sets up the command used to execute the program based on the path to the executable

        Args:
            executable_path (str): The path to the main executable of the program
        """
        executable_extension = path.splitext(executable_path)[-1]
        relative_path = path.relpath(executable_path, self.directory)
        class_path = path.relpath(executable_path, path.join(self.directory, self.bin_dir))

        if self.language == 'java':
            if executable_extension == '.jar':
                self._command = ('java', '-jar', relative_path, *self._args)

            elif executable_extension == '.class':
                self._command = ('java', '-cp', self.bin_dir, class_path[:-6], *self._args)

        elif self.language == 'python':
            self._command = ('python', relative_path, *self._args)

        elif self.language in ['bash', 'shell']:
            self._command = ('bash', relative_path, *self._args)

        else:
            self._command = (f'.{os.sep}{relative_path}', *self._args)


    def run_tests(self, tests, description='Running Test Cases'):
        """Runs a series of test cases on the program by starting a subprocess and piping
            the specified strings into the standard input of that subprocess.

        Args:
            tests (list(TestCase)): A list of strings. Each string will be used as the standard input for a test case
        """

        self._results = []

        for test in tqdm(tests, desc=description):
            command = self._command if test.command is None else test.command
            
            program_pipe = subprocess.Popen((*test.runner_args, *command, *test.args), stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, cwd=self.directory)
            program_pipe.stdin.write(test.stdin.encode('utf-8'))
            program_pipe.stdin.close()

            timeout = False

            try:
                program_pipe.wait(test.timeout)
            except subprocess.TimeoutExpired:
                program_pipe.terminate()
                timeout = True

            test_output = program_pipe.stdout.read().decode('utf-8')
            test_errors = program_pipe.stderr.read().decode('utf-8')

            exit_code = program_pipe.returncode
            self._results.append(TestResult(test, test_output, test_errors, exit_code, timeout))

        return self._results


    def _compile_c(self):
        """Yeah no,

        Returns:
            bool: false
        """

        # TODO Somehow add support for compiling c/c++ code automatically...
        return False


    def _compile_java(self):
        """Internal function to compile a java project. Searches for all .java file and compiles them to the project's bin directory

        Returns:
            bool: True if all compilations were successfully, false if any of them encountered an error
        """

        print("Compiling java project...")

        source_directory = path.join(self.directory, self.src_dir)
        target_directory = path.join(self.directory, self.bin_dir)

        javac = ('javac', '-cp', source_directory, '-d', target_directory)

        # Compile all java files found
        for dir_name, _, file_list in os.walk(source_directory):
            for fname in file_list:
                if path.splitext(fname)[-1].lower() == '.java':
                    result = subprocess.run((*javac, path.join(dir_name, fname)))
                    if result.returncode != 0:
                        return False

        return True


    def _compile_make(self):
        """Internal function used to compile based off of a makefile

        Returns:
            bool: True if the compilation was successful, false if an error was encountered
        """

        source_directory = path.join(self.directory, self.src_dir)

        if 'makefile' in (i.lower() for i in os.listdir(self.directory)):
            result = subprocess.run('make', capture_output=True, cwd=self.directory)
            if result.returncode == 0:
                return True

        if source_directory != self.directory and 'makefile' in (i.lower() for i in os.listdir(source_directory)):
            result = subprocess.run('make', capture_output=True, cwd=source_directory)
            if result.returncode == 0:
                return True

        return False


    def _compile_scripts(self):
        """All that needs to be done for "compiling" a script is to copy it from the src dir to the bin dir if necessary

        Returns:
            bool: true
        """

        if not self.src_bin_present:
            return True

        source_directory = path.join(self.directory, self.src_dir)
        target_directory = path.join(self.directory, self.bin_dir)

        for dir_name, _, fileList in os.walk(source_directory):
            for fname in fileList:
                if path.splitext(fname)[-1] in ['.py', '.sh', '.bash', '']:
                    short_dir_name = dir_name[len(path.commonpath(source_directory, dir_name)):]
                    from_file = path.join(dir_name, fname)
                    to_file = path.join(target_directory, short_dir_name, fname)
                    copyfile(from_file, to_file)

        return True


    def _is_executable(self, file_name):
        """Checks if a file is executable or can be executed by the interpreter for the program's selected language

        Args:
            file_name (str): The name of the file to be checked

        Returns:
            bool: True if the file can be executed
        """

        extension = path.splitext(file_name)[-1]
        if os.access(file_name, os.X_OK) or extension == '.exe':
            return True

        if self.language == 'java' and extension in ['.class', '.jar']:
            return True

        if self.language == 'python' and extension in ['.py']:
            return True

        if self.language in ['bash', 'shell'] and extension in ['.sh', '.bash']:
            return True

        return self.language in ['c', 'cpp', 'c++'] and extension in [''] and is_binary(file_name)

