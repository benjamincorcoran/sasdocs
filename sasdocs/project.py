import os
import datetime 
import logging
import pathlib

from collections import Counter
from .program import sasProgram

log = logging.getLogger(__name__) 

class sasProject(object):
    """
    Abstracted SAS project class.

    A SAS project is a collection of individual SAS programs that combine, 
    use the same library, include each other, or generally create datasets used by 
    each other in such away that they can be considered largly part of the same piece
    of work. 
    ...

    Attributes
    ----------
    path : pathlib.Path
        File path to the root directory of the project
    programs : [sasProgram]
        List of parsed .sas programs found in the project root or subfolders
    macroVariables : [macroVariableDefinition]
        List of all macro variable defintions found in all programs in the project
    """

    def __init__(self, path):
        self.programs = []
        if self.load_project(path) is False:
            return None
        
        self.get_extended_info()

    def load_project(self, path):
        """
        load_project(path)

        Search the given path recursively to find all .sas files, then generate sasProgram objects
        from any valid sas programs found. 

        Sets values of path and programs. 

        Parameters
        ----------
        path : str
            The root file path of the project .
        """
        try:
            self.path = pathlib.Path(path).resolve(strict=True)
        except Exception as e:
            log.error("Unable to resolve path: {}".format(e))
            return False

        try: 
            programPaths = self.path.rglob('*.sas')
        except Exception as e:
            log.error("Unable to search folder: {}".format(e))
            return False
        
        try: 
            self.add_programs_to_project(programPaths)
        except Exception as e:
            log.error("Unable to add programs to project: {}".format(e))
            return False
        
        # self.macroVariables = {d.variable:d.value for d in self.get_objects(objectType='macroVariableDefinition')}
        
    def add_programs_to_project(self, programPaths):
        """
        add_programs_to_project(programPaths)

        For a list of found paths to .sas files in the project directory, generate sasProgram objects. If any sasProgram
        objects contain an include object, where possible follow the path in the %include statement, parse file and add to 
        the project's programs list. 

        Does not parse the program if the path has already been visited.

        Parameters
        ----------
        programPaths : list
            List of discovered program paths in the project's directories.

        """
        for path in programPaths:
            if path not in [program.path for program in self.programs]:
                self.programs.append(sasProgram(path))
        
        # includePaths = set(include.path for include in self.get_objects(objectType='include'))
        # while includePaths.difference(set([program.path for program in self.programs])):
        #     for path in includePaths:
        #         self.programs.append(sasProgram(path))
        #     includePaths = set(include.path for include in self.get_objects(objectType='include'))
        
        self.programs = [program for program in self.programs if program.failedLoad != 1]
    
    def summarise_project(self):
        """
        summarise_objects()

        Recursively loop through parsed objects in the project's programs, counting each object by object type.
        This function will count macros and the contents of said macros.

        Returns
        -------
        ObjCounter : Counter
            Collections Counter object for all sasdoc.object types found in all programs in the project.
        ProgramCount : dict
            Dictionary containing a object Counter for each program found in the project 
        """
        objectCounter = Counter()
        programCounter = dict()
        for program in self.programs:
            cnt = program.summarise_objects()
            objectCounter += cnt
            programCounter[program] = dict(cnt)
        return objectCounter, programCounter
         
    def get_objects(self, objectType=None):
        """
        get_objects(objectType=None)

        Recursively loop through parsed programs in the project, yielding each sasdocs object. If the object 
        is a macro object, enter and yield sas objects found in the macro's contents. 

        This function will never return a macro object. 

        If passed with optional objectType, this function will only yield objects of type equal to objectType. 

        Parameters
        ----------
        objectType : str
            If not none, only yield objects where the object is of type objectType.
        
        Yields
        ------
        sasdocs.object 
        """
        for program in self.programs:
            yield from program.get_objects(objectType=objectType)

    def get_extended_info(self):
        """
        get_extended_info

        Creates class attributes for information about the SAS project. 
        
        .. code-block:: rst

            name : Filename of the SAS code,
            path : Full path to the SAS code,
            programs : Number of programs found in the project,
            summary : Counter object returned by summarise_objects,
            objects : Dictionary of Counter objects indexed by program 
            
        """
        objSum, prgSum = self.summarise_project()
        
        self.name = os.path.basename(self.path)
        self.nPrograms = len(self.programs)
        self.summary = dict(objSum)
        self.objects = dict(prgSum)
