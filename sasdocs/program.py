import os
import datetime 
import logging
import pathlib
import jinja2

from collections import Counter
import importlib.resources as pkg_resources

from . import templates
from .objects import fullprogram, force_partial_parse


log = logging.getLogger(__name__) 

class sasProgram(object):
    """
    Abstracted SAS program class.
    
    This class represents a .sas program file. Initialised with a valid file path 
    to the .sas file, the parser will then parse any valid SAS object it can find 
    within the file and return them to a list in the contents attribute. 

    The percentage of complete parsing will also be stored in the parsedRate attribute. 

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
        
        if self.load_file(path) is False:
            self.contents = []
            self.failedLoad = 1
        else:
            self.failedLoad = 0
            self.get_extended_info()
            self.get_documentation()

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
            self.path = pathlib.Path(path).resolve(strict=True)
        except Exception as e:
            self.path = pathlib.Path(path)
            log.error("Unable to resolve path: {}".format(e))
            return False
            
        try:
            with open(self.path,'r') as f :
                self.raw = f.read()
        except Exception as e:
            log.error("Unable to read file: {}".format(e))
            return False

        try:
            self.contents, self.parsedRate = force_partial_parse(fullprogram, self.raw, stats=True, mark=True)
        except Exception as e:
            log.error("Unable to parse file: {}".format(e))
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
                if objectType == 'macro':
                    yield obj
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

        Creates class attributes for extended information about the parsed SAS code. 
        
        .. code-block:: rst

            name : Filename of the SAS code,
            path : Full path to the SAS code,
            lines : Number of lines in the SAS code,
            lastEdit : Timestamp for the last edit of the SAS code,
            summary : Counter object returned by summarise_objects,
            parsed : Percentage of the SAS code succesfully parsed
        """
        
        self.name = self.path.stem
        self.lines = self.raw.count('\n')
        self.lastEdit = "{:%Y-%m-%d %H:%M}".format(datetime.datetime.fromtimestamp(os.stat(self.path).st_mtime))
        self.summary = dict(self.summarise_objects())
        self.parsed = "{:.2%}".format(self.parsedRate)
    

    def get_documentation(self):
        cmnts = []
        for obj in self.contents:
            if type(obj).__name__ == 'comment':
                cmnts.append(obj)
            else:
                break
        if len(cmnts) == 0:
            self.documentation = 'No documentation found.'
            self.documented = False
        else:
            self.documentation = '\n'.join([comment.text for comment in cmnts])
            self.documented = True
    
    def generate_documentation(self):
        """
        generate_documentation

        Generate documentation for the program using the jinja2 template

        Returns
        -------
        str
            jinja2 templated version of this program

        """

        template = jinja2.Template(pkg_resources.read_text(templates, 'program.md'))
        return template.render(program=self)


    def __repr__(self):
        return self.path.name



