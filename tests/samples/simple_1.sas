%include "a/bad/path";

data test;
    set work.test;
run;

proc sort data=test out=test; run;
