# simple_1
`Last built: 2020-01-03 12:23`

`Path: \\hefce\Scratch\corcobe\SASDocs\tests\samples\simple_1.sas`

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
| Library | Path | Line | 
| --- | --- | --- |
| output | [path/to/output](path/to/output) | 2 |




## Includes
| Path | Line | 
| --- | --- | 
| [a\bad\path]() | 1 | 



## Raw code 

```sas
%include "a/bad/path";
libname output "path/to/output";

data test1;
    set test;
run;

proc sort data=test1 out=test2; run;

```