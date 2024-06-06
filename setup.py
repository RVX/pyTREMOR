from setuptools import setup

setup(
    name='pyTREMOR',
    version='0.5',
    description='Dependencies for pyTREMOR project',
    author='psy',
    author_email='epsylon@riseup.net',
    install_requires=[
        'datetime',
        'pygame',
        'obspy',
        'tqdm', 
    ],
)
