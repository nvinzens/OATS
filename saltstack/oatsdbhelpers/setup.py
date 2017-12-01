from setuptools import setup, find_packages

setup(name='oatsdbhelpers',
      version='0.1.01',
      description='Helper functions for OATS, includes db access functions which require MongoDB ',
      url='http://github.com/rjoehl',
      author='Raphael Joehl, Nico Vinzens',
      author_email='rjoehl@hsr.ch',
      license='',
      packages=find_packages(exclude=('tests', 'docs'))
)