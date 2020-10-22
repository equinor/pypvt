# coding: utf-8

import pathlib

from setuptools import setup


# Read the contents of README.md, for PyPI
with open(pathlib.Path(__file__).resolve().parent / "README.md") as f_handle:
    LONG_DESCRIPTION = f_handle.read()

REQUIREMENTS = ["ecl2df", "pandas", "scipy", "numpy", "matplotlib"]

SETUP_REQUIREMENTS = ["setuptools >=28", "setuptools_scm"]

TESTS_REQUIRES = [
    "pylint~=2.3",
    "black",
    "bandit",
    "mypy",
    "pytest",
]

setup(
    name="pypvt",
    description=(
        "Generate, perfrom consistency testing and perturb initialization "
        "of Eclipse reservoir simulator decs with respect to pvt"
    ),
    long_description=LONG_DESCRIPTION,
    long_description_content_type="text/markdown",
    url="http://github.com/equinor/pypvt",
    author="Knut Uleberg, Eivind Smørgrav, Wouter J. de Bruin, Anders Kiær",
    author_email="kule@equinor.com",
    license="LGPLv3",
    keywords="pvt, fluid contacts, initailization, reservoir simulation",
    classifiers=[
        "Development Status :: 1 - Planning",
        "License :: OSI Approved :: GNU Lesser General Public License v3 or later (LGPLv3+)",
        "Natural Language :: English",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Topic :: Scientific/Engineering",
    ],
    packages=["pypvt"],
    entry_points={
        "console_scripts": [
            "pypvt=pypvt._cli:main",
        ]
    },
    python_requires="~=3.6",
    zip_safe=False,
    install_requires=REQUIREMENTS,
    setup_requires=SETUP_REQUIREMENTS,
    tests_require=TESTS_REQUIRES,
    extras_require={"tests": TESTS_REQUIRES},
    use_scm_version=True,
)
