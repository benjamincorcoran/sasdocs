import os
import pathlib
import logging
import attr
import re
import parsy as ps

log = logging.getLogger(__name__) 

def flatten_list(aList):
    '''
    Recursively dig through a list flattening all none list
    objects into a single list. 

    Parameters
    ----------
    aList : list 
        List of nested lists and objects to be flattened
    
    Returns
    -------
    list
        Flattened list containing all objects found in aList
    '''
    rt = []
    for item in aList:
        if not isinstance(item, list):
            rt.append(item)
        else:
            rt.extend(flatten_list(item))
    return rt


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
        if len(output) > 0 and type(output[0]) == macroStart and type(obj) == macroEnd:
            return (macro(ref=output[0].name, arguments=output[0].arguments, contents=output[1:]), i)
        elif type(obj) != macroStart or (type(obj) == macroStart and len(output)==0) :
            output.append(obj)
        else:
            _, i = rebuild_macros(objs,i=i)
            output.append(_)
        i+=1
    
    return output, i


def force_partial_parse(parser, string, stats=False, mark=False):
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
    if mark:
        parser = parser.mark()
    if isinstance(string, str):
        parsed = []
        olen = len(string)
        skips = 0
        lastPosistion = (1, 0)

        while len(string) > 0:
            partialParse, string = parser.parse_partial(string)
            
            if mark:
                start, obj, end = partialParse
                start = [sum(x) for x in zip(start, lastPosistion)]
                if end[0] == 0:
                    lastPosistion = [sum(x) for x in zip(end, lastPosistion)]
                else:
                    lastPosistion = [end[0]+lastPosistion[0], end[1]]
            else:
                obj = partialParse

            if obj is None:
                string = string[1:]
                skips += 1
                lastPosistion = [lastPosistion[0], lastPosistion[1]+1]
            else:
                if mark and not isinstance(obj,str):
                    if isinstance(obj,list):
                        for x in obj:
                            x.set_found_posistion(start,lastPosistion)
                    else:
                        obj.set_found_posistion(start,lastPosistion)
                
                parsed.append(obj)
                
        
        # print("Parsed: {:.2%}".format(1-(skips/olen)))
        flattened = flatten_list(parsed)
        parsed = rebuild_macros(flattened)[0]
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
class baseSASObject:
    """
    Base object containing general functions used by all SAS objects
    """

    def set_found_posistion(self, start, end):
        """
        set_found_posistion(start, end)

        Set the start and end attributes for the object. Used during 
        force_partial_parse with mark=True to grab where in the SAS
        program the object appears. 

        Parameters
        ----------
        start : tuple 
            The start line:char tuple for the object 
        end : tuple 
            The end line:char tuple for the objet 
        """
        self.start = start
        self.end = end


@attr.s
class macroVariable(baseSASObject):
    """
    Abstracted python class to reference the SAS macro variable.

    This class recongises SAS code in the form `&variableName.` or `&variableName`
    where the variable name 'varaibleName' is stored in the object's variable attribute.

    Attributes
    ----------
    variable : str
        Macro variable reference as used in SAS code
    """
    variable = attr.ib()

@attr.s
class comment(baseSASObject):
    """
    Abstracted python class to reference the SAS comment.

    This class recognises SAS code in either of the below forms and stores
    any texts stored between the comment delimiters in the object's text
    attribute.

    .. code-block:: sas

        /* Comment text */
        * Comment text;
    
    Attributes
    ----------
    text : str
        Text contained between SAS comment delimiters delimiters
    """
    text = attr.ib()

@attr.s
class macroVariableDefinition(baseSASObject):
    """
    Abstracted python class for the definition and assignment of macro varaibles.
    
    This class recognises SAS `%let` statements and parses the reference variable and 
    the value assigned to it in to the objects variable and value attributes respectively. 

    For example

    .. code-block:: sas

        %let var = 1
        %let var&i. = 1

    Will be parsed into 

    .. code-block:: python

        macroVariableDefinition(variable='var', value='1')
        macroVariableDefinition(variable=['var',macroVariable(variable='i')], value='1')

    Attributes
    ----------
    variable : str or list
        Macro variable reference as used in SAS code
    value : str or list
        Unparsed value contained in the macro variable
    """
    variable = attr.ib()
    value = attr.ib()

@attr.s 
class include(baseSASObject):
    """
    Abstracted python class for %include statements in SAS code.

    This class recognises SAS `%include` statements and parses the path assigned to it in to the objects 
    path. 

    For example

    .. code-block:: sas

        %include "C:/SASCode/Example1.sas"

    Attributes
    ----------
    path : str
        Hardcoded path used in the %include statement

    """
    path = attr.ib()
    uri = ''
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
            self.path = pathlib.Path(value).resolve(strict=True)
            self.uri = self.path.as_uri()
        except Exception as e:
            self.path = pathlib.Path(value)
            log.warning("Unable to directly resolve path: {}".format(e))


@attr.s
class dataArg(baseSASObject):
    """
    Abstracted python class for an argument applied to a dataset in SAS.

    This class recognises inline arguments applied to datasets in SAS code. In the 
    below example this object would pull out the option `where` with the setting
    `A=1`.

    .. code-block:: sas

        data test(where=(A=1));
        ...
    
    This object is created for each argument in an inline statement and passed to the 
    dataObject options attribute. 

    Attributes
    ----------
    option : str
        Inline data argument being set
    settings : str
        Value passed to the inline data argument
    """
    option = attr.ib()
    setting = attr.ib(default=None, repr=False)


@attr.s(repr=False)
class dataObject(baseSASObject):
    """
    Abstracted python class for data objects created and used by SAS datasteps and procedures.

    This object represents a dataset, as referenced within the SAS code. In the below example
    there are two `dataObjects` referenced, `foo` and `bar`. Both objects would be generated if this 
    code was parsed by a dataStep parser. As `foo` has no specified library, its library attribute 
    will default to 'work'. The bar dataset has an explicit library reference pointing to `lib1`, this will
    be the value stored in the library attribute.
    Any inline options will be parsed into a list and passed to the options attribute. 

    .. code-block:: sas

        data foo;
            set lib1.bar;
        run;
        
    dataObjects have a `name` attribute which is the combination of the library and the datastep names seperated
    by a period. For internal linking they also have a UID attribute which is the upcased version of the name attribute.


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
class dataStep(baseSASObject):
    """
    Abstracted python class for parsing datasteps
    
    This object represents a datastep process in SAS. In the below example the dataset `foo` is 
    passed to the object's output attribute, as parsed into a dataobject object. The dataset bar 
    is parsed into the inputs attribute. 

    Any addition code, between foo; and the set/merge statment will be saved into the header attribute 
    and similarly any further code between the end of the set/merge statement and the end of the 
    datastep will be parsed into the body attribute. Both the header and body remain as unparsed strings.

    .. code-block:: sas

        data foo;
            set lib1.bar;
        run;

    Attributes
    ----------
    outputs : list 
        List of dataObjects the datastep outputs
    inputs : list
        List of dataObjects the datastep takes as inputs
    header : str 
        Any code between the end of the 'data ;' statement and the begining of the 'set/merge ;' statement
    body : str
        Any code between the end of the 'set/merge ;' statement and the 'run;' statement
    """
    outputs = attr.ib()
    inputs = attr.ib()
    header = attr.ib(repr=False, default=None)
    body = attr.ib(repr=False, default=None)

@attr.s
class procedure(baseSASObject):
    """
    Abstracted python class for parsing procedures.

    This object parses a SAS procedure (except proc sql) into inputs, outputs and the type of procedure. 
    The type attribute will capture the word directly after the proc indicator. In a similar way to the 
    datastep parser, the foo and bar datasets will be parsed into the input and outputs respectively. 
    
    .. code-block:: sas

        proc sort data=foo out=bar; by A; run;
        proc tranpose data=foo out=bar; by A; var B; run;
        proc summary data=foo; class A; output out=bar; run;


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
    type = attr.ib(default='sql')

    def __attrs_post_init__(self):
        self.outputs=flatten_list([self.outputs])
        self.inputs=flatten_list([self.inputs])

@attr.s
class unparsedSQLStatement(baseSASObject):
    """
    Abstracted class for unparsed SQL statements found in
    proc sql procedures. Only currently parsed statement is
    `create table`, all other statements are parsed into 
    this object

    Attributes
    ----------
    text : str
        Raw SQL code for unparsed statement
    """

    text = attr.ib()

@attr.s 
class libname(baseSASObject):
    """
    Abstracted python class for libname statements.

    This object parses a SAS libname statement into the reference variable used in the SAS 
    code and path it defines. In the example below the object's library attribute is 'lib1' 
    and its path attribute is 'C:/data/'. 

    In the case that the libname points to an already existing library. The value of path is 
    None and the pointer attribute contains the value of the library being pointed to, in the 
    example below the value of pointer would be 'lib1'.

    .. code-block:: sas

        libname lib1 "C:/data/";
        libname lib2 (lib1);


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

    uri = ''
    is_path = False
    is_pointer = False

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
                self.path = pathlib.Path(value).resolve(strict=True)
                self.uri = self.path.as_uri()
                self.is_path = True
        except Exception as e:
            self.is_path = True
            log.warning("Unable to directly resolve path: {}".format(e))
    
    def __attrs_post_init__(self):
        if self.path is None and self.pointer is not None:
            self.is_pointer = True
        



    def __attrs_post_init__(self):
        if self.path is None and self.pointer is not None:
            self.type = 'pointer'
        elif self.path is not None and self.pointer is None:
            self.type = 'path'
        
        self.name = ''.join(self.library)


@attr.s
class macroStart(baseSASObject):
    """
    Flagging class for start of %macro definition

    Attributes
    ----------
    name : str 
        Name of the %macro being defined
    arguments : list, optional
        List of macroargument objects as defined
    """
    name = attr.ib()
    arguments = attr.ib()

@attr.s
class macroEnd(baseSASObject):
    """
    Flagging class for end of %macro definition

    Attributes
    ----------
    text : str
        Dummy variable.
    """
    text = attr.ib()


@attr.s
class macroargument(baseSASObject):
    """
    Abstracted python class for parsing a macro argument defintion.

    This class parses the marco arguments that are definied in the macro 
    definition. The arg attribute contains the local macro variable name. The
    default attribute contains the default value defined for the arguement, if no
    default value is defined then the default attribute is None. Any comments 
    next to the argument definition are parsed and passed to the doc attribute. 

    In the below example, the arg value is 'arg1' and 'arg2', the default values are
    None and 'N' and the doc attributes are 'Arg1 docstring' and 'Arg2 docstring'
    respectively. 
    
    .. code-block:: sas

        %macro run(arg1 /*Arg1 docstring*/, arg2=N /*Arg2 docstring*/);
        ...

    Attributes
    ----------
    arg : str 
        Name of the argument
    default : str, optional
        Default value of the argument
    doc : str, optional
        Documentation comment for the argument
    """
    arg = attr.ib()
    default = attr.ib()
    doc = attr.ib()

@attr.s
class macro(baseSASObject):
    """
    Abstracted python class for SAS macro.
    
    This class parses a SAS macro. In the example below the objects name attribute is
    'run'. The arguments attribute is the parsed arguments defined in the macro variable. The 
    contents attribute is any parseable SAS object found between the end of the `%macro` statement
    and the `%mend` statement. 

    .. code-block:: sas

        %macro run(arg1 /*Arg1 docstring*/, arg2=N /*Arg2 docstring*/);
            data &arg1.;
                set &arg2.; 
            run;
        %mend;
    


    Attributes
    ----------
    name : str 
        Name of the marco
    arguments : list, optional
        List of macroarguments parsed from the macro defintion
    contents : list
        List of sasdocs objects parsed within the macro
    """
    ref = attr.ib()
    arguments = attr.ib()
    contents = attr.ib(repr=False)

    def __attrs_post_init__(self):
        self.name = ''.join(self.ref)
        self.contents = [obj for obj in self.contents if obj != '\n']
        about = []
        for obj in self.contents:
            if type(obj).__name__ == 'comment':
                about.append(obj)
            else:
                break
        if len(about) == 0:
            self.about = 'No docstring found.'
            self.documented = False
        else:
            self.about = '\n'.join([comment.text for comment in about])
            self.documented = True
        


# Parsy Objects
# Define reFlags as ignorecase and dotall to capture new lines
reFlags = re.IGNORECASE|re.DOTALL

# Basic Objects
# Basic and reused parsy objects referencing various recurring 
# regex objects

# Word: 1 or more alphanumeric characters
wrd = ps.regex(r'[a-zA-Z0-9_\-]+')
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
    header = (ps.regex(r'.*?(?=set|merge)', flags=reFlags)).optional(),
    inputs = ((opspc + ps.regex(r'set|merge',flags=re.IGNORECASE) + opspc) >> dataLine << col).optional(),
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

# crtetbl: Parser for create table sql statement

crtetbl = ps.seq(
    outputs = ps.regex(r'create table', flags=reFlags) + opspc >> dataObj.sep_by(opspc+cmm+opspc) <<  opspc + ps.regex(r'as'),
    inputs = (ps.regex(r'[^;]*?from', flags=reFlags) + spc + opspc >> dataObj.sep_by(opspc+cmm+opspc)).many(),
    _h = ps.regex(r'[^;]*?(?=;)', flags=reFlags) + col
).combine_dict(procedure)

# unparsedSQL: Capture currently unparsed SQL statements

unparsedSQL = ps.regex(r'[^;]*?;(?<!quit;)', flags=reFlags).map(unparsedSQLStatement)

# sql: Abstracted proc sql statement, three primary components:
#   - output: Output of the create table statement
#   - inputs Any dataset referenced next to a from statement

sql = ps.regex(r'proc sql', flags=reFlags) + opspc + col + opspc >> (crtetbl|unparsedSQL).sep_by(opspc) << ps.regex(r'.*?quit', flags=reFlags) + opspc + col


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
    default = (eq + opspc >> (ps.regex(r'(?:[a-zA-Z0-9_\-@\.\:]|\/(?!\*)|\\(?!\*))+')|mcv).many()).optional(),
    doc = cmnt.optional()
).combine_dict(macroargument)

mcroargline = lb + opspc >> mcroarg.sep_by(opspc+cmm+opspc) << opspc + rb

mcroStart = ps.seq(
    name = ps.regex(r'%macro',flags=re.IGNORECASE) + spc + opspc >> sasName,
    arguments = (opspc >> mcroargline).optional() << opspc + col 
).combine_dict(macroStart)

mcroEnd = (ps.regex(r'%mend.*?;',flags=re.IGNORECASE)).map(macroEnd)

# fullprogram: multiple SAS objects including macros
fullprogram =  (nl|mcvDef|cmnt|datastep|proc|sql|lbnm|icld|mcroStart|mcroEnd).optional()

