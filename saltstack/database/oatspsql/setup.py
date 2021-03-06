from setuptools import setup, find_packages

setup(name='oatspsql',
      version='0.1.01',
      description='Helper functions for OATS, which require PostgreSQL ',
      url='http://github.com/rjoehl',
      author='Raphael Joehl, Nico Vinzens',
      author_email='rjoehl@hsr.ch',
      license='',
      packages=find_packages(exclude=('tests', 'docs'))
)
