#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys

from os import path as p

import pkutils

try:
    from setuptools import setup, find_packages
except ImportError:
    from distutils.core import setup, find_packages

PARENT_DIR = p.abspath(p.dirname(__file__))

sys.dont_write_bytecode = True
requirements = sorted(pkutils.parse_requirements("requirements.txt"))
dev_requirements = sorted(pkutils.parse_requirements("dev-requirements.txt"))
readme = pkutils.read("README.md")
module = pkutils.parse_module(p.join(PARENT_DIR, "csv2ofx", "__init__.py"))
license = module.__license__
version = module.__version__
project = module.__title__
description = module.__description__
user = "reubano"

# Setup requirements
setup_require = [r for r in dev_requirements if "pkutils" in r]

setup(
    name=project,
    version=version,
    description=description,
    long_description=readme,
    long_description_content_type="text/markdown",
    author=module.__author__,
    author_email=module.__email__,
    url=pkutils.get_url(project, user),
    download_url=pkutils.get_dl_url(project, user, version),
    packages=find_packages(exclude=["docs", "tests"]),
    include_package_data=True,
    package_data={
        "data": ["data/*"],
        "helpers": ["helpers/*"],
        "tests": ["tests/*"],
        "docs": ["docs/*"],
        "examples": ["examples/*"],
    },
    install_requires=requirements,
    setup_requires=setup_require,
    test_suite="nose.collector",
    tests_require=dev_requirements,
    license=license,
    zip_safe=False,
    keywords=[project] + description.split(" "),
    classifiers=[
        pkutils.get_license(license),
        pkutils.get_status(version),
        "Natural Language :: English",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3 :: Only",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: Implementation :: CPython",
        "Programming Language :: Python :: Implementation :: PyPy",
        "Environment :: Console",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Intended Audience :: Developers",
        "Operating System :: POSIX :: Linux",
        "Operating System :: MacOS :: MacOS X",
        "Operating System :: Microsoft :: Windows",
    ],
    platforms=["MacOS X", "Windows", "Linux"],
    scripts=[p.join("bin", "csv2ofx")],
)
