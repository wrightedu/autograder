from setuptools import setup, find_packages
import pathlib

README = (pathlib.Path(__file__).parent / "README.md").read_text()

setup(
    name='wsu-autograder',
    version='1.0.1',
    description='An intelligent autograder tool written and used by the Wright State University CECS department',
    long_description=README,
    long_description_content_type='text/markdown',
    url='https://github.com/wrightedu/autograder',
    author='WSU CECS, Owen O\'Connor',
    author_email='cse-support@wright.edu',
    license='MIT',
    packages=find_packages(),
    entry_points={
        'console_scripts': ['autograder=WSUAutograder._utils:autograder']
    },
    classifiers=[
        'License :: OSI Approved :: MIT License',
        'Development Status :: 4 - Beta',
        'Environment :: Console',
        'Intended Audience :: Education',
        'Natural Language :: English',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 3 :: Only',
        'Topic :: Education :: Computer Aided Instruction (CAI)'
    ],
    install_requires=[
        'binaryornot',
        'lark-parser',
        'Pygments',
        'tqdm'
    ],
    keywords='grading, automation, wright state university',
    zip_safe=False
)