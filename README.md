<img src="https://static.vecteezy.com/system/resources/previews/000/422/489/large_2x/vector-documents-icon.jpg" width=100 title="SASDocumentationLogo" alt="SASDocumentationLogo"> 

# sasdocs

*A small python library to generate rich documentation from SAS code*

[![Build Status](https://travis-ci.com/benjamincorcoran/sasdocs.svg?branch=master)](https://travis-ci.com/benjamincorcoran/sasdocs) [![Documentation Status](https://readthedocs.org/projects/sasdocs/badge/?version=latest)](https://sasdocs.readthedocs.io/en/latest/?badge=latest) [![Commits](https://img.shields.io/github/last-commit/benjamincorcoran/sasdocs.svg)](https://GitHub.com/benjamincorcoran/) [![Coveralls github branch](https://img.shields.io/coveralls/github/benjamincorcoran/sasdocs/master)](https://coveralls.io/github/benjamincorcoran/sasdocs?branch=master)

This library relies on the [parsy](https://pypi.org/project/parsy/) parsing library to parse SAS code and generate python objects representing SAS concepts. 

The library also allows for these objects to be converted into readable documentation using [sphinx](https://pypi.org/project/Sphinx/).

## Installation

```shell 
$ pip install git+https://github.com/benjamincorcoran/sasdocs
``` 
or clone this repository and pip install locally.
```shell
$ git clone https://github.com/benjamincorcoran/sasdocs
$ pip install ./sasdocs
```

## Documentation 
Complete documentation available at [ReadTheDocs.io](https://sasdocs.readthedocs.io/en/latest/index.html) 

## Usage

This module can be used as part of a python project to explore static SAS code, or in tandem with sphinx to autogenerate documentation from SAS code. 

### Simple Example 

In the tests/samples folder in this repository there are three .sas files.
```
├───samples
│       macro_1.sas
│       macro_2.sas
│       simple_1.sas
```
Using the below code, we can generate a SASProject object that will collect all of these files and parse them.
```python
from sasdocs.project import sasProject

prj = sasProject("./tests/samples")
```
This `prj` instance now contains several attributes that can be used to describe the project and in the individual programs contained within.
```python
print(prj.name)
>> "samples"

print(prj.programs)
>> [macro_1.sas, macro_2.sas, simple_1.sas]

print(prj.summary)
>> {'dataStep': 7, 'macro': 4, 'include': 2, 'procedure': 3}
```

### Sphinx directives

Any .rst file in your source directory can call the sasinclude directive which will parse the passed SAS file or all SAS files found in the folder and return the result at the point that the directive is called.

```rst
.. This will parse sasprogram1.sas and return the result.
.. sasinclude:: ..\sasprograms\sasprogram1.sas

.. This will parse all programs in the ..\sasprograms directory and return the results here.
.. sasinclude:: ..\sasprograms\
```

## Contributors

**Ben Corcoran** - 2019 

[![Ask Me Anything !](https://img.shields.io/badge/Ask%20me-anything-1abc9c.svg)](https://GitHub.com/benjamincorcoran/ama) [![Follow](https://img.shields.io/github/followers/benjamincorcoran.svg?label=Follow)](https://GitHub.com/benjamincorcoran/)


## License

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
