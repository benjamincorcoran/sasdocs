import os
import datetime 
import logging
import pathlib

from collections import Counter

from .objects import fullprogram, force_partial_parse, procedure, macro

log = logging.getLogger(__name__) 


class sasProgram(object):

    def __init__(self, path):

        if self.load_file(path) is None:
            return None
        

    def load_file(self, path):
        try:
            self.path = pathlib.Path(path).resolve()
        except Exception as e:
            log.error("Unable to resolve path: {}".format(e))
            return None
       
        try:
            with open(self.path,'r') as f :
                self.raw = f.read()
        except Exception as e:
            log.error("Unable to read file: {}".format(e))
            return None

        try:
            self.contents, self.parsedRate = force_partial_parse(fullprogram, self.raw, stats=True)
            self.get_extended_info()
        except Exception as e:
            log.error("Unable to parse file: {}".format(e))
            return None

    def get_objects(self, object=None):
        if object == None:
            object = self
        for obj in object.contents:
            if type(obj).__name__ == 'macro':
                yield from self.get_objects(obj)
            else:
                yield obj 

    def summarise_objects(self, object=None):
        if object == None:
            object = self
        counter = Counter(type(obj).__name__ for obj in object.contents)
        for obj in object.contents:
            if type(obj).__name__ == 'macro':
                counter += self.summarise_objects(obj)
        return counter


    def get_extended_info(self):
        self.extendedInfo = {
            'name': os.path.splitext(os.path.basename(self.path))[0],
            'path': self.path,
            'lines': self.raw.count('\n'),
            'lastEdit': "{:%Y-%m-%d %H:%M}".format(datetime.datetime.fromtimestamp(os.stat(self.path).st_mtime)),
            'summary': dict(self.summarise_objects()),
            'parsed': "{:.2%}".format(self.parsedRate)
        }



