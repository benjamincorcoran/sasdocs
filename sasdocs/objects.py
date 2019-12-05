import os
import logging
import attr
import re
import parsy as ps

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
    variable = attr.ib()

@attr.s
class macroVariableDefinition:
    variable = attr.ib()
    value = attr.ib()

@attr.s
class comment:
    text = attr.ib()

@attr.s
class dataObject:
    library = attr.ib()
    dataset = attr.ib()
    options = attr.ib(default=None)

@attr.s
class dataStep:
    outputs = attr.ib()
    header = attr.ib()
    inputs = attr.ib()
    body = attr.ib()

@attr.s
class procedure:
    outputs = attr.ib()
    inputs = attr.ib()
    type = attr.ib()
    
@attr.s 
class libname:
    library = attr.ib()
    path = attr.ib()
    pointer = attr.ib(default=None)

@attr.s 
class include:
    path = attr.ib()


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

# Multiline comment entry and exit points
comstart = ps.string(r'/*')
comend = ps.string(r'*/')

# Quotes
qte = ps.string('"') | ps.string("'")

# Common SAS keywords
run = ps.regex('run',flags=re.IGNORECASE)
qt = ps.regex('quit',flags=re.IGNORECASE)


# Basic SAS Objects

# Macrovariable: ampersand + word + optional dot
mcv = (amp + wrd + opdot).map(macroVariable)

# Inline comment: start + commentry + semicolon
inlinecmnt = star >> ps.regex('[^;]+') << col
# Multiline comment: Commentary start + commentry + Commentry end
multicmnt = comstart >> ps.regex('.+?(?=\*\/)', flags=reFlags) << comend

# Either inline or multiline comment, mapped to comment object
cmnt = (inlinecmnt|multicmnt).map(comment)

# Complex SAS Objects
# sasName: Any named object in SAS, can contain macrovariable as part of name
sasName = (wrd|mcv).many()

# Marcovariable definition:
mcvDef = ps.seq(
    variable =ps.regex('%let',flags=reFlags) + spc + opspc >> sasName << opspc + eq,
    value = ps.regex('[^;]+', flags=reFlags).optional(),
    _col = col
).combine_dict(macroVariableDefinition)

# datalineArg: Argument in dataline sasName = (setting)
# e.g. where=(1=1)
datalineArg = ps.seq(
    option =sasName << (opspc + eq + opspc), 
    setting = lb + ps.regex('[^)]*') + rb
)

# datalineOptions: Seperate multiple datalineArgs by spaces
datalineOptions = ps.seq(
    args= lb >> (datalineArg|sasName).sep_by(spc) << rb
)

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
    outputs = (ps.regex('data', flags=re.IGNORECASE) + spc) >> dataLine << col,
    header = ps.regex('.*?(?=set|merge)', flags=reFlags),
    inputs = (opspc + ps.regex('set|merge',flags=re.IGNORECASE) + opspc) >> dataLine << col,
    body = ps.regex('.*?(?=run)', flags=reFlags),
    _run = run + opspc + col
).combine_dict(dataStep)

# proc: Abstracted form of all procedure statements, has three components:
#   - type: capture procedure type directly after "proc"
#   - inputs: capture single dataObj after "data="
#   - outputs: capture single dataObj after "out="
# throw away an other excess
proc = ps.seq(
    type = (ps.regex('proc', flags=re.IGNORECASE) + spc) >> wrd << spc,
    _h1 = ps.regex('.*?(?=data)', flags=reFlags),
    inputs = (ps.regex('data', flags=re.IGNORECASE) + opspc + eq + opspc) >> dataObj,
    _h2 = ps.regex('.*?(?=out\s*=)', flags=reFlags).optional(),
    outputs = ((ps.regex('out', flags=re.IGNORECASE) + opspc + eq + opspc) >> dataObj).optional(),
    _h3 = ps.regex('.*?(?=run|quit)', flags=reFlags),
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


program = (nl|mcvDef|cmnt|datastep|proc|lbnm|icld).many()
