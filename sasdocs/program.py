import os
import json
import datetime 
import logging
import pathlib
import jinja2
import networkx
import importlib.resources as pkg_resources

from collections import Counter

from . import templates, format_logger
from .objects import force_partial_parse
from .parsers import fullprogram


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

        self.path = path
        self.logger = logging.getLogger(__name__)
        try: 
            self.logger = format_logger(self.logger,{'path':self.path})
        except Exception as e:
            self.logger.exception("Unable to format log. {}".format(e))
        
        if self.load_file(path) is False:
            self.contents = []
            self.failedLoad = 1
        else:
            self.failedLoad = 0
            self.get_extended_info()
            self.parse_code_documentation()
            self.get_data_objects()
            self.build_network()

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
            self.logger.error("Unable to resolve path: {}".format(e))
            return False
            
        try:
            with open(self.path,'r') as f :
                self.raw = f.read()
        except Exception as e:
            self.logger.exception("Unable to read file: {}".format(e))
            return False

        try:
            self.contents, self.parsedRate = force_partial_parse(fullprogram, self.raw, stats=True, mark=True)
        except Exception as e:
            self.logger.exception("Unable to parse file: {}".format(e))
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
    
    def get_data_objects(self):
        """
        get_data_objects

        Loop through all datasteps and procedures and add any valid dataobjects
        to a list self.dataObjects
        """
        self.dataObjects = {}

        for validObject in ('dataStep', 'procedure'):
            for proc in self.get_objects(objectType=validObject):
                for dataset in proc.inputs + proc.outputs:
                    if dataset.UID not in self.dataObjects.keys():
                        self.dataObjects[dataset.UID] = [{'obj':dataset, 'start':proc.start, 'end':proc.end}]
                    else:
                        self.dataObjects[dataset.UID].append({'obj':dataset, 'start':proc.start, 'end':proc.end})    

    def build_network(self):
        """
        build_network

        Generate a JSON containing the network diagram for the SAS code and add to class variable self.networkJSON
        Add class varaible self.hasNodes containing a bool as to whether this code contains any valid data objects.
        """

        self.networkGraph = networkx.DiGraph()

        for validObject in ('dataStep','procedure'):
            for obj in self.get_objects(objectType=validObject):

                for input in obj.inputs:
                    if self.networkGraph.has_node(input.UID) is False:
                        self.networkGraph.add_node(input.UID, library=input.library, dataset=input.dataset, line=obj.start[0])
                    
                    for output in obj.outputs:
                        if self.networkGraph.has_node(output.UID) is False:
                            self.networkGraph.add_node(output.UID, library=output.library, dataset=output.dataset, line=obj.start[0])
                        
                        if input.UID != output.UID:
                            if hasattr(obj,'type'):
                                self.networkGraph.add_edge(input.UID, output.UID, label=f'proc {obj.type}')
                            else:
                                self.networkGraph.add_edge(input.UID, output.UID)


        network = networkx.readwrite.json_graph.node_link_data(self.networkGraph)
        self.hasNodes = len(network['nodes']) > 0    
        self.networkJSON = json.dumps(network)



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
        self.nameURL = self.name.replace(' ','%20')
        self.lines = self.raw.count('\n')
        self.lastEdit = "{:%Y-%m-%d %H:%M}".format(datetime.datetime.fromtimestamp(os.stat(self.path).st_mtime))
        self.summary = dict(self.summarise_objects())
        self.parsed = "{:.2%}".format(self.parsedRate)
    

    def parse_code_documentation(self):
        """
        parse_code_documentation 

        Generate class variables self.documentation and self.documented containing the first set of 
        comments in the SAS program. 

        self.documentation: str 
            The first parsed comments.

        self.documented: bool
            True if the first object parsed in the SAS code is a comment. 

        """
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
    
    def generate_documentation(self, template='program.md'):
        """
        generate_documentation

        Generate documentation for the program using the jinja2 template

        Returns
        -------
        str
            jinja2 templated version of this program

        """

        template = jinja2.Template(pkg_resources.read_text(templates, template))
        return template.render(program=self)


    def __repr__(self):
        return self.path.name



