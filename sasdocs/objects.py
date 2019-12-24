import os
import pathlib
import logging
import attr
import re
import parsy as ps

log = logging.getLogger(__name__) 


def rebuild_macros(objs, i=0):
    '''
    Recursively generate macro objects from macroStart & macroEnd objects in 
    processed list

    Parameters
    ----------
    objs : list 
        list of sas objects
    i : int
        recursive safe loop variable

    Returns
    -------
    list
        parsed objects from string
    '''
    output = []
    while i < len(objs):
        obj = objs[i]
        if type(obj) == macroEnd:
            return (macro(name=output[0].name, arguments=output[0].arguments, contents=output[1:]), i)
        elif type(obj) != macroStart or (type(obj) == macroStart and len(output)==0) :
            output.append(obj)
        else:
            _, i = rebuild_macros(objs,i=i)
            output.append(_)
        i+=1
    
    return output, i


def force_partial_parse(parser, string, stats=False):
    """Force partial parse of string skipping unparsable characters
    
    Parameters
    ----------
    parser : parsy.parser
        parsy valid parsing object
    string : str
        String to be parsed
    stats : bool
        Return percentage parsed if true

    Returns
    -------
    list
        parsed objects from string"""
    if isinstance(string, str):
        parsed = []
        olen = len(string)
        skips = 0
        while len(string) > 0:
            partialParse, string = parser.parse_partial(string)
            if len(partialParse) == 0:
                string = string[1:]
                skips += 1
            else:
                parsed += partialParse
        
        # print("Parsed: {:.2%}".format(1-(skips/olen)))
        parsed = rebuild_macros(parsed)[0]
        if type(parsed) == list:
            ret = [p for p in parsed if p != '\n']
        else:
            ret = [parsed]
        if stats:
            return (ret, (1-skips/olen))
        else:
            return ret
    else:
        return []

# SAS object classes 
# Class objects are roughly equivalent to abstracted SAS concepts
# as such they are 
#     - macroVariable
#     - macroVariableDefinition
#     - comment
#     - dataObject (a reference to any dataobject within the code)
#     - dataStep
#     - procedure
#     - libname
#     - include

@attr.s
class macroVariable:
    """
    Abstracted python class to reference the SAS macro variable.
    ...

    Attributes
    ----------
    variable : str
        Macro variable reference as used in SAS code
    """
    variable = attr.ib()

@attr.s
class comment:
    """
    Abstracted python class to reference the SAS comment.
    ...

    Attributes
    ----------
    text : str
        Text contained between SAS comment delimiters delimiters
    """
    text = attr.ib()

@attr.s
class macroVariableDefinition:
    """
    Abstracted python class for the definition and assignment of macro varaibles.
    ...

    Attributes
    ----------
    variable : str
        Macro variable reference as used in SAS code
    value : str
        Unparsed value contained in the macro variable
    """
    variable = attr.ib()
    value = attr.ib()

@attr.s 
class include:
    """
    Abstracted python class for %include statements in SAS code.
    ...

    Attributes
    ----------
    path : str
        Hardcoded path used in the %include statement

    """
    path = attr.ib()
    @path.validator
    def check_path_is_valid(self, attribute, value):
        """
        check_path_is_valid(attribute, value)

        Set the value of path if parsed path is valid.

        Parameters
        ----------
        attribute : str
        value : str

        Returns
        -------
        None
        """
        try:
            self.path = pathlib.Path(value).resolve()
        except Exception as e:
            log.error("Unable to resolve path: {}".format(e))


@attr.s
class dataArg:
    """
    Abstracted python class for option applied inline to a data object.

    Attributes
    ----------
    option : str
        Inline data argument being set
    settings : str
        Value passed to the inline data arguement
    """
    option = attr.ib()
    setting = attr.ib(default=None, repr=False)


@attr.s(repr=False)
class dataObject:
    """
    Abstracted python class for data objects created and used by SAS datasteps and procedures.
    ...

    Attributes
    ----------
    library : str or list 
        Library in which the data is stored
    dataset : str or list
        Name used to reference the dataset in the code
    options : [dataArg]
        Options applied to the dataset at a particular point 
    name : str
        String of the form 'library.dataset'
    UID : str
        Upcased version of 'library.datastep', data object's unique identifier
    """
    library = attr.ib()
    dataset = attr.ib()
    options = attr.ib(default=None)

    def __attrs_post_init__(self):
        if self.library is None:
            self.library = 'work'
        
        if type(self.library) == list:
            _lib = ''.join([s if type(s) != macroVariable else s.variable for s in self.library])
        else:
            _lib = self.library
        
        if type(self.dataset) == list:
            _ds = ''.join([s if type(s) != macroVariable else s.variable for s in self.dataset])
        else:
            _ds = self.dataset

        self.name = (_lib + '.' + _ds)
        self.UID = self.name.upper()
        
    def __repr__(self):
        return self.name
    def __str__(self):
        return self.name

@attr.s
class dataStep:
    """
    Abstracted python class for parsing datasteps.
    ...

    Attributes
    ----------
    outputs : list 
        List of dataObjects the datastep outputs
    inputs : list
        List of dataObjects the datastep takes as inputs
    header : str 
        Any code between the end of the 'data ;' statement and the begining of the 'set/merge ;' statement
    name : str
        Any code between the end of the 'set/merge ;' statement and the 'run;' statement
    """
    outputs = attr.ib()
    inputs = attr.ib()
    header = attr.ib(repr=False, default=None)
    body = attr.ib(repr=False, default=None)

@attr.s
class procedure:
    """
    Abstracted python class for parsing procedures.
    ...

    Attributes
    ----------
    outputs : list 
        List of dataObjects the datastep outputs
    inputs : list
        List of dataObjects the datastep takes as inputs
    type : str
        Procedure type i.e. sort/tranpose/summary
    """
    outputs = attr.ib()
    inputs = attr.ib()
    type = attr.ib()
    
@attr.s 
class libname:
    """
    Abstracted python class for libname statements.
    ...

    Attributes
    ----------
    library : str
        libname reference as used in SAS code
    path : str, optional
        Hardcoded path pointing to library on disk
    pointer : str, optional
        Libname reference if current libname is pointing to an already established library

    """
    library = attr.ib()
    path = attr.ib()
    pointer = attr.ib(default=None)
    @path.validator
    def check_path_is_valid(self, attribute, value):
        """
        check_path_is_valid(attribute, value)

        Set the value of path if parsed path is valid.

        Parameters
        ----------
        attribute : str
        value : str

        Returns
        -------
        None
        """
        try:
            if self.path is not None:
                self.path = pathlib.Path(value).resolve()
        except Exception as e:
            log.error("Unable to resolve path: {}".format(e))

@attr.s
class macroStart:
    """
    Abstracted python class for flagging start of %macro definition
    ...

    Attributes
    ----------
    name : str 
        Name of the %macro being defined
    arguements : list, optional
        List of macroarguement objects as defined
    """
    name = attr.ib()
    arguments = attr.ib()

@attr.s
class macroEnd:
    """
    Abstracted python class for flagging end of %macro definition
    ...

    Attributes
    ----------
    text : str
        Dummy variable.
    """
    text = attr.ib()


@attr.s
class macroargument:
    """
    Abstracted python class for parsing a macro arguement defintion
    ...

    Attributes
    ----------
    arg : str 
        Name of the arguement
    default : str, optional
        Default value of the argument
    doc : str, optional
        Documentation comment for the arguement
    """
    arg = attr.ib()
    default = attr.ib()
    doc = attr.ib()

@attr.s
class macro:
    """
    Abstracted python class for SAS macro
    ...

    Attributes
    ----------
    name : str 
        Name of the marco
    arguements : list, optional
        List of macroarguments parsed from the macro defintion
    contents : list
        List of sasdocs objects parsed within the macro
    """
    name = attr.ib()
    arguments = attr.ib()
    contents = attr.ib(repr=False)

    def __attrs_post_init__(self):
        self.contents = [obj for obj in self.contents if obj != '\n']


# Parsy Objects
# Define reFlags as ignorecase and dotall to capture new lines
reFlags = re.IGNORECASE|re.DOTALL

# Basic Objects
# Basic and reused parsy objects referencing various recurring 
# regex objects

# Word: 1 or more alphanumeric characters
wrd = ps.regex(r'[a-zA-Z0-9_-]+')
# FilePath: String terminating in a quote (used only for include and libname)
fpth = ps.regex(r'[^\'"]+')

# Whitespace and Optional whitespace
spc = ps.regex(r'\s+')
opspc = ps.regex(r'\s*')

# Dot and optional dot
dot = ps.string('.')
opdot = ps.string('.').optional().map(lambda x: '' if x is None else x)

# Common identifiers
nl = ps.string('\n')
eq = ps.string('=')
col = ps.string(';')
amp = ps.string('&')
lb = ps.string('(')
rb = ps.string(')')
star = ps.string('*')
cmm = ps.string(',')

anycharacter = ps.regex(r'.', flags=reFlags)

# Multiline comment entry and exit points
comstart = ps.string(r'/*')
comend = ps.string(r'*/')

# Quotes
qte = ps.string('"') | ps.string("'")

# Common SAS keywords
run = ps.regex(r'run',flags=re.IGNORECASE)
qt = ps.regex(r'quit',flags=re.IGNORECASE)


# Basic SAS Objects

# Macrovariable: ampersand + word + optional dot
_mcv = (amp + wrd + opdot) 
mcv = (_mcv | amp + _mcv + _mcv).map(macroVariable)

# Inline comment: start + commentry + semicolon
inlinecmnt = star >> ps.regex(r'[^;]+') << col
# Multiline comment: Commentary start + commentry + Commentry end
multicmnt = comstart >> ps.regex(r'.+?(?=\*\/)', flags=reFlags) << comend

# Either inline or multiline comment, mapped to comment object
cmnt = (inlinecmnt|multicmnt).map(comment)

# Complex SAS Objects
# sasName: Any named object in SAS, can contain macrovariable as part of name
sasName = (wrd|mcv).many()

# Marcovariable definition:
mcvDef = ps.seq(
    variable =ps.regex(r'%let',flags=reFlags) + spc + opspc >> sasName << opspc + eq,
    value = ps.regex(r'[^;]+', flags=reFlags).optional(),
    _col = col
).combine_dict(macroVariableDefinition)

# datalineArg: Argument in dataline sasName = (setting)
# e.g. where=(1=1)
datalineArg = ps.seq(
    option = sasName << (opspc + eq + opspc), 
    setting = lb + ps.regex(r'[^)]*') + rb
).combine_dict(dataArg)

# datalineOptions: Seperate multiple datalineArgs by spaces
datalineOptions = lb >> (datalineArg|sasName).sep_by(spc) << rb

# dataObj: Abstracted data object exists as three components:
#   - library: sasName before . if . exists
#   - dataset: sasName after . or just sasName required
#   - options: dataLineOptions is present

dataObj = ps.seq(
    library = (sasName << dot).optional(),
    dataset = dot >> sasName | sasName,
    options = datalineOptions.optional()
).combine_dict(dataObject)

# dataLine: Multiple dataObjs seperated by space
dataLine = dataObj.sep_by(spc)

# datastep: Abstracted form of datastep process has four components:
#   - outputs: dataline existing directly after "data"
#   - header: anything between outputs and set/merge statment
#   - inputs: dataline directly after set/merge statement
#   - body: anything between inputs and "run"
# terminating run is thrown away

datastep = ps.seq(
    outputs = (ps.regex(r'data', flags=re.IGNORECASE) + spc) >> dataLine << col,
    header = ps.regex(r'.*?(?=set|merge)', flags=reFlags),
    inputs = (opspc + ps.regex(r'set|merge',flags=re.IGNORECASE) + opspc) >> dataLine << col,
    body = ps.regex(r'.*?(?=run)', flags=reFlags),
    _run = run + opspc + col
).combine_dict(dataStep)

# proc: Abstracted form of all procedure statements, has three components:
#   - type: capture procedure type directly after "proc"
#   - inputs: capture single dataObj after "data="
#   - outputs: capture single dataObj after "out="
# throw away an other excess

proc = ps.seq(
    type = (ps.regex(r'proc', flags=re.IGNORECASE) + spc) >> wrd << spc,
    _h1 = ps.regex(r'.*?(?=data)', flags=reFlags),
    inputs = (ps.regex(r'data', flags=re.IGNORECASE) + opspc + eq + opspc) >> dataObj,
    _h2 = ps.regex(r'.*?(?=out\s*=)', flags=reFlags).optional(),
    outputs = ((ps.regex(r'out', flags=re.IGNORECASE) + opspc + eq + opspc) >> dataObj).optional(),
    _h3 = ps.regex(r'.*?(?=run|quit)', flags=reFlags),
    _run = (run|qt) + opspc + col
).combine_dict(procedure)

# lbnm: Abstracted libname statement, three components:
#   - library: name of library reference in code 
#   - path: filepath of the library if given 
#   - pointer: name of library reference pointed to if given

lbnm = ps.seq(
    library = (ps.regex(r'libname', flags=re.IGNORECASE) + spc) >> sasName << spc,
    path = (opspc + qte >> fpth << opspc + qte + col).optional(),
    pointer = (opspc + lb + opspc >> sasName << opspc + rb + opspc + col).optional()
).combine_dict(libname)

# icld: Abstracted include statement, one component:
#   - path: file path to the included code 
icld = ps.seq(
    path = (ps.regex(r'%include', flags=re.IGNORECASE) + spc + opspc + qte) >> fpth << (qte + opspc + col),
).combine_dict(include)

# program: Multiple SAS objects in any order
program = (nl|mcvDef|cmnt|datastep|proc|lbnm|icld).many()


mcroarg = ps.seq(
    arg = sasName << opspc,
    default = (eq + opspc >> sasName).optional(),
    doc = cmnt.optional()
).combine_dict(macroargument)

mcroargline = lb + opspc >> mcroarg.sep_by(opspc+cmm+opspc) << opspc + rb




mcroStart = ps.seq(
    name = ps.regex(r'%macro',flags=re.IGNORECASE) + spc + opspc >> sasName,
    arguments = (opspc >> mcroargline).optional() << opspc + col 
).combine_dict(macroStart)

mcroEnd = (ps.regex(r'%mend.*?;',flags=re.IGNORECASE)).map(macroEnd)

# fullprogram: multiple SAS objects including macros
fullprogram =  (nl|mcvDef|cmnt|datastep|proc|lbnm|icld|mcroStart|mcroEnd).many()



