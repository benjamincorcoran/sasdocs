import pytest
import pprint
from sasdocs.objects import *

testcases = [("""
libname a "path/to/folder";
%let a = 1;
data a.data2;
    set a.data1;
run;
*inline comment;
*inline comment;
/*Comment*/
proc summary data=a.data2 nway; 
    class a b c;
    output out=a.data3;
run;

proc transpose data=a.data3 out=a.data4;
    by a;
run;
""",
[
libname(library=['a'], path='path/to/folder', pointer=None),
macroVariableDefinition(variable=['a'], value=' 1'),
dataStep(outputs=[dataObject(library=['a'], dataset=['data2'], options=None)], header='\n    ', inputs=[dataObject(library=['a'], dataset=['data1'], options=None)], body='\n'),
comment(text='inline comment'),
comment(text='inline comment'),
comment(text='Comment'),
procedure(outputs=dataObject(library=['a'], dataset=['data3'], options=None), inputs=dataObject(library=['a'], dataset=['data2'], options=None), type='summary'),
procedure(outputs=dataObject(library=['a'], dataset=['data4'], options=None), inputs=dataObject(library=['a'], dataset=['data3'], options=None), type='transpose')
])]

@pytest.mark.parametrize("case,expected", testcases)
def test_force_partial_parse(case, expected):
    res = force_partial_parse(program, case)
    res = [item for item in res if item != '\n']
    assert res == expected


testcases = [("""
libname a "path/to/folder";
%let a = 1;
data a.data2;
    set a.data1;
run;
%macro test;
*inline comment;
*inline comment;
/*Comment*/
proc summary data=a.data2 nway; 
    class a b c;
    output out=a.data3;
run;
%mend;
proc transpose data=a.data3 out=a.data4;
    by a;
run;
""",
[
libname(library=['a'], path='path/to/folder', pointer=None),
macroVariableDefinition(variable=['a'], value=' 1'),
dataStep(outputs=[dataObject(library=['a'], dataset=['data2'], options=None)], header='\n    ', inputs=[dataObject(library=['a'], dataset=['data1'], options=None)], body='\n'),
macro(name=['test'], arguments=None, body=[
    comment(text='inline comment'),
    comment(text='inline comment'),
    comment(text='Comment'),
    procedure(outputs=dataObject(library=['a'], dataset=['data3'], options=None), inputs=dataObject(library=['a'], dataset=['data2'], options=None), type='summary')
]),
procedure(outputs=dataObject(library=['a'], dataset=['data4'], options=None), inputs=dataObject(library=['a'], dataset=['data3'], options=None), type='transpose')
])]

@pytest.mark.parametrize("case,expected", testcases)
def test_force_partial_marco_parse(case, expected):
    res = force_partial_parse(fullprogram, case)
    assert res == expected
