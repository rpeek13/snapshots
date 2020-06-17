from setuptools import setup

setup(
    name='snapshots-cli',
    version='0.1',
    summary='Snapshots-CLI is a tool to manage AWS EC2 snapshots',
    author='riley peek',
    author_email='riley.s.peek@gmail.com',
    license='GPLv3+',
    packages=['snapshots'],
    url='https://github.com/rpeek13/snapshots',
    install_requires=[
        'click',
        'boto3'
        'datetime'
    ],
    entry_points='''
        [console_scripts]
        snapshots=snapshots.snapshots:cli
    ''',
)
