import os 
import m2r
import sphinx

from docutils.parsers import rst
from docutils import nodes, statemachine
from sphinx.util.docutils import SphinxDirective 

from shutil import copyfile

import importlib.resources as pkg_resources

from .program import sasProgram
from .project import sasProject

from . import sphinxStatic

__version__ = 0.01

class SASDirective(SphinxDirective):
    
    has_content = True
    required_arguments = 1
    optional_arguments = 0
    final_argument_whitespace = False

    def run(self):
        sasfile = self.arguments[0]
        srcpath = os.path.normpath(os.path.join(self.env.srcdir,sasfile))

        if os.path.splitext(sasfile)[1].lower() == '.sas':
            parsedSAS = m2r.convert(sasProgram(srcpath).generate_documentation())
            self.state_machine.insert_input(parsedSAS.split('\n'), '')
            return []
        else:
            parsedSAS = sasProject(srcpath)
            for prg in parsedSAS.programs:
                documentation = m2r.convert(prg.generate_documentation())
                self.state_machine.insert_input(documentation.split('\n'), '')
            return []



class SASParser(rst.Parser):
    supported = ['sas_program']

    def parse(self, inputstring, document):
        parsedSAS = sasProgram(document.current_source)
        mdDocumentation = parsedSAS.generate_documentation()
        rst.Parser.parse(self, m2r.convert(mdDocumentation), document)
   

def setup(app):
    app.add_source_suffix('.sas','sas_program')
    app.add_source_parser(SASParser)
    app.add_directive('sasinclude', SASDirective)

    with pkg_resources.path(sphinxStatic, 'd3.v5.js') as p:
        copyfile(str(p), os.path.join(app.srcdir,'_static','d3.v5.js'))
        app.add_js_file('d3.v5.js')
    with pkg_resources.path(sphinxStatic, 'network.js') as p:
        copyfile(str(p), os.path.join(app.srcdir,'_static','network.js'))
        app.add_js_file('network.js')
    with pkg_resources.path(sphinxStatic, 'codemirror.js') as p:
        copyfile(str(p), os.path.join(app.srcdir,'_static','codemirror.js'))
        app.add_js_file('codemirror.js')
    with pkg_resources.path(sphinxStatic, 'codemirrorSAS.js') as p:
        copyfile(str(p), os.path.join(app.srcdir,'_static','codemirrorSAS.js'))
        app.add_js_file('codemirrorSAS.js')
    with pkg_resources.path(sphinxStatic, 'networkStyle.css') as p:
        copyfile(str(p), os.path.join(app.srcdir,'_static','networkStyle.css'))
        app.add_css_file('networkStyle.css')
    with pkg_resources.path(sphinxStatic, 'codemirrorStyle.css') as p:
        copyfile(str(p), os.path.join(app.srcdir,'_static','codemirrorStyle.css'))
        app.add_css_file('codemirrorStyle.css')

    

    return {
        'version': __version__,
        'parallel_read_safe': True,
        'parallel_write_safe': True,
        'env_version': 2,
    }

