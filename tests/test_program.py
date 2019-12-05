import pytest
import pprint
from sasdocs.objects import datastep, program

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
remain = sasCode;

parsed = []
while len(remain) > 0:
    partialParse, remain = program.parse_partial(remain)
    if len(partialParse) == 0:
        remain = remain[1:]
        print(remain)
    else:
        parsed += partialParse


parsed1 = [item for item in parsed if item != '\n']
print(parsed)
pprint.pprint(parsed1)