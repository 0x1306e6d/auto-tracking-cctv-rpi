from setuptools import setup, find_packages

setup(
    name='auto-tracking-cctv-rpi',
    version='1.0',
    packages=find_packages(),
    install_requires=[
        'picamera',
    ],
    entry_points={
        'console_scripts': [
            'run-cctv-rpi = rpi.startup:start_from_command_line'
        ]
    }
)
