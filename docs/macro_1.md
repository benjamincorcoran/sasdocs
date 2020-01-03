# macro_1
`Last built: 2020-01-03 12:23`

`Path: \\hefce\Scratch\corcobe\SASDocs\tests\samples\macro_1.sas`

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
| [a\bad\path]() | 9 | 



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