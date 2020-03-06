import re
import parsy as ps

from . import objects


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

# QuotedString:
qstr = ps.regex(r'[^\'"]*')

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
fs = ps.string('/')


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
mcv = (_mcv | amp + _mcv + _mcv).map(objects.macroVariable)

# Inline comment: start + commentry + semicolon
inlinecmnt = star >> ps.regex(r'[^;]+') << col
# Multiline comment: Commentary start + commentry + Commentry end
multicmnt = comstart >> ps.regex(r'.+?(?=\*\/)', flags=reFlags) << comend

# Either inline or multiline comment, mapped to comment object
cmnt = (inlinecmnt|multicmnt).map(objects.comment)

# Complex SAS Objects
# sasName: Any named object in SAS, can contain macrovariable as part of name
sasName = (wrd|mcv).at_least(1)

# Marcovariable definition:
mcvDef = ps.seq(
    variable =ps.regex(r'%let',flags=reFlags) + spc + opspc >> sasName << opspc + eq,
    value = ps.regex(r'[^;]+', flags=reFlags).optional(),
    _col = col
).combine_dict(objects.macroVariableDefinition)

# datalineArg: Argument in dataline sasName = (setting)
# e.g. where=(1=1)
datalineArg = ps.seq(
    option = sasName << (opspc + eq + opspc), 
    setting = lb + ps.regex(r'[^);]*',flags=reFlags) + rb
).combine_dict(objects.dataArg)

# datalineArg: Argument in dataline sasName = sasName sasName sasName...
# e.g. keep=A B C 
datalineArgNB = ps.seq(
    option = sasName << (opspc + eq + opspc), 
    setting = ps.regex(r'[^;]*?(?=\s+\w+\s*=)|[^\);]*?(?=\))|.*?(?=;)', flags=reFlags)
).combine_dict(objects.dataArg)

datalineArgPt = ps.seq(
    option = sasName << (opspc + eq + opspc),
    setting = opspc + qte >> fpth << opspc + qte
).combine_dict(objects.dataArg)

# datalineOptions: Seperate multiple datalineArgs by spaces
datalineOptions = lb + opspc >> (datalineArg|datalineArgPt|datalineArgNB|sasName).sep_by(spc) << opspc + rb


# dataObj: Abstracted data object exists as three components:
#   - library: sasName before . if . exists
#   - dataset: sasName after . or just sasName required
#   - options: dataLineOptions is present

dataObj = ps.seq(
    library = (sasName << dot).optional(),
    dataset = (dot >> sasName) | sasName,
    options = (opspc >> datalineOptions).optional()
).combine_dict(objects.dataObject)

# dataLine: Multiple dataObjs seperated by space
dataLine = dataObj.sep_by(spc)

# datastep: Abstracted form of datastep process has four components:
#   - outputs: dataline existing directly after "data"
#   - header: anything between outputs and set/merge statment
#   - inputs: dataline directly after set/merge statement
#   - body: anything between inputs and "run"
# terminating run is thrown away

datastep = ps.seq(
    outputs = (ps.regex(r'\bdata\b', flags=re.IGNORECASE) + spc) >> dataLine,
    options = (opspc + fs + opspc >> (datalineArg|datalineArgPt|datalineArgNB|sasName).sep_by(spc)).optional(), 
    _col = opspc + col,
    header = (ps.regex(r'(?:(?!run).)*(?=\bset\b|\bmerge\b)', flags=reFlags)).optional(),
    inputs = ((opspc + ps.regex(r'\bset\b|\bmerge\b',flags=re.IGNORECASE) + opspc) >> dataLine << opspc + col).optional(),
    body = ps.regex(r'.*?(?=\brun\b)', flags=reFlags),
    _run = run + opspc + col
).combine_dict(objects.dataStep)

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
    outputs = ((ps.regex(r'out', flags=re.IGNORECASE) + opspc + eq + opspc) >> dataObj).sep_by(ps.regex(r'(?:(?!run|quit).)*?(?=out\s*=)', flags=reFlags)).optional(),
    _h3 = ps.regex(r'.*?(?=run|quit)', flags=reFlags),
    _run = (run|qt) + opspc + col
).combine_dict(objects.procedure)

# crtetbl: Parser for create table sql statement

crtetbl = ps.seq(
    outputs = ps.regex(r'create table', flags=reFlags) + opspc >> dataObj.sep_by(opspc+cmm+opspc) <<  opspc + ps.regex(r'as'),
    inputs = (ps.regex(r'[^;]*?from', flags=reFlags) + spc + opspc >> dataObj.sep_by(opspc+cmm+opspc)).many(),
    _h = ps.regex(r'[^;]*?(?=;)', flags=reFlags) + col
).combine_dict(objects.procedure)

# unparsedSQL: Capture currently unparsed SQL statements

unparsedSQL = ps.regex(r'[^;]*?;(?<!quit;)', flags=reFlags).map(objects.unparsedSQLStatement)

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
).combine_dict(objects.libname)

# icld: Abstracted include statement, one component:
#   - path: file path to the included code 
icld = ps.seq(
    path = (ps.regex(r'%include', flags=re.IGNORECASE) + spc + opspc + qte) >> fpth << (qte + opspc + col),
).combine_dict(objects.include)

# program: Multiple SAS objects in any order
program = (nl|mcvDef|cmnt|datastep|proc|lbnm|icld).many()


mcroarg = ps.seq(
    arg = sasName << opspc,
    default = (eq + opspc >> (ps.regex(r'(?:[a-zA-Z0-9_\-@\.\:]|\/(?!\*)|\\(?!\*))+')|mcv|(qte+qstr+qte)).many()).optional() << opspc,
    doc = opspc >> cmnt.optional()
).combine_dict(objects.macroargument)

mcroargline = lb + opspc >> mcroarg.sep_by(opspc+cmm+opspc) << opspc + rb

mcroStart = ps.seq(
    name = ps.regex(r'%macro',flags=re.IGNORECASE) + spc + opspc >> sasName,
    arguments = (opspc >> mcroargline).optional(), 
    options = (opspc + fs + opspc >> (datalineArg|datalineArgPt|sasName).sep_by(spc)).optional(),
    _col = opspc + col 
).combine_dict(objects.macroStart)

mcroEnd = (ps.regex(r'%mend.*?;',flags=re.IGNORECASE)).map(objects.macroEnd)

mcroCall = ps.seq(
    name = ps.regex(r'%') >> sasName,
    arguments = (opspc >> mcroargline).optional(),
    _col = opspc + col
).combine_dict(objects.macroCall)

# fullprogram: multiple SAS objects including macros
fullprogram =  (nl|mcvDef|cmnt|datastep|proc|sql|lbnm|icld|mcroStart|mcroEnd|mcroCall).optional()

