#!/usr/bin/env python3
"""
Setup script for ROBOTY - Multi-robot trajectory planning system
"""

from setuptools import setup, find_packages
import os

# Read the README file
def read_readme():
    with open("README.md", "r", encoding="utf-8") as fh:
        return fh.read()

# Read requirements
def read_requirements():
    with open("ROBOTY/requirements.txt", "r", encoding="utf-8") as fh:
        return [line.strip() for line in fh if line.strip() and not line.startswith("#")]

setup(
    name="roboty",
    version="1.0.0",
    author="ROBOTY Team",
    author_email="roboty@example.com",
    description="Multi-robot trajectory planning system with collision detection and visualization",
    long_description=read_readme(),
    long_description_content_type="text/markdown",
    url="https://github.com/skofer/roboty",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Intended Audience :: Science/Research",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
    python_requires=">=3.8",
    install_requires=read_requirements(),
    extras_require={
        "dev": [
            "pytest>=6.0",
            "pytest-cov>=2.0",
            "black>=21.0",
            "flake8>=3.8",
            "mypy>=0.800",
        ],
    },
    entry_points={
        "console_scripts": [
            "roboty=ROBOTY.main:main",
        ],
    },
    include_package_data=True,
    package_data={
        "ROBOTY": [
            "data/*.json",
            "data/*.txt",
            "ui_files/*.ui",
        ],
    },
    keywords="robotics, trajectory, planning, multi-robot, collision-detection, visualization",
    project_urls={
        "Bug Reports": "https://github.com/skofer/roboty/issues",
        "Source": "https://github.com/skofer/roboty",
        "Documentation": "https://github.com/skofer/roboty#readme",
    },
)
