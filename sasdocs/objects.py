import os
import logging
import attr
import re
import parsy as ps


@attr.s
class macroVariable:
    variable = attr.ib()

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

reFlags = re.IGNORECASE|re.DOTALL

# Basic Objects
wrd = ps.regex(r'[a-zA-Z0-9_-]+')
fpth = ps.regex(r'[^\'"]+')

spc = ps.regex(r'\s+')
opspc = ps.regex(r'\s*')

dot = ps.string('.')
opdot = ps.string('.').optional().map(lambda x: '' if x is None else x)

nl = ps.string('\n')
eq = ps.string('=')
col = ps.string(';')
amp = ps.string('&')
lb = ps.string('(')
rb = ps.string(')')

qte = ps.string('"') | ps.string("'")


run = ps.regex('run',flags=re.IGNORECASE)
qt = ps.regex('quit',flags=re.IGNORECASE)


# Basic SAS Objects
mcv = (amp + wrd + opdot).map(macroVariable)

# Complex SAS Objects
sasName = (wrd|mcv).many()

datalineArg = ps.seq(
    option =sasName << (opspc + eq + opspc), 
    setting = lb + ps.regex('[^)]*') + rb
)

datalineOptions = ps.seq(
    args= lb >> (datalineArg|sasName).sep_by(spc) << rb
)

dataObj = ps.seq(
    library = (sasName << dot).optional(),
    dataset = dot >> sasName | sasName,
    options = datalineOptions.optional()
).combine_dict(dataObject)

dataLine = dataObj.sep_by(spc)

datastep = ps.seq(
    outputs = (ps.regex('data', flags=re.IGNORECASE) + spc) >> dataLine << col,
    header = ps.regex('.*?(?=set|merge)', flags=reFlags),
    inputs = (opspc + ps.regex('set|merge',flags=re.IGNORECASE) + opspc) >> dataLine << col,
    body = ps.regex('.*?(?=run)', flags=reFlags),
    _run = run + opspc + col
).combine_dict(dataStep)

proc = ps.seq(
    type = (ps.regex('proc', flags=re.IGNORECASE) + spc) >> wrd << spc,
    _h1 = ps.regex('.*?(?=data)', flags=reFlags),
    inputs = (ps.regex('data', flags=re.IGNORECASE) + opspc + eq + opspc) >> dataObj,
    _h2 = ps.regex('.*?(?=out\s*=)', flags=reFlags).optional(),
    outputs = ((ps.regex('out', flags=re.IGNORECASE) + opspc + eq + opspc) >> dataObj).optional(),
    _h3 = ps.regex('.*?(?=run|quit)', flags=reFlags),
    _run = (run|qt) + opspc + col
).combine_dict(procedure)

lbnm = ps.seq(
    library = (ps.regex(r'libname', flags=re.IGNORECASE) + spc) >> sasName << spc,
    path = (opspc + qte >> fpth << opspc + qte + col).optional(),
    pointer = (opspc + lb + opspc >> sasName << opspc + rb + opspc + col).optional()
).combine_dict(libname)

icld = ps.seq(
    path = (ps.regex(r'%include', flags=re.IGNORECASE) + spc + opspc + qte) >> fpth << (qte + opspc + col),
).combine_dict(include)


noMacroSAS = (nl|datastep|proc|lbnm|icld).many()
