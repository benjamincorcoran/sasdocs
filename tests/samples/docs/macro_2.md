# macro_2
`Last built: 2019-12-27 11:53`

`Path: /home/ben/Documents/sasdocs/tests/samples/macro_2.sas`

`Parsed: 100.00%`

## Documentation

No documentation found.

## Summary 

| Object | Count | 
| --- | ---: | 
| dataStep | 4 |
| macro | 3 |
| procedure | 1 |






## Raw code 

```sas

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
```