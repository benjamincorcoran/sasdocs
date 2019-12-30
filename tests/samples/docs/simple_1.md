# simple_1
`Last built: 2019-12-30 14:29`

`Path: /home/ben/Documents/sasdocs/tests/samples/simple_1.sas`

`Parsed: 100.00%`

## Documentation

No documentation found.

## Summary 

| Object | Count | 
| --- | ---: | 
| include | 1 |
| libname | 1 |
| dataStep | 1 |
| procedure | 1 |


## Libraries
| Library | Path | 
| --- | --- | 
| output | [/home/ben/Documents/sasdocs/path/to/output](/home/ben/Documents/sasdocs/path/to/output) |


## Include
| Path | 
| --- | 
| [/home/ben/Documents/sasdocs/a/bad/path](file:///home/ben/Documents/sasdocs/a/bad/path) |


## Raw code 

```sas
%include "a/bad/path";
libname output "path/to/output";

data test1;
    set work.test;
run;

proc sort data=test1 out=test2; run;

```