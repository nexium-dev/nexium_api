from os import getenv

from dotenv import load_dotenv
from setuptools import setup, find_packages


load_dotenv()
NAME = getenv('NAME')
VERSION = getenv('VERSION')
DESCRIPTION = getenv('DESCRIPTION')
AUTHOR = getenv('AUTHOR')
AUTHOR_EMAIL = getenv('AUTHOR_EMAIL')
LICENSE = getenv('LICENSE')
URL = getenv('URL')


README_REPLACE = {
    '🧡': '♡',
}


def parse_requirements(filename: str) -> list[str]:
    with open(filename, 'r') as f:
        return [line.strip() for line in f if line.strip() and not line.startswith('#')]


def get_long_description() -> str:
    with open('README.md', encoding='utf-8') as file:
        long_description = file.read()
    for key, value in README_REPLACE.items():
        long_description = long_description.replace(key, value)
    return long_description


setup(
    name=NAME,
    version=VERSION,
    description=DESCRIPTION,
    author=AUTHOR,
    author_email=AUTHOR_EMAIL,
    url=URL,
    packages=find_packages(),
    long_description=get_long_description(),
    long_description_content_type='text/markdown',
    license=LICENSE,
    install_requires=parse_requirements('requires.txt'),
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.11',
)

