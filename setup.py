# coding: utf-8

from os import path
import sys
from setuptools import setup, find_packages


# Read the contents of README.md, for PyPI
this_directory = path.abspath(path.dirname(__file__))
with open(path.join(this_directory, "README.md")) as f_handle:
    LONG_DESCRIPTION = f_handle.read()


def parse_requirements(filename):
    """Load requirements from a pip requirements file"""
    try:
        lineiter = (line.strip() for line in open(filename))
        return [line for line in lineiter if line and not line.startswith("#")]
    except IOError:
        return []


REQUIREMENTS = parse_requirements("requirements.txt")
SETUP_REQUIREMENTS = ["pytest-runner", "setuptools >=28", "setuptools_scm"]

setup(
    name="pypvt",
    version="0.0.1",
    description=(
        "Generate, perfrom consistency testing and perturb initialization of Eclipse reservoir simulator decs with respect to pvt"
    ),
    long_description=LONG_DESCRIPTION,
    long_description_content_type="text/markdown",
    url="http://github.com/equinor/pypvt",
    author="Knut Uleberg, Eivind Smørgrav, Wouter J. de Bruin",
    author_email="kule@equinor.com",
    license="LGPLv3",
    keywords="pvt, fluid contacts, initailization, reservoir simulation",
    classifiers=[
        "Development Status :: 0 - Beta",
        "License :: OSI Approved :: GNU Lesser General Public License v3 or later (LGPLv3+)",
        "Natural Language :: English",
        "Programming Language :: Python :: 2",
        "Programming Language :: Python :: 2.7",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.6",
    ],
    packages=['pypvt'],
    zip_safe=False,
    install_requires=REQUIREMENTS,
    setup_requires=SETUP_REQUIREMENTS,
)
