import os 
import logging

from .objects import fullprogram, force_partial_parse

log = logging.getLogger(__name__) 


class sasProgram(object):

    def __init__(path):
       
        try:
            self.path = os.path.abspath(path)
        except Exception as e:
            log.ERROR("Unable to resolve path: {}".format(e))
            return None
       
        try:
            with open(self.path,'r') as f :
                self.raw = f.read()
        except Exception as e:
            log.ERROR("Unable to read file: {}".format(e))

        try:
            self.contents = force_partial_parse(fullprogram, self.raw)
        except Exception as e:
            log.ERROR("Unable to parse file: {}".format(e))