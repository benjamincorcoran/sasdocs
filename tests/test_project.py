import pytest
import pprint
import jinja2 as ji

from sasdocs.project import sasProject


def write_to_markdown(project):
    with open('./sasdocs/templates/project.tplt', 'r') as f:
        tmplt = f.read()

    t = ji.Template(tmplt)

    with open('./tests/samples/output.md', 'w') as f:
        f.write(t.render(project=test_project))



test_project = sasProject(r'./tests/samples/')
for x in test_project.get_objects(objectType='macro'):
    print(x)

write_to_markdown(test_project)