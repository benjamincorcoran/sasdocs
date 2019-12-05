import pytest
import pprint
from sasdocs.objects import program, force_partial_parse

sasCode = """
libname a "path/to/folder";
%let a = 1;
data a.data2;
    set a.data1;
run;
*inline comment;
*inline comment;
/*Comment*/
proc summary data=a.data2 nway; 
    class a b c;
    output out=a.data3;
run;

proc transpose data=a.data3 out=a.data4;
    by a;
run;
"""
parsed = force_partial_parse(program, sasCode)
parsed1 = [item for item in parsed if item != '\n']
print(parsed)
pprint.pprint(parsed1)