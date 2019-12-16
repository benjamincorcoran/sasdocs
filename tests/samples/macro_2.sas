
data test;
    set a;
run;

%macro outer;

data out; set a; run;
%macro inner;
proc sql;
    create table a as 
    select * from b;
quit;
data inn; set a; run;
%macro innermost;
data inmst; set a; run;
%mend;
%mend;
%mend;