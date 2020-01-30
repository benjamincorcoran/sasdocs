import os 
import sphinx
from docutils.parsers import rst

from .program import sasProgram

__version__ = 0.01

class SASParser(rst.Parser):
    supported = ['sas_program']

    def parse(self, inputstring, document):
        parsedDoc = sasProgram(document.current_source)
        rst.Parser.parse(self, "Another\n^^^^^^^", document)

        

def setup(app):
    app.add_source_suffix('.sas','sas_program')
    app.add_source_parser(SASParser)

    app.add_config_value('sasdocs_execute', 'auto', rebuild='env')
    app.add_config_value('sasdocs_kernel_name', '', rebuild='env')
    app.add_config_value('sasdocs_execute_arguments', [], rebuild='env')
    app.add_config_value('sasdocs_allow_errors', False, rebuild='')
    app.add_config_value('sasdocs_timeout', 30, rebuild='')
    app.add_config_value('sasdocs_codecell_lexer', 'none', rebuild='env')


    return {
        'version': __version__,
        'parallel_read_safe': True,
        'parallel_write_safe': True,
        'env_version': 2,
    }

