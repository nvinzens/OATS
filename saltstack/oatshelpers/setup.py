from setuptools import setup, find_packages

setup(name='oatshelpers',
      version='0.11',
      description='Helper functions for the OATS System',
      url='http://github.com/rjoehl',
      author='Raphael Joehl',
      author_email='rjoehl@hsr.ch',
      license='',
      packages=find_packages(exclude=('tests', 'docs'))
)