import pytest
import pprint
import pathlib
import jinja2 

from sasdocs.project import sasProject

test_project = sasProject(r'./tests/samples/')
test_project.generate_documentation()

for key, value in test_project.documentation.items():
    print(key, value.keys())