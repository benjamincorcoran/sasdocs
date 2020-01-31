/*This is the macro_1 sas program*/
/* */
/*Ben Corcoran 2019*/
data test1;
    set a;
run;
%macro test;
/*This is the test macro definition*/
%include "a/bad/path";

data test1;
    set work.test;
run;

proc sort data=test1 out=test2; run;
%mend; 
