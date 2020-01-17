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


res = sasProject('travis/safe')
res.add_programs_to_project(['./tests/samples/macro_1.sas','./tests/samples/macro_2.sas','./tests/samples/simple_1.sas'])
res.path='travis/safe'
res.get_extended_info()

testcases = [
    (res,{'programs':[sasProgram('./tests/samples/macro_1.sas'), 
                                    sasProgram('./tests/samples/macro_2.sas'), 
                                    sasProgram('./tests/samples/simple_1.sas')],
                        'names':['macro_1', 'macro_2', 'simple_1']}
    )
]

@pytest.mark.parametrize("case,expected", testcases)
def test_project_programs(case,expected):
    # assert list(map(lambda x: x.__dict__, case.programs)) == list(map(lambda x: x.__dict__, expected['programs']))
    assert [prg.name for prg in case.programs] == expected['names']


@pytest.mark.parametrize("case,expected", testcases)
def test_project_get_objects(case,expected):
    allObjects = [x for x in case.get_objects()]
    assert allObjects == [obj for prg in expected['programs'] for obj in prg.get_objects()]
