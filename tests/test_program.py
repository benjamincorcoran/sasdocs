import pytest
import pprint
from sasdocs.objects import *
from sasdocs.program import sasProgram


testcases = [
    ('./tests/samples/simple_1.sas',[include(path='a/bad/path'),dataStep(outputs=[dataObject(library=None,dataset=['test1'],options=None)], inputs=[dataObject(library=None,dataset=['test'],options=None)], header='\n    ', body='\n'),procedure(type='sort',outputs=[dataObject(library=None,dataset=['test2'],options=None)],inputs=[dataObject(library=None,dataset=['test1'],options=None)])]),
    # ('./tests/samples/macro_1.sas',None),
    # ('./tests/samples/macro_2.sas',None)
]

@pytest.mark.parametrize("case,expected", testcases)
def test_simple_program(case, expected):
    res = sasProgram(case)
    assert res.contents == expected

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




test = sasProgram(testcases[0][0])
for obj in test.get_objects():
    print(obj, obj.start, obj.end)