from __future__ import print_function
from setuptools import setup, find_packages
from setuptools.command.test import test as TestCommand
import io
import os
import sys

import klaatu

here = os.path.abspath(os.path.dirname(__file__))


def read(*filenames, **kwargs):
    encoding = kwargs.get('encoding', 'utf-8')
    sep = kwargs.get('sep', '\n')
    buf = []
    for filename in filenames:
        with io.open(filename, encoding=encoding) as f:
            buf.append(f.read())
    return sep.join(buf)

# long_description = read('README.txt', 'CHANGES.txt')

long_description = 'ADD LONG DESCRIPTION'


class PyTest(TestCommand):
    def finalize_options(self):
        TestCommand.finalize_options(self)
        self.test_args = []
        self.test_suite = True

    def run_tests(self):
        import pytest

        errcode = pytest.main(self.test_args)
        sys.exit(errcode)


setup(
    name='klaatu',
    version=klaatu.__version__,
    url='http://github.com/choderalab/robots/klaatu',
    license='Apache Software License',
    author='John D. Chodera, Sonya Hanson, Jan-Hendrik Prinz, Bas Rustenberg',
    tests_require=['pytest'],
    install_requires=[
    ],
    cmdclass={'test': PyTest},
    author_email='jan.prinz@choderalab.org',
    description='Collection of python libraries to control various parts of the robot',
    long_description=long_description,
    packages=['klaatu'],
    include_package_data=True,
    platforms='any',
    test_suite='klaatu.test.test_klaatu',
    classifiers=[
        'Programming Language :: Python',
        'Development Status :: 4 - Beta',
        'Natural Language :: English',
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: Apache Software License',
        'Operating System :: OS Independent',
        'Topic :: Software Development :: Libraries :: Python Modules',
    ],
    extras_require={
        'testing': ['pytest'],
    }
)
