import pytest
from sasdocs.objects import *

testcases = [
    ("test", ["test"]),
    ("&test", [macroVariable(variable="&test")]),
    ("&test.", [macroVariable(variable="&test.")]),
    ("&&test&test.", [macroVariable(variable="&&test&test.")]),
    ("ab&test", ['ab',macroVariable(variable="&test")]),
    ("ab&test.", ['ab', macroVariable(variable='&test.')]),
    ("ab&test.ab", ['ab', macroVariable(variable='&test.'), 'ab']),
    ("ab&test.ab&test", ['ab', macroVariable(variable='&test.'), 'ab', macroVariable(variable='&test')]),
    ("ab&test.ab&test.", ['ab', macroVariable(variable='&test.'), 'ab', macroVariable(variable='&test.')]),
    ("ab&test.abab&test.ab", ['ab', macroVariable(variable='&test.'), 'abab', macroVariable(variable='&test.'), 'ab'])
]

@pytest.mark.parametrize("case,expected", testcases)
def test_sasname_parse(case, expected):
    assert sasName.parse(case) == expected

testcases = [
    ("lib.test", dataObject(library=['lib'], dataset=['test'])),
    ("&test.test", dataObject(library=None, dataset=[macroVariable(variable='&test.'), 'test'])),
    ("lib.&test.", dataObject(library=['lib'], dataset=[macroVariable(variable='&test.')])),
    ("lib.ab&test.", dataObject(library=['lib'], dataset=['ab', macroVariable(variable='&test.')])),
    ("lib.ab&test", dataObject(library=['lib'], dataset=['ab', macroVariable(variable='&test')])),
    ("lib.ab&test.ab", dataObject(library=['lib'], dataset=['ab', macroVariable(variable='&test.'), 'ab'])),
    ("lib.ab&test.ab&test", dataObject(library=['lib'], dataset=['ab', macroVariable(variable='&test.'), 'ab', macroVariable(variable='&test')])),
    ("li&lib.b.ab&test.ab&test.",  dataObject(library=['li', macroVariable(variable='&lib.'), 'b'], dataset=['ab', macroVariable(variable='&test.'), 'ab', macroVariable(variable='&test.')])),
    ("ab&lib.&lib.aa.ab&test.abab&test.ab",  dataObject(library=['ab', macroVariable(variable='&lib.'), macroVariable(variable='&lib.'), 'aa'], dataset=['ab', macroVariable(variable='&test.'), 'abab', macroVariable(variable='&test.'), 'ab']))
]

@pytest.mark.parametrize("case,expected", testcases)
def test_dataObject_parse(case, expected):
    assert dataObj.parse(case) == expected

testcases = [
    ("(where=(1=1))", [dataArg(option=['where'], setting='(1=1)')]),
    ("(drop=a)",[dataArg(option=['drop'], setting='a')]),
    ("(drop=a b c d)",[dataArg(option=['drop'], setting='a b c d')]),
    ("(where=(1=1) drop=a)",[dataArg(option=['where'], setting='(1=1)'), dataArg(option=['drop'], setting='a')]),
    ("(drop=a where=(1=1))",[dataArg(option=['drop'], setting='a'), dataArg(option=['where'], setting='(1=1)')]),
    ("(drop=a b c where=(1=1))",[dataArg(option=['drop'], setting='a b c'), dataArg(option=['where'], setting='(1=1)')])
]


@pytest.mark.parametrize("case,expected", testcases)
def test_dataLineOption_parse(case, expected):
    assert datalineOptions.parse(case) == expected

testcases = [
    ("test library.test library.test&i library.test&i.(where=(a=b))", [dataObject(library=None, dataset=['test'], options=None), dataObject(library=['library'], dataset=['test'], options=None), dataObject(library=['library'], dataset=['test', macroVariable(variable='&i')], options=None), dataObject(library=['library'], dataset=['test', macroVariable(variable='&i.')], options=[dataArg(option=['where'], setting='(a=b)')])])
]

@pytest.mark.parametrize("case,expected", testcases)
def test_dataLine_parse(case, expected):
    assert dataLine.parse(case) == expected

testcases = [
    ("data test.test lib2.test(where=(ax=b) rename=(a=b)); format a; set test; a = 1; b = 2; output; run;", dataStep(outputs=[dataObject(library=['test'], dataset=['test'], options=None), dataObject(library=['lib2'], dataset=['test'], options=[dataArg(option=['where'], setting='(ax=b)'), dataArg(option=['rename'], setting='(a=b)')])], header=' format a; ', inputs=[dataObject(library=None, dataset=['test'], options=None)], body=' a = 1; b = 2; output; ')),
    ("data out; input a; datalines; 1; run;", dataStep(outputs=[dataObject(library=None,dataset=['out'],options=None)],inputs=None,header=None,body=' input a; datalines; 1; '))
]

@pytest.mark.parametrize("case,expected", testcases)
def test_dataStep_parse(case, expected):
    assert datastep.parse(case) == expected


testcases = [
    ("proc summary data=lib2.test(where=(ax=b) rename=(a=b)); by x; output out=lib3.test2; run;", procedure(outputs=dataObject(library=['lib3'], dataset=['test2'], options=None), inputs=dataObject(library=['lib2'], dataset=['test'], options=[dataArg(option=['where'], setting='(ax=b)'), dataArg(option=['rename'], setting='(a=b)')]), type='summary'))
]

@pytest.mark.parametrize("case,expected", testcases)
def test_procedure_parse(case, expected):
    assert proc.parse(case) == expected

testcases = [
    ('libname test "helloeastset";', libname(library=['test'], path='helloeastset', pointer=None)),
    ("libname test 'hellotest';", libname(library=['test'], path="hellotest", pointer=None)),
    (r'libname test "\\network\drive";', libname(library=['test'], path=r'\\network\drive', pointer=None)),
    (r"libname test 'S:\mappeddrive';", libname(library=['test'], path=r"S:\mappeddrive", pointer=None)),
    ('libname test (work);', libname(library=['test'], path=None, pointer=['work']))
]

@pytest.mark.parametrize("case,expected", testcases)
def test_libname_parse(case, expected):
    assert lbnm.parse(case) == expected


testcases = [
    (r'%include "\\network\drive\prg.sas";', include(path=r'\\network\drive\prg.sas')),
    (r"%include 'S:\mappeddrive\prg.sas';", include(path=r"S:\mappeddrive\prg.sas")),
    (r'%include "\\network\drive";', include(path=r'\\network\drive')),
    (r"%include 'S:\mappeddrive';", include(path=r"S:\mappeddrive"))
]

@pytest.mark.parametrize("case,expected", testcases)
def test_include_parse(case, expected):
    assert icld.parse(case) == expected

testcases = [
    (r'*Comment;', comment(text=r'Comment')),
    (r"/*Comment*/", comment(text=r"Comment"))
]

@pytest.mark.parametrize("case,expected", testcases)
def test_include_parse(case, expected):
    assert cmnt.parse(case) == expected

testcases = [
    ('create table a as select * from b;',procedure(outputs=dataObject(library=None, dataset=['a'], options=None), inputs=[dataObject(library=None, dataset=['b'], options=None)]))
]
@pytest.mark.parametrize("case,expected", testcases)
def test_create_table_parse(case, expected):
    assert crtetbl.parse(case) == expected

testcases = [
    ('proc sql; create table a as select * from b left join select * from c on a.a=c.a right join select * from d on a.d=d.d; quit;',[procedure(outputs=dataObject(library=None, dataset=['a'], options=None), inputs=[dataObject(library=None, dataset=['b'], options=None),dataObject(library=None, dataset=['c'], options=None),dataObject(library=None, dataset=['d'], options=None)])]),
    ('proc sql; create table a as select * from b; select * from d; create table c as select * from d; quit;',[procedure(outputs=[dataObject(library=None, dataset=['a'], options=None)], inputs=[dataObject(library=None, dataset=['b'], options=None)]), unparsedSQLStatement(text='select * from d;'), procedure(outputs=[dataObject(library=None, dataset=['c'], options=None)], inputs=[dataObject(library=None, dataset=['d'], options=None)])])
]
@pytest.mark.parametrize("case,expected", testcases)
def test_sql_parse(case, expected):
    assert sql.parse(case) == expected



testcases = [
    ('%let a = 1;', macroVariableDefinition(variable=['a'],value=' 1')),
    ('%let a=1;', macroVariableDefinition(variable=['a'],value='1')),
    ('%let a =1;', macroVariableDefinition(variable=['a'],value='1')),
    ('%let a = ;', macroVariableDefinition(variable=['a'],value=' ')),
    ('%let a =;', macroVariableDefinition(variable=['a'],value=None))
]
@pytest.mark.parametrize("case,expected", testcases)
def test_macroVariableDefinition_parse(case, expected):
    assert mcvDef.parse(case) == expected

testcases = [
    ('a', macroargument(arg=['a'],default=None,doc=None)),
    ('a=1', macroargument(arg=['a'],default=['1'],doc=None)),
    ('a =1', macroargument(arg=['a'],default=['1'],doc=None)),
    ('a = ', macroargument(arg=['a'],default=[],doc=None)),
    ('a = 1', macroargument(arg=['a'],default=['1'],doc=None)),
    ('a/*Docs*/', macroargument(arg=['a'],default=None,doc=comment(text="Docs"))),
    ('a=1/*Docs*/', macroargument(arg=['a'],default=['1'],doc=comment(text="Docs"))),
    ('a =1/*Docs*/', macroargument(arg=['a'],default=['1'],doc=comment(text="Docs"))),
    ('a = /*Docs*/', macroargument(arg=['a'],default=[],doc=comment(text="Docs"))),
    ('a = 1/*Docs*/', macroargument(arg=['a'],default=['1'],doc=comment(text="Docs"))),
    ('a = a.b@c.com/*Email*/', macroargument(arg=['a'],default=['a.b@c.com'],doc=comment(text="Email"))),
    ('a = //path/to/file/*Fpath*/', macroargument(arg=['a'],default=['//path/to/file'],doc=comment(text="Fpath"))),
    ('a = C:/path/to/file/*Fpath*/', macroargument(arg=['a'],default=['C:/path/to/file'],doc=comment(text="Fpath"))),
    ('a = &mVar.', macroargument(arg=['a'],default=[macroVariable(variable='&mVar.')],doc=None))
]
@pytest.mark.parametrize("case,expected", testcases)
def test_macroargument_parse(case, expected):
    assert mcroarg.parse(case) == expected


testcases = [
    ('(a, b, c)', [macroargument(arg=['a'],default=None,doc=None), macroargument(arg=['b'],default=None,doc=None), macroargument(arg=['c'],default=None,doc=None)]),
    ('(a=1, b)', [macroargument(arg=['a'],default=['1'],doc=None), macroargument(arg=['b'],default=None,doc=None)]),
    ('(a=1, b=2)', [macroargument(arg=['a'],default=['1'],doc=None), macroargument(arg=['b'],default=['2'],doc=None)]),
    ('(a=1/*Doc A*/,b=2)', [macroargument(arg=['a'],default=['1'],doc=comment(text="Doc A")), macroargument(arg=['b'],default=['2'],doc=None)]),
    ('(a=1/*Doc A*/,b/*Doc B*/)', [macroargument(arg=['a'],default=['1'],doc=comment(text="Doc A")), macroargument(arg=['b'],default=None,doc=comment(text="Doc B"))]),
]
@pytest.mark.parametrize("case,expected", testcases)
def test_macroargumentLine_parse(case, expected):
    assert mcroargline.parse(case) == expected


testcases = [
    ('%macro test;', macroStart(name=['test'], arguments=None, options=None)),
    ('%macro test /des="Description";', macroStart(name=['test'], arguments=None, options=[dataArg(option=['des'],setting='Description')])),
    ('%macro test /strict des="Description";', macroStart(name=['test'], arguments=None, options=[['strict'], dataArg(option=['des'],setting='Description')]))

]
@pytest.mark.parametrize("case,expected", testcases)
def test_macro_start_parse(case, expected):
    assert mcroStart.parse(case) == expected



testcases = [
    ('%macro test; %mend;', macro(name=['test'], arguments=None, contents='')),
    ('%macro test(a, b, c); %mend;', macro(name=['test'], arguments=[macroargument(arg=['a'],default=None,doc=None), macroargument(arg=['b'],default=None,doc=None), macroargument(arg=['c'],default=None,doc=None)], contents='')),
    ('%macro test (a=1/*Doc A*/,b/*Doc B*/); %mend;', macro(name=['test'], arguments=[macroargument(arg=['a'],default=['1'],doc=comment(text="Doc A")), macroargument(arg=['b'],default=None,doc=comment(text="Doc B"))], contents='')),
    ('%macro test; data a; set b; run; %mend;', macro(name=['test'], arguments=None, contents=[dataStep(outputs=[dataObject(library=None, dataset=['a'], options=None)], header=' ', inputs=[dataObject(library=None, dataset=['b'], options=None)], body=' ')])),                                                                    
    ('%macro test(a=1/*Doc A*/,b/*Doc B*/); data a; set b; run; %mend;', macro(name=['test'], arguments=[macroargument(arg=['a'], default=['1'], doc=comment(text='Doc A')), macroargument(arg=['b'], default=None, doc=comment(text='Doc B'))], contents=[dataStep(outputs=[dataObject(library=None, dataset=['a'], options=None)], header=' ', inputs=[dataObject(library=None, dataset=['b'], options=None)], body=' ')])),
]

@pytest.mark.parametrize("case,expected", testcases)
def test_macro_parse(case, expected):
    assert force_partial_parse(fullprogram, case) == [expected]

testcases = [
    ('%macro test; /*This is the test macro*/ %mend;', 'This is the test macro'),
    ('%macro test; /*This is the test macro*/\n/*This is the second line*/%mend;', 'This is the test macro\nThis is the second line'),
    ('%macro test; data a; set b; run; /*This is the test macro*/ %mend;', 'No docstring found.'),
]

@pytest.mark.parametrize("case,expected", testcases)
def test_macro_about_parse(case, expected):
    macro = force_partial_parse(fullprogram,case)[0]
    assert macro.about == expected

testcases = [
    ('%macro test; /*This is the test macro*/ %mend;', None),
    ('%macro test /strict; /*This is the test macro*/\n/*This is the second line*/%mend;', [['strict']]),
    ('%macro test /strict des="Description"; data a; set b; run; /*This is the test macro*/ %mend;', [['strict'], dataArg(option=['des'],setting='Description')]),
]

@pytest.mark.parametrize("case,expected", testcases)
def test_macro_options_parse(case, expected):
    macro = force_partial_parse(fullprogram,case)[0]
    assert macro.options == expected

testcases = [
    ('%macro test; data a; set b; run; %mend;', [dataStep(outputs=[dataObject(library=None, dataset=['a'], options=None)], header=' ', inputs=[dataObject(library=None, dataset=['b'], options=None)], body=' ')]),
    ('%macro test(a=1/*Doc A*/,b/*Doc B*/); data a; set b; run; %mend;', [dataStep(outputs=[dataObject(library=None, dataset=['a'], options=None)], header=' ', inputs=[dataObject(library='work', dataset=['b'])], body=' ')]),
]

@pytest.mark.parametrize("case,expected", testcases)
def test_macro_children_parse(case, expected):
    assert force_partial_parse(fullprogram, case)[0].contents == expected


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
macro(name=['test'], arguments=None, contents=[
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
%mend;
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
macroEnd(text='%mend;'),
procedure(outputs=dataObject(library=['a'], dataset=['data4'], options=None), inputs=dataObject(library=['a'], dataset=['data3'], options=None), type='transpose')
])]


@pytest.mark.parametrize("case,expected", testcases)
def test_force_partial_incomplete_marco_parse(case, expected):
    res = force_partial_parse(fullprogram, case)
    assert res == expected
