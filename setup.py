from setuptools import setup, find_packages

setup(
    name='auto-tracking-cctv-rpi',
    version='1.0',
    packages=find_packages(),
    entry_points={
        'console_scripts': [
            'run-cctv-rpi = rpi.__main__:main'
        ]
    }
)
