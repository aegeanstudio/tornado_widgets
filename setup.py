# -*- coding: UTF-8 -*-

from setuptools import setup, find_packages


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
    name='tornado_widgets',
    use_scm_version=True,
    description='Easier Tornado Web Application Development',
    author='AeGean-Studio',
    author_email='wyqsmith@aegeanstudio.com',
    url='https://github.com/AeGean-Studio/tornado_widgets',
    license='BSD',
    packages=find_packages(exclude=('tests*', 'example*')),
    install_requires=parse_requirements('requirements.txt'),
    setup_requires=['setuptools_scm'],
    python_requires='>=3.6',
)
