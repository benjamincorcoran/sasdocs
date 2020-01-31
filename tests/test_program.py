import pytest
import pprint
from sasdocs.objects import *
from sasdocs.program import sasProgram

testcases = ["bad/path"]

@pytest.mark.parametrize("case", testcases)
def test_failed_program(case):
    res = sasProgram(case)
    assert res.failedLoad == 1
    assert res.contents == []

testcases = [
    ('./tests/samples/simple_1.sas',[include(path='a/bad/path'),libname(library=['output'],path='path/to/output'),dataStep(outputs=[dataObject(library=None,dataset=['test1'],options=None)], inputs=[dataObject(library=None,dataset=['test'],options=None)], header='\n    ', body='\n'),procedure(type='sort',outputs=[dataObject(library=None,dataset=['test2'],options=None)],inputs=[dataObject(library=None,dataset=['test1'],options=None)])]),
    ('./tests/samples/macro_1.sas',[comment(text='This is the macro_1 sas program'), comment(text=' '), comment(text='Ben Corcoran 2019'), dataStep(outputs=[dataObject(library=None, dataset=['test1'], options=None)], inputs=[dataObject(library=None, dataset=['a'], options=None)], header='\n    ', body='\n'), macro(ref=['test'], arguments=None, options=None, contents=[comment(text='This is the test macro definition'), include(path='a/bad/path'), dataStep(outputs=[dataObject(library=None, dataset=['test1'], options=None)], header='\n    ', body='\n', inputs=[dataObject(library=['work'], dataset=['test'], options=None)]), procedure(outputs=[dataObject(library=None, dataset=['test2'], options=None)], inputs=[dataObject(library=None, dataset=['test1'], options=None)], type='sort')])]),
    ('./tests/samples/macro_2.sas',[dataStep(outputs=[dataObject(library=None, dataset=['test'], options=None)], inputs=[dataObject(library=None, dataset=['a'], options=None)], header='\n    ', body='\n'), macro(ref=['outer'], arguments=None, options=None, contents=[dataStep(outputs=[dataObject(library=None, dataset=['out'], options=None)], inputs=[dataObject(library=None, dataset=['a'], options=None)], header=' ', body=' '), macro(ref=['inner'], arguments=None, options=None, contents=[procedure(outputs=[dataObject(library=None, dataset=['a'], options=None)], inputs=[dataObject(library=None, dataset=['b'], options=None)], type='sql'), dataStep(outputs=[dataObject(library=None, dataset=['inn'], options=None)], inputs=[dataObject(library=None, dataset=['a'], options=None)], header=' ', body=' '), macro(ref=['innermost'], arguments=None, options=None, contents=[dataStep(outputs=[dataObject(library=None, dataset=['inmst'], options=None)], inputs=[dataObject(library=None, dataset=['a'], options=None)], header=' ', body=' ')])])])])
]

@pytest.mark.parametrize("case,expected", testcases)
def test_simple_program(case, expected):
    res = sasProgram(case)
    assert res.contents == expected

testcases = [
    ('./tests/samples/simple_1.sas',[include(path='a/bad/path'),libname(library=['output'],path='path/to/output'),dataStep(outputs=[dataObject(library=None,dataset=['test1'],options=None)], inputs=[dataObject(library=None,dataset=['test'],options=None)], header='\n    ', body='\n'),procedure(type='sort',outputs=[dataObject(library=None,dataset=['test2'],options=None)],inputs=[dataObject(library=None,dataset=['test1'],options=None)])]),
    ('./tests/samples/macro_1.sas',[comment(text='This is the macro_1 sas program'), comment(text=' '), comment(text='Ben Corcoran 2019'), dataStep(outputs=[dataObject(library=None, dataset=['test1'], options=None)], inputs=[dataObject(library=None, dataset=['a'], options=None)], header='\n    ', body='\n'), comment(text='This is the test macro definition'), include(path='a/bad/path'), dataStep(outputs=[dataObject(library=None, dataset=['test1'], options=None)], header='\n    ', body='\n', inputs=[dataObject(library=['work'], dataset=['test'], options=None)]), procedure(outputs=[dataObject(library=None, dataset=['test2'], options=None)], inputs=[dataObject(library=None, dataset=['test1'], options=None)], type='sort')]),
    ('./tests/samples/macro_2.sas',[dataStep(outputs=[dataObject(library=None, dataset=['test'], options=None)], inputs=[dataObject(library=None, dataset=['a'], options=None)], header='\n    ', body='\n'), dataStep(outputs=[dataObject(library=None, dataset=['out'], options=None)], inputs=[dataObject(library=None, dataset=['a'], options=None)], header=' ', body=' '), procedure(outputs=[dataObject(library=None, dataset=['a'], options=None)], inputs=[dataObject(library=None, dataset=['b'], options=None)], type='sql'), dataStep(outputs=[dataObject(library=None, dataset=['inn'], options=None)], inputs=[dataObject(library=None, dataset=['a'], options=None)], header=' ', body=' '), dataStep(outputs=[dataObject(library=None, dataset=['inmst'], options=None)], inputs=[dataObject(library=None, dataset=['a'], options=None)], header=' ', body=' ')])
]

@pytest.mark.parametrize("case,expected", testcases)
def test_get_objects(case, expected):
    res = sasProgram(case)
    assert [obj for obj in res.get_objects()] == expected



testcases = [
    ('./tests/samples/simple_1.sas',['simple_1',8,"100.00%"]),
    ('./tests/samples/macro_1.sas',['macro_1',16,"99.60%"]),
    ('./tests/samples/macro_2.sas',['macro_2',18,'100.00%'])
]

@pytest.mark.parametrize("case,expected", testcases)
def test_extended_info_program(case, expected):
    res = sasProgram(case)
    assert res.name == expected[0]
    assert res.lines == expected[1]
    assert res.parsed == expected[2]



testcases = [
    ('./tests/samples/simple_1.sas', {'libname': 1, 'include':1, 'dataStep':1, 'procedure':1}),
    ('./tests/samples/macro_1.sas', {'comment':4, 'dataStep': 2, 'macro': 1, 'include': 1, 'procedure': 1}),
    ('./tests/samples/macro_2.sas', {'dataStep': 4, 'macro': 3, 'procedure': 1})
]

@pytest.mark.parametrize("case,expected", testcases)
def test_summarise_program(case, expected):
    res = sasProgram(case)
    assert res.summarise_objects() == expected


testcases = [
    ('./tests/samples/simple_1.sas',[([1,0],[1,22]),([2,0],[2,32]),([4,0],[6,4]),([8,0],[8,36])]),
    # ('./tests/samples/macro_1.sas',None),
    # ('./tests/samples/macro_2.sas',None)
]

@pytest.mark.parametrize("case,expected", testcases)
def test_get_posistion_program(case, expected):
    res = sasProgram(case)
    for obj, (start, end) in zip(res.contents,expected):
        assert obj.start == start
        assert obj.end == end
