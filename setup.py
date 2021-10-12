from setuptools import setup, find_packages

setup(
    name='watch-and-copy',
    version='0.0.1',
    packages=find_packages('WatchAndCopy'),
    entry_points={
        'console_scripts': [
            'wac=WatchAndCopy.WatchAndCopy:main',
        ],
    }
)
