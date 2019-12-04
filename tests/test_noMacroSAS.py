import pytest
import pprint
from sasdocs.objects import datastep, noMacroSAS

sasCode = """
libname a "path/to/folder";

data a.data2;
    set a.data1;
run;

proc summary data=a.data2 nway;
    class a b c;
    output out=a.data3;
run;

proc transpose data=a.data3 out=a.data4;
    by a;
run;
"""


sc = noMacroSAS.parse_partial(sasCode)[0]
sc = [item for item in sc if item != '\n']
pprint.pprint(sc)