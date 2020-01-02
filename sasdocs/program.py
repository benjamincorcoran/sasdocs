import os
import datetime 
import logging
import pathlib

from collections import Counter

from . import format_logger
from .objects import fullprogram, force_partial_parse



class sasProgram(object):
    """
    Abstracted SAS program class.
    ...

    Attributes
    ----------
    path : pathlib.Path
        File path to the source of the SAS program
    contents : list
        List of parsed sasdocs.objects found in the program
    failedLoad : int
        Flag if there was a failure to load/parse the program file
    raw : str
        Raw string version of the program file
    parsedRate : float
        Percentage of the program file successfully parsed 
    """

    def __init__(self, path):

        self.path = path
        self.logger = logging.getLogger(__name__)
        try: 
            self.logger = format_logger(self.logger,{'path':self.path})
        except Exception as e:
            self.logger.error("Unable to format log. {}".format(e))
        
        if self.load_file(path) is False:
            self.contents = []
            self.failedLoad = 1
        else:
            self.failedLoad = 0

    def load_file(self, path):
        """
        load_file(path)

        Attempt to load the given path and parse into a sasProgram object. Errors logged on failure
        to resolve path, read file and parse. 

        Sets values of path, raw, contents and parsed rate if successful. 

        Parameters
        ----------
        path : str
            Filepath to the SAS file to be parsed.
        """
        try:
            self.path = pathlib.Path(path).resolve()
        except Exception as e:
            self.logger.error("Unable to resolve path: {}".format(e))
            return False
            
        try:
            with open(self.path,'r') as f :
                self.raw = f.read()
        except Exception as e:
            self.logger.error("Unable to read file: {}".format(e))
            return False

        try:
            self.contents, self.parsedRate = force_partial_parse(fullprogram, self.raw, stats=True)
        except Exception as e:
            self.logger.error("Unable to parse file: {}".format(e))
            return False

    def get_objects(self, object=None, objectType=None):
        """
        get_objects(object=None, objectType=None)

        Recursively loop through parsed objects in the programs contents, yielding each object. If the object 
        is a macro object, enter and yield sas objects found in the macro's contents. 

        This function will never return a macro object. 

        If passed with optional objectType, this function will only yield objects of type equal to objectType. 

        Parameters
        ----------
        object : None, macro 
            Recursion parameter, if none loop through self.contents else loop through object.contents
        objectType : str
            If not none, only yield objects where the object is of type objectType.
        
        Yields
        ------
        sasdocs.object 
        """
        if object is None:
            object = self
        for obj in object.contents:
            if type(obj).__name__ == 'macro':
                yield from self.get_objects(obj, objectType=objectType)
            elif objectType is not None:
                if type(obj).__name__ == objectType:
                    yield obj
            else:
                yield obj

    def summarise_objects(self, object=None):
        """
        summarise_objects(object=None)

        Recursively loop through parsed objects in the programs contents, counting each object by object type.
        This function will count macros and the contents of said macros.

        Parameters
        ----------
        object : None, macro 
            Recursion parameter, if none loop through self.contents else loop through object.contents
        
        Returns
        -------
        Counter
            Collections Counter object for all sasdoc.object types found in program.
        """
        if object is None:
            object = self
        counter = Counter(type(obj).__name__ for obj in object.contents)
        for obj in object.contents:
            if type(obj).__name__ == 'macro':
                counter += self.summarise_objects(obj)
        return counter

    def get_extended_info(self):
        """
        get_extended_info()

        Creates dictionary containing extended information about the parsed SAS code. 
        
        .. code-block:: rst

            name : Filename of the SAS code,
            path : Full path to the SAS code,
            lines : Number of lines in the SAS code,
            lastEdit : Timestamp for the last edit of the SAS code,
            summary : Counter object returned by summarise_objects,
            parsed : Percentage of the SAS code succesfully parsed
            


        Returns
        -------
        dict
            A dictionary containing extended information about the SAS program

        """
        return {
            'name': os.path.splitext(os.path.basename(self.path))[0],
            'path': self.path,
            'lines': self.raw.count('\n'),
            'lastEdit': "{:%Y-%m-%d %H:%M}".format(datetime.datetime.fromtimestamp(os.stat(self.path).st_mtime)),
            'summary': dict(self.summarise_objects()),
            'parsed': "{:.2%}".format(self.parsedRate)
        }
    
    def __repr__(self):
        return os.path.basename(self.path)



