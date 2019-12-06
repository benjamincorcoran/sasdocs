import pytest
from sasdocs.objects import *

testcases = [
    ("test", ["test"]),
    ("&test", [macroVariable(variable="&test")]),
    ("&test.", [macroVariable(variable="&test.")]),
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
    ("(where=(1=1))", {'args': [{'option': ['where'], 'setting': '(1=1)'}]})
]

@pytest.mark.parametrize("case,expected", testcases)
def test_dataLineOption_parse(case, expected):
    assert datalineOptions.parse(case) == expected

testcases = [
    ("test library.test library.test&i library.test&i.(where=(a=b))", [dataObject(library=None, dataset=['test'], options=None), dataObject(library=['library'], dataset=['test'], options=None), dataObject(library=['library'], dataset=['test', macroVariable(variable='&i')], options=None), dataObject(library=['library'], dataset=['test', macroVariable(variable='&i.')], options={'args': [{'option': ['where'], 'setting': '(a=b)'}]})])
]

@pytest.mark.parametrize("case,expected", testcases)
def test_dataLine_parse(case, expected):
    assert dataLine.parse(case) == expected

testcases = [
    ("data test.test lib2.test(where=(ax=b) rename=(a=b)); format a; set test; a = 1; b = 2; output; run;", dataStep(outputs=[dataObject(library=['test'], dataset=['test'], options=None), dataObject(library=['lib2'], dataset=['test'], options={'args': [{'option': ['where'], 'setting': '(ax=b)'}, {'option': ['rename'], 'setting': '(a=b)'}]})], header=' format a; ', inputs=[dataObject(library=None, dataset=['test'], options=None)], body=' a = 1; b = 2; output; '))
]

@pytest.mark.parametrize("case,expected", testcases)
def test_dataStep_parse(case, expected):
    assert datastep.parse(case) == expected


testcases = [
    ("proc summary data=lib2.test(where=(ax=b) rename=(a=b)); by x; output out=lib3.test2; run;", procedure(outputs=dataObject(library=['lib3'], dataset=['test2'], options=None), inputs=dataObject(library=['lib2'], dataset=['test'], options={'args': [{'option': ['where'], 'setting': '(ax=b)'}, {'option': ['rename'], 'setting': '(a=b)'}]}), type='summary'))
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
    ('%macro test; %mend;', macro(name=['test'], arguments=None, body=' ')),
    ('%macro test(a, b, c); %mend;', macro(name=['test'], arguments=[macroargument(arg=['a'],default=None,doc=None), macroargument(arg=['b'],default=None,doc=None), macroargument(arg=['c'],default=None,doc=None)], body=' ')),
    ('%macro test (a=1/*Doc A*/,b/*Doc B*/); %mend;', macro(name=['test'], arguments=[macroargument(arg=['a'],default=['1'],doc=comment(text="Doc A")), macroargument(arg=['b'],default=None,doc=comment(text="Doc B"))], body=' ')),
    ('%macro test; data a; set b; run; %mend;', macro(name=['test'], arguments=None, body=' data a; set b; run; ')),
    ('%macro test(a=1/*Doc A*/,b/*Doc B*/); data a; set b; run; %mend;', macro(name=['test'], arguments=[macroargument(arg=['a'],default=['1'],doc=comment(text="Doc A")), macroargument(arg=['b'],default=None,doc=comment(text="Doc B"))], body=' data a; set b; run; ')),
]

@pytest.mark.parametrize("case,expected", testcases)
def test_macro_parse(case, expected):
    assert mcro.parse(case) == expected

testcases = [
    ('%macro test; data a; set b; run; %mend;', [dataStep(outputs=[dataObject(library=None, dataset=['a'], options=None)], header=' ', inputs=[dataObject(library=None, dataset=['b'], options=None)], body=' ')]),
    ('%macro test(a=1/*Doc A*/,b/*Doc B*/); data a; set b; run; %mend;', [dataStep(outputs=[dataObject(library=None, dataset=['a'], options=None)], header=' ', inputs=[dataObject(library=None, dataset=['b'], options=None)], body=' ')]),
]

@pytest.mark.parametrize("case,expected", testcases)
def test_macro_children_parse(case, expected):
    assert mcro.parse(case).body == expected