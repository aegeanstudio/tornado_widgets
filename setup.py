# -*- coding: UTF-8 -*-

from setuptools import setup, find_packages


package = 'tornado_widgets'
version = '0.0.0'


def valid_requirement(line):
    if not line:
        return False
    else:
        ch = line[0]
        return ch not in ('#', '-')


def parse_requirements(filename):
    """ load requirements from a pip requirements file """
    from os.path import dirname, realpath, join as path_join

    root = dirname(realpath(__file__))
    line_iter = (line.strip() for line in open(path_join(root, filename)))
    return [line for line in line_iter if valid_requirement(line)]


setup(
    name=package,
    version=version,
    description='Easier Tornado Web Application Development',
    url='https://github.com/aegean/tornado_widgets',
    packages=find_packages(),
    install_requires=parse_requirements('requirements.txt'),
    entry_points={
        'console_scripts': [],
    },
    maintainer='AeGean Studio',
    maintainer_email='wyqsmith@aegeanstudio.com',
)
