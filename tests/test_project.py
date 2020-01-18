import pytest
import pprint

from collections import Counter
from sasdocs.project import sasProject
from sasdocs.program import sasProgram

testcases = ["bad/path"]

@pytest.mark.parametrize("case", testcases)
def test_failed_project(case):
    res = sasProject(case)
    assert res.programs == list()
    assert hasattr(res, 'name') is False
    assert hasattr(res, 'nPrograms') is False
    assert hasattr(res, 'summary') is False
    assert hasattr(res, 'objects') is False

testcases = [
    (sasProject('./tests/samples'),{'programs':[sasProgram('./tests/samples/macro_1.sas'), 
                      sasProgram('./tests/samples/macro_2.sas'), 
                      sasProgram('./tests/samples/simple_1.sas')],
                        'names':set(['macro_1', 'macro_2', 'simple_1'])}
    )
]

@pytest.mark.parametrize("case,expected", testcases)
def test_project_programs_attrs(case,expected):
    assert hasattr(case, 'name') is True
    assert hasattr(case, 'nPrograms') is True
    assert hasattr(case, 'summary') is True
    assert hasattr(case, 'objects') is True


@pytest.mark.parametrize("case,expected", testcases)
def test_project_programs_names(case,expected):
    assert set([prg.name for prg in case.programs]) == expected['names']


# @pytest.mark.parametrize("case,expected", testcases)
# def test_project_get_objects(case,expected):
#     summary = Counter()
#     for program in case.programs:
#         summary += Counter(type(obj).__name__ for obj in program.contents) 
#     assert case.summary == summary
