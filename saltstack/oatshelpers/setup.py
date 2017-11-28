from setuptools import setup, find_packages

setup(name='oatshelpers',
      version='0.11',
      description='Helper functions for OATS, includes db access functions which require MongoDB ',
      url='http://github.com/rjoehl',
      author='Raphael Joehl, Nico Vinzens',
      author_email='rjoehl@hsr.ch',
      license='',
      packages=find_packages(exclude=('tests', 'docs'))
)