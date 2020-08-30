from setuptools import setup
from pathlib import Path

readme = open(Path(__file__).parent / 'README.md', encoding='utf8').read()

setup(
    name = 'PiIR',
    version = '0.1',
    description = 'IR remote control for Raspberry Pi',
    long_description = readme,
    long_description_content_type = 'text/markdown',
    author = 'Takeshi Sone',
    author_email = 'takeshi.sone@gmail.com',
    install_requires = ['pigpio'],
    python_requires = '~= 3.6',
    url = 'https://github.com/ts1/PiIR',
    license = 'MIT',
    packages = ['piir'],
    #scripts=['bin/piir'],
    entry_points = {
        'console_scripts': ['piir=piir.cli:main'],
    },
    tests_require = ['pytest'],
    setup_requires = ['pytest-runner'],
)
