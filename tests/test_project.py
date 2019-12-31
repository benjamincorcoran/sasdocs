import pytest
import pprint


from sasdocs.project import sasProject

test_project = sasProject(r'./tests/samples/')
test_project.generate_documentation(outputDirectory='docs')

