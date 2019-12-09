import pytest
import pprint
from sasdocs.program import sasProgram


testcases = [('./tests/samples/simple_1.sas',None)]

@pytest.mark.parametrize("case,expected", testcases)
def test_simple_program(case, expected):
    res = sasProgram(case)

pprint.pprint(sasProgram(testcases[0][0]).extendedInfo)
pprint.pprint(sasProgram(testcases[0][0]).contents)