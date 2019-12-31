# macro_1
`Last built: 2019-12-31 10:30`

`Path: /home/ben/Documents/sasdocs/tests/samples/macro_1.sas`

`Parsed: 99.60%`

## Documentation

This is the macro_1 sas program
 
Ben Corcoran 2019

## Summary 

| Object | Count | 
| --- | ---: | 
| comment | 4 |
| dataStep | 2 |
| macro | 1 |
| include | 1 |
| procedure | 1 |





## Includes
| Path | Line | 
| --- | --- | 
| [/home/ben/Documents/sasdocs/a/bad/path](file:///home/ben/Documents/sasdocs/a/bad/path) | 9 | 



## Raw code 

```sas
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

```