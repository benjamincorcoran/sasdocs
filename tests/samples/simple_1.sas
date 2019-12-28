%include "a/bad/path";
libname output "path/to/output";

data test1;
    set work.test;
run;

proc sort data=test1 out=test2; run;
