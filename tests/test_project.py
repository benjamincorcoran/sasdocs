import pytest
import pprint


from sasdocs.project import sasProject

test_project = sasProject(r'S:\HESA AP Student\2017-18\Data checking tool\Code\Live')
test_project.generate_documentation(outputDirectory='W:\docs')

