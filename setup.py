#!/usr/bin/env python3

from setuptools import find_packages, setup

with open("README.md", "r") as fh:
    long_description = fh.read()

setup(
    name="RaiseWikibase",
    version='1.35.0-wmde.0',
    author="Renat Shigapov, Joerg Mechnich, Irene Schumm",
    license="MIT",
    description="RaiseWikibase: Fast inserts into a Wikibase instance",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/UB-Mannheim/RaiseWikibase",
    use_scm_version={"local_scheme": "no-local-version"},
    setup_requires=['setuptools_scm'],
    install_requires=[
    "matplotlib>=3.0.2",
    "mysqlclient>=2.0.3",
    "numpy>=1.16.2",
    "pandas>=1.2.2",
    "requests>=2.21.0",
    "seaborn>=0.11.1",
    ],
    scripts=['miniWikibase.py','megaWikibase.py','performance.py'],
    packages=find_packages(),
    classifiers=[
	"License :: OSI Approved :: MIT License",
        "Intended Audience :: Developers",
	"Intended Audience :: Education",
        "Intended Audience :: Science/Research",
	"Operating System :: OS Independent",
	"Programming Language :: Python",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
	"Topic :: Software Development :: Libraries",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
    python_requires='>=3.6',
)
