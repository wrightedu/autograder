import os
from os import path
import re
import subprocess
from shutil import copyfile
from tqdm import tqdm
from binaryornot.check import is_binary

from pygments import highlight
from pygments.lexers import get_lexer_by_name
from pygments.formatters import TerminalTrueColorFormatter

from utils import print_file, print_formatted_text


class Program:
    language_extensions = ['.java', '.py', '.c', '.cpp', '.sh', '.bash', ]


    def __init__(self, directory, language='java', args=[]):
        """Creates a new program objects that stores all of the necessary information to compile, run, and test that program

        Args:
            directory (str): The program's base directory
            language (str, optional): The language that the program is written in. Defaults to 'java'. 
                Currently accepted values are 'java', 'cpp', 'c++', 'c', 'python', 'bash', and 'shell' 
            args (list, optional): The arguments to be passed to the program when it's being executed. Defaults to [].
        """
        self.directory = directory
        self.language = language

        self.src_bin_present = path.isdir(path.join(directory, 'src')) and path.isdir(path.join(directory, 'bin'))
        self.src_dir = 'src' if self.src_bin_present else ''
        self.bin_dir = 'bin' if self.src_bin_present else ''

        self._command = None
        self._args = args


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


    def _compile_java(self):
        """Internal function to compile a java project. Searches for all .java file and compiles them to the project's bin directory

        Returns:
            bool: True if all compilations were successfully, false if any of them encountered an error
        """
        source_directory = path.join(self.directory, self.src_dir)
        target_directory = path.join(self.directory, self.bin_dir)

        javac = ('javac', '-cp', source_directory, '-d', target_directory)

        # Compile all java files found
        for dir_name, _, file_list in os.walk(source_directory):
            for fname in file_list:
                if path.splitext[-1].lower() == 'java':
                    result = subprocess.run((*javac, path.join(dir_name, fname)))
                    if result.returncode != 0:
                        return False

        return True


    def _compile_c(self):
        """Yeah no,

        Returns:
            bool: false
        """

        # TODO Somehow add support for compiling c/c++ code automatically...
        print('Automatically detecting and compiling c/c++ code is not easy. Makefiles are recommended')
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
                if self._is_executable(file_path, self.language):
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

        self.generate_command(executable_path)

        return True


    def generate_command(self, executable_path):
        """Sets up the command used to execute the program based on the path to the executable

        Args:
            executable_path (str): The path to the main executable of the program
        """

        executable_extension = path.splitext(executable_path)[-1]
        relative_path = path.relpath(executable_path, self.directory)

        if self.language == 'java':
            if executable_extension == '.jar':
                self._command = ('java', '-jar', relative_path, *self._args)

            elif executable_extension == '.class':
                self._command = ('java', '-cp', self.bin_dir, relative_path[-6], *self._args)

        elif self.language == 'python':
            self._command = ('python', relative_path, *self._args)

        elif self.language in ['bash', 'shell']:
            self._command = ('bash', relative_path, *self._args)

        else:
            self._command = (f'./{relative_path}', *self._args)


    def _is_executable(self, file_name):
        """Checks if a file is executable or can be executed by the interpreter for the program's selected language

        Args:
            file_name (str): The name of the file to be checked

        Returns:
            bool: True if the file can be executed
        """

        extension = path.splitext(file_name)[-1]
        if os.access(path, os.X_OK) or extension == '.exe':
            return True

        if self.language == 'java' and extension in ['.class', '.jar']:
            return True

        if self.language == 'python' and extension in ['.py']:
            return True

        if self.language in ['bash', 'shell'] and extension in ['.sh', '.bash']:
            return True

        return self.language in ['c', 'cpp', 'c++'] and extension in [''] and is_binary(file_name)


    # TODO: make a TestCase class that contains information like stdin, arguments, commands, and timeout
    def run_tests(self, tests, timeout=5):
        """Runs a series of test cases on the program by starting a subprocess and piping
            the specified strings into the standard input of that subprocess.

        Args:
            tests (list(str)): A list of strings. Each string will be used as the standard input for a test case
            timeout (int, optional): The amount of time to wait for the program to finish running before force killing it. Defaults to 5.
        """

        self._results = []

        for test in tqdm(tests):
            program_pipe = subprocess.Popen(self._command, stdin=subprocess.PIPE, stdout=subprocess.PIPE)
            program_pipe.stdin.write(test.encode('utf-8'))
            program_pipe.stdin.close()

            if program_pipe.wait(timeout) is None:
                program_pipe.terminate()

            test_output = program_pipe.stdout.read().decode('utf-8')
            exit_code = program_pipe.returncode
            self._results.append((test_output, exit_code))


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

        self.generate_command(executable_path)


    def print_source_files(self, directory = None):
        """Recursively prints all source files in the project directory tree

        Args:
            directory (str, optional): The subdirectory to print all of the source files for. 
                Defaults to None, which will start printing from the project base directory
        """

        if directory is None:
            directory = self.directory

        for dir_name, _, file_list in os.walk(directory):
            for fname in file_list:
                file_extension = os.path.splitext(fname)[-1]

                # TODO Better handling of language selection for syntax highlighting
                # TODO Add makefiles in here probably
                if file_extension in Program.language_extensions:
                    path = os.path.join(dir_name, fname)
                    print_formatted_text(f'\033[1;4m{path}\033[0m')
                    print_file(path, language=file_extension[1:])


    def print_directory_listing(self, directory=None, recursion_level=0, indent='│   ', dir_branch='├───┐', file_branch='├── '):
        """Recursively prints a nicely formatted listing of all of the files in the project's directory tree

        Args:
            directory (string, optional): The current directory being recursed through. Defaults to None, which 
                specifies the project base directory
            recursion_level (int, optional): The current recursion depth. Defaults to 0.
            indent (str, optional): A string printed for each directory level in the tree. Defaults to '│   '.
            dir_branch (str, optional): A string printed before any directory name in the tree. Defaults to '├───┐'.
            file_branch (str, optional): A string printed before any file name in the tree. Defaults to '├── '.
        """
        if directory is None:
            directory = self.directory

        file_indent = f'{recursion_level * indent}{file_branch}'
        dir_indent = f'{(recursion_level - 1) * indent}{dir_branch}'

        # Prints this directory name 
        if recursion_level == 0:
            print_formatted_text(f'\033[1m{os.path.basename(dir)}\033[0m')
        else:
            print_formatted_text(f'{dir_indent}\033[1m{os.path.basename(directory)}\033[0m')

        # Iterate over every file and sub directory, printing file names
        #   and recursing into sub-directories
        for file in os.listdir(directory):
            new_path = os.path.join(directory, file)
            if os.path.isdir(new_path):
                self.print_directory_listing(new_path, recursion_level + 1, indent, dir_branch, file_branch)
            else:
                print_formatted_text(f'{file_indent}\033[3m{file}\033[0m')

    
