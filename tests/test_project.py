import pytest
import pprint

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
    ("./tests/samples",{'programs':[sasProgram('./tests/samples/macro_1.sas'), 
                                    sasProgram('./tests/samples/macro_2.sas'), 
                                    sasProgram('./tests/samples/simple_1.sas')],
                        'names':['macro_1', 'macro_2', 'simple_1']}
    )
]

# @pytest.mark.parametrize("case,expected", testcases)
# def test_project_programs(case,expected):
#     res = sasProject(case)
#     assert list(map(lambda x: x.__dict__, res.programs)) == list(map(lambda x: x.__dict__, expected['programs']))
#     assert [prg.name for prg in res.programs] == expected['names']


@pytest.mark.parametrize("case,expected", testcases)
def test_project_get_objects(case,expected):
    res = sasProject(case)
    allObjects = [x for x in res.get_objects()]
    assert allObjects == [obj for prg in expected['programs'] for obj in prg.get_objects()]
