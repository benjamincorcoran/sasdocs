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
    ('./tests/samples/simple_1.sas',[include(path='a/bad/path'),dataStep(outputs=[dataObject(library=None,dataset=['test1'],options=None)], inputs=[dataObject(library=None,dataset=['test'],options=None)], header='\n    ', body='\n'),procedure(type='sort',outputs=[dataObject(library=None,dataset=['test2'],options=None)],inputs=[dataObject(library=None,dataset=['test1'],options=None)])]),
    ('./tests/samples/macro_1.sas',[dataStep(outputs=[dataObject(library=None, dataset=['test1'], options=None)], inputs=[dataObject(library=None, dataset=['a'], options=None)], header='\n    ', body='\n'), macro(name=['test'], arguments=None, options=None, contents=[include(path='a/bad/path'), dataStep(outputs=[dataObject(library=None, dataset=['test1'], options=None)], header='\n    ', body='\n', inputs=[dataObject(library=['work'], dataset=['test'], options=None)]), procedure(outputs=[dataObject(library=None, dataset=['test2'], options=None)], inputs=[dataObject(library=None, dataset=['test1'], options=None)], type='sort')])]),
    ('./tests/samples/macro_2.sas',[dataStep(outputs=[dataObject(library=None, dataset=['test'], options=None)], inputs=[dataObject(library=None, dataset=['a'], options=None)], header='\n    ', body='\n'), macro(name=['outer'], arguments=None, options=None, contents=[dataStep(outputs=[dataObject(library=None, dataset=['out'], options=None)], inputs=[dataObject(library=None, dataset=['a'], options=None)], header=' ', body=' '), macro(name=['inner'], arguments=None, options=None, contents=[procedure(outputs=[dataObject(library=None, dataset=['a'], options=None)], inputs=[dataObject(library=None, dataset=['b'], options=None)], type='sql'), dataStep(outputs=[dataObject(library=None, dataset=['inn'], options=None)], inputs=[dataObject(library=None, dataset=['a'], options=None)], header=' ', body=' '), macro(name=['innermost'], arguments=None, options=None, contents=[dataStep(outputs=[dataObject(library=None, dataset=['inmst'], options=None)], inputs=[dataObject(library=None, dataset=['a'], options=None)], header=' ', body=' ')])])])])
]

@pytest.mark.parametrize("case,expected", testcases)
def test_simple_program(case, expected):
    res = sasProgram(case)
    assert res.contents == expected

testcases = [
    ('./tests/samples/simple_1.sas',[include(path='a/bad/path'),dataStep(outputs=[dataObject(library=None,dataset=['test1'],options=None)], inputs=[dataObject(library=None,dataset=['test'],options=None)], header='\n    ', body='\n'),procedure(type='sort',outputs=[dataObject(library=None,dataset=['test2'],options=None)],inputs=[dataObject(library=None,dataset=['test1'],options=None)])]),
    ('./tests/samples/macro_1.sas',[dataStep(outputs=[dataObject(library=None, dataset=['test1'], options=None)], inputs=[dataObject(library=None, dataset=['a'], options=None)], header='\n    ', body='\n'), include(path='a/bad/path'), dataStep(outputs=[dataObject(library=None, dataset=['test1'], options=None)], header='\n    ', body='\n', inputs=[dataObject(library=['work'], dataset=['test'], options=None)]), procedure(outputs=[dataObject(library=None, dataset=['test2'], options=None)], inputs=[dataObject(library=None, dataset=['test1'], options=None)], type='sort')]),
    ('./tests/samples/macro_2.sas',[dataStep(outputs=[dataObject(library=None, dataset=['test'], options=None)], inputs=[dataObject(library=None, dataset=['a'], options=None)], header='\n    ', body='\n'), dataStep(outputs=[dataObject(library=None, dataset=['out'], options=None)], inputs=[dataObject(library=None, dataset=['a'], options=None)], header=' ', body=' '), procedure(outputs=[dataObject(library=None, dataset=['a'], options=None)], inputs=[dataObject(library=None, dataset=['b'], options=None)], type='sql'), dataStep(outputs=[dataObject(library=None, dataset=['inn'], options=None)], inputs=[dataObject(library=None, dataset=['a'], options=None)], header=' ', body=' '), dataStep(outputs=[dataObject(library=None, dataset=['inmst'], options=None)], inputs=[dataObject(library=None, dataset=['a'], options=None)], header=' ', body=' ')])
]

@pytest.mark.parametrize("case,expected", testcases)
def test_get_objects(case, expected):
    res = sasProgram(case)
    assert [obj for obj in res.get_objects()] == expected



testcases = [
    ('./tests/samples/simple_1.sas',['simple_1',7,"100.00%"]),
    ('./tests/samples/macro_1.sas',['macro_1',12,"99.32%"]),
    ('./tests/samples/macro_2.sas',['macro_2',18,'100.00%'])
]

@pytest.mark.parametrize("case,expected", testcases)
def test_extended_info_program(case, expected):
    res = sasProgram(case)
    assert res.name == expected[0]
    assert res.lines == expected[1]
    assert res.parsed == expected[2]



testcases = [
    ('./tests/samples/simple_1.sas', {'include':1, 'dataStep':1, 'procedure':1}),
    ('./tests/samples/macro_1.sas', {'dataStep': 2, 'macro': 1, 'include': 1, 'procedure': 1}),
    ('./tests/samples/macro_2.sas', {'dataStep': 4, 'macro': 3, 'procedure': 1})
]

@pytest.mark.parametrize("case,expected", testcases)
def test_summarise_program(case, expected):
    res = sasProgram(case)
    assert res.summarise_objects() == expected


testcases = [
    ('./tests/samples/simple_1.sas',[([1,0],[1,22]),([3,0],[5,4]),([7,0],[7,36])]),
    # ('./tests/samples/macro_1.sas',None),
    # ('./tests/samples/macro_2.sas',None)
]

@pytest.mark.parametrize("case,expected", testcases)
def test_get_posistion_program(case, expected):
    res = sasProgram(case)
    for obj, (start, end) in zip(res.contents,expected):
        assert obj.start == start
        assert obj.end == end
