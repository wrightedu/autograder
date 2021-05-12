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
        self.directory = directory
        self.language = language

        self.src_bin_present = path.isdir(path.join(directory, 'src')) and path.isdir(path.join(directory, 'bin'))
        self.src_dir = 'src' if self.src_bin_present else ''
        self.bin_dir = 'bin' if self.src_bin_present else ''

        self._command = None
        self._args = args


    def compile(self):
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
        source_directory = path.join(self.directory, self.src_dir)

        if 'makefile' in (i.lower() for i in os.listdir(source_directory)):
            result = subprocess.run('make', capture_output=True, cwd=source_directory)
            if result.returncode == 0:
                return True

        return False


    def _compile_java(self):
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
        # TODO Somehow add support for compiling c/c++ code automatically...
        print('Automatically detecting and compiling c/c++ code is not easy. Makefiles are recommended')
        return False


    # Scripts don't get compiled, so all that this has to do is copy them over if necessary
    def _compile_scripts(self):
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


    def find_main_executable(self):
        potential_executables = []

        for dir_name, _, file_list in os.walk(path.join(self.directory, self.bin_dir)):
            for fname in file_list:
                file_path = path.join(dir_name, fname)
                if _is_executable(file_path, self.language):
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
        executable_extension = path.splitext(executable_path)[-1]
        relative_path = path.relpath(executable_path, self.directory)

        if self.language == 'java':
            if executable_extension == '.jar':
                self._command = ('java', '-jar', relative_path, *self._args)

            elif executable_extension == '.class':
                self._command = ('java', '-cp', self.bin_dir, relative_path[-6], *self._args)

        elif self.language == 'python':
            self._command = ('python', relative_path, *self._args)

        elif self.language in ['bash', 'shell', 'sh']:
            self._command = ('bash', relative_path, *self._args)

        else:
            self._command = (f'./{relative_path}', *self._args)


    def _is_executable(self, file_name):
        extension = path.splitext(file_name)[-1]
        if os.access(path, os.X_OK) or extension == '.exe':
            return True

        if self.language == 'java' and extension in ['.class', '.jar']:
            return True

        if self.language == 'python' and extension in ['.py']:
            return True

        if self.language in ['bash', 'shell', 'sh'] and extension in ['.sh', '.bash']:
            return True

        return self.language in ['c', 'cpp', 'c++'] and extension in [''] and is_binary(file_name)


    def run_tests(self, tests, timeout=5):
        self._results = []

        for test in tqdm(tests):
            program_pipe = subprocess.Popen(self._command, stdin=subprocess.PIPE, stdout=subprocess.PIPE)
            program_pipe.stdin.write(test['input'].encode('utf-8'))
            program_pipe.stdin.close()

            if program_pipe.wait(timeout) is None:
                program_pipe.terminate()

            test_output = program_pipe.stdout.read().decode('utf-8')
            exit_code = program_pipe.returncode
            self._results.append((test_output, exit_code))


    def set_command(self, command):
        self._command = command


    def set_main_executable(self, executable_path):
        self.generate_command(executable_path)


    def print_source_files(self, directory = None):
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

    
