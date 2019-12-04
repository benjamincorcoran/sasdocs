from setuptools import setup, find_packages


def readme():
    with open('README.md') as f:
        return f.read()


NAME = 'sasdocs'
VERSION = '1.0.dev0'
DESCRIPTION = 'A tool for analysising and documenting SAS code.'
LONG_DESCRIPTION = readme()
AUTHOR = 'Ben Corcoran'

with open('requirements.txt') as f:
    INSTALL_REQUIRES = f.read().splitlines()


setup(name=NAME,
      version=VERSION,
      description=DESCRIPTION,
      long_description=LONG_DESCRIPTION,
      author=AUTHOR,
      packages=find_packages(),
      install_requires=INSTALL_REQUIRES,
      include_package_data=True,
      zip_safe=False)
