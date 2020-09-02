# -*- coding: UTF-8 -*-

import os
from setuptools import setup, find_packages


_REQUIRES_PATH = os.path.join(
    os.path.dirname(os.path.abspath(__file__)), 'requires')


def _read_requires(filename):
    with open(file=os.path.join(_REQUIRES_PATH, filename), mode='r') as f:
        line_iter = (line.strip() for line in f.readlines())
    return [line for line in line_iter
            if line and (line[0] not in ('#', '-'))]


REQUIREMENTS = _read_requires(filename='requirements.in')

EXTRAS_REQUIRE = dict(
    postgres=_read_requires(filename='postgres.in'),
    mysql=_read_requires(filename='mysql.in'),
    redis=_read_requires(filename='redis.in'),
    influxdb=_read_requires(filename='influxdb.in'),
)


setup(
    name='tornado_widgets',
    use_scm_version=True,
    description='Easier Tornado Web Application Development',
    author='AeGean-Studio',
    author_email='wyqsmith@aegeanstudio.com',
    url='https://github.com/AeGean-Studio/tornado_widgets',
    license='BSD',
    packages=find_packages(exclude=('tests*', 'example*')),
    install_requires=REQUIREMENTS,
    extras_require=EXTRAS_REQUIRE,
    setup_requires=['setuptools_scm'],
    python_requires='>=3.6',
    classifiers=[
        'License :: OSI Approved :: BSD License',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3 :: Only',
    ],
)
