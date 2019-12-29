import pytest
import pprint
import pathlib
import jinja2 

from sasdocs.project import sasProject


def write_to_markdown(project, outdir=None):
    
    if outdir is None:
        outdir = project.path.joinpath('docs')
    else:
        outdir = pathlib.Path(outdir)
    
    outdir.mkdir(exist_ok=True)

    templates = {path.stem:path for path in pathlib.Path(r'./sasdocs/templates').glob('*.tplt')}
    for key, path in templates.items():
        with path.open() as f:
            templates[key] = jinja2.Template(f.read())

    outdir.joinpath('project.md').write_text(templates['project'].render(project=project))
    for program in project.programs:
        outdir.joinpath(program.name+'.md').write_text(templates['program'].render(program=program))




test_project = sasProject(r'./tests/samples/')
write_to_markdown(test_project)