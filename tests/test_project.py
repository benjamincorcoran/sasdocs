import pytest
import pprint
import pathlib
import jinja2 

from sasdocs.project import sasProject

test_project = sasProject(r'./tests/samples/')
test_project.write_to_markdown()