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