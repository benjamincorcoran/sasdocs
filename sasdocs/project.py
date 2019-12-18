import os
import datetime 
import logging
import pathlib

from collections import Counter
from .program import sasProgram

log = logging.getLogger(__name__) 

class sasProject(object):

    def __init__(self, path):

        self.programs = []
        if self.load_project(path) is False:
            return None

    def load_project(self, path):
        try:
            self.path = pathlib.Path(path).resolve()
        except Exception as e:
            log.error("Unable to resolve path: {}".format(e))
            return False

        try: 
            programPaths = self.path.glob('**/*.sas')
        except Exception as e:
            log.error("Unable to search folder: {}".format(e))
            return False
        
        try: 
            self.add_programs_to_project(programPaths)
        except Exception as e:
            log.error("Unable to add programs to project: {}".format(e))
            return False
        
    def add_programs_to_project(self, programPaths):
        for path in programPaths:
            if path not in [program.path for program in self.programs]:
                self.programs.append(sasProgram(path))
        
        includePaths = set(include.path for include in self.get_objects(objectType='include'))
        while includePaths.difference(set([program.path for program in self.programs])):
            for path in includePaths:
                self.programs.append(sasProgram(path))
            includePaths = set(include.path for include in self.get_objects(objectType='include'))
        
        self.programs = [program for program in self.programs if program.failedLoad != 1]

    
    def summarise_project(self):
        objectCounter = Counter()
        programCounter = dict()
        for program in self.programs:
            cnt = program.summarise_objects()
            objectCounter += cnt
            programCounter[program] = dict(cnt)
        return objectCounter, programCounter
         
    def get_objects(self, objectType=None):
        for program in self.programs:
            yield from program.get_objects(objectType=objectType)

    def get_extended_info(self):
        objSum, prgSum = self.summarise_project()
        return {
            'name': os.path.basename(self.path),
            'path': self.path,
            'programs': len(self.programs),
            'summary': dict(objSum),
            'objects': dict(prgSum)
        }
                
                



