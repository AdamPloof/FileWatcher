from setuptools import setup, find_packages

setup(
    name='WatchAndCopy',
    version='0.0.1',
    packages=find_packages('WatchAndCopy'),
    entry_points={
        'console_scripts': [
            'wac=WatchAndCopy:main',
        ],
    }
)
