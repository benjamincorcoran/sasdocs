import pytest
import pprint

from sasdocs.project import sasProject

prj =  sasProject('./tests/samples/')

pprint.pprint(prj.get_extended_info())

# for x in prj.get_objects():
#     print(x)

# Include tests