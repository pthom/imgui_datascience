#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""The setup script."""

from setuptools import setup, find_packages

with open('README.rst') as readme_file:
    readme = readme_file.read()

with open('HISTORY.rst') as history_file:
    history = history_file.read()

requirements = [ ]

setup_requirements = ['pytest-runner', ]

test_requirements = ['pytest', ]

setup(
    author="Pascal Thomet",
    author_email='pthomet@gmail.com',
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: Apache Software License',
        'Natural Language :: English',
        "Programming Language :: Python :: 2",
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
    ],
    package_data={
        '': ['*.ttf', 'images/*.jpg', 'images/*.png'],
    },
    description="A set of utilities for data science using python, imgui, numpy and opencv",
    install_requires=['imgui', 'opencv-python', 'imgui[pygame]', 'pyopengl', 'matplotlib','pygame', 'enum34', 'xxhash'],
    license="Apache Software License 2.0",
    long_description="""

A set of utilities for data science using python, imgui, numpy and opencv

Features
========

View the full demo (1'50") on youtube: 

https://www.youtube.com/watch?v=qstEZyLGsTQ&feature=youtu.be    

Run it after install:

python -m imgui_datascience --example


Display numpy.ndarray (aka opencv image)
----------------------------------------

The following types are supported : RGB, RGBA, GRAY, float32, float64

Display matplotlib figures
--------------------------

Inspect images
--------------
- show pixels color (or float values)
- adjust visibility for float images
- save images
- zoom & pan (with possible sync between 2 images)
    """,

    include_package_data=True,
    keywords='imgui_datascience',
    name='imgui_datascience',
    packages=find_packages(include=['imgui_datascience']),
    entry_points={
          'console_scripts': [
              'my_project = my_project.__main__:main'
          ]
    },
    setup_requires=setup_requirements,
    test_suite='tests',
    tests_require=test_requirements,
    url='https://github.com/pthom/imgui_datascience',
    version='0.2.7',
    zip_safe=False,
)
