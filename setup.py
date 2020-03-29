import os
import re

from setuptools import setup, find_packages


def get_version():
    """Extract and return version number from the packages '__init__.py'."""
    init_path = os.path.join('forecast_api', '__init__.py')
    content = read_file(init_path)
    match = re.search(r"__version__ = '([^']+)'", content, re.M)
    version = match.group(1)
    return version


def read_requirements(filename):
    """Open a requirements file and return list of its lines."""
    contents = read_file(filename).strip('\n')
    return contents.split('\n') if contents else []


def read_file(filename):
    """Open and a file, read it and return its contents."""
    path = os.path.join(os.path.dirname(__file__), filename)
    with open(path) as f:
        return f.read()


install_requires = read_requirements('requirements.txt')
tests_require = read_requirements('requirements_dev.txt')

setup(
    name='forecast_api',
    version=get_version(),
    author='Andrew Smith',
    author_email='dr.andrew.c.smith@gmail.com',
    description='forecast_api',
    long_description=read_file('README.rst'),
    url='https://github.com/drandrewcsmith/forecast_api',
    install_requires=install_requires,
    tests_require=tests_require,
    classifiers=[
        'Intended Audience :: Developers',
        'Natural Language :: English',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3.6',
    ],
    packages=find_packages(
        exclude=["*.tests", "*.tests.*", "tests.*", "tests"]),
    include_package_data=True,
    zip_safe=False,
)
