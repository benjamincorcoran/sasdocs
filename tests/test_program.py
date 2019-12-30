import pytest
import pprint
from sasdocs.objects import fullprogram, force_partial_parse, rebuild_macros
from sasdocs.program import sasProgram


testcases = [
    ('./tests/samples/simple_1.sas',None),
    ('./tests/samples/macro_1.sas',None),
    ('./tests/samples/macro_2.sas',None)
]

@pytest.mark.parametrize("case,expected", testcases)
def test_simple_program(case, expected):
    res = sasProgram(case)


test = sasProgram(testcases[0][0])
for obj in test.get_objects():
    print(obj, obj.start, obj.end)