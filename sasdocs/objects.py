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

# Parsy Objects

# Basic Objects
wrd = ps.regex(r'[a-zA-Z0-9_-]+')

spc = ps.regex(r'\s+')
opspc = ps.regex(r'\s*')

dot = ps.string('.')
opdot = ps.string('.').optional().map(lambda x: '' if x is None else x)

eq = ps.string('=')
col = ps.string(';')
amp = ps.string('&')
lb = ps.string('(')
rb = ps.string(')')


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
    header = ps.regex('.*?(?=set|merge)', flags=re.IGNORECASE),
    inputs = (opspc + ps.regex('set|merge',flags=re.IGNORECASE) + opspc) >> dataLine << col,
    body = ps.regex('.*?(?=run)', flags=re.IGNORECASE),
    _run = run + opspc + col
).combine_dict(dataStep)

proc = ps.seq(
    type = (ps.regex('proc', flags=re.IGNORECASE) + spc) >> wrd << spc,
    _h1 = ps.regex('.*?(?=data)', flags=re.IGNORECASE),
    inputs = (ps.regex('data', flags=re.IGNORECASE) + opspc + eq + opspc) >> dataLine,
    _h2 = ps.regex('.*?(?=out\s*=)', flags=re.IGNORECASE).optional(),
    outputs = ((ps.regex('out', flags=re.IGNORECASE) + opspc + eq + opspc) >> dataLine).optional(),
    _h3 = ps.regex('.*?(?=run|quit)', flags=re.IGNORECASE),
    _run = (run|qt) + opspc + col
).combine_dict(procedure)


