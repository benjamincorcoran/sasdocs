import os
import logging

class codeBlock(object):

    def __init__(self, **kwargs):
        self.enable_logging()
    
    def enable_logging(self):
        self.logger = logging.getLogger(__name__)

class SASFile(codeBlock):

    def __init__(self, file, **kwargs):

        self.enable_logging()
        
        if not os.path.isfile(file):
            self.logger.error('File does not exist: {}'.format(file))
            return None    
        
        self.path = os.path.abspath(file)
        self.fileName = os.path.basename(self.path)



