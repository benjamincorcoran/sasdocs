# Macro index
*Last built: 2019-12-29 11:37*

## Macros 
| Macro | About |
| --- | --- | 
| [test](#test) | This is the test macro definition |
| [outer](#outer) | No docstring found. |
| [inner](#inner) |  from b |
| [innermost](#innermost) | No docstring found. |



## test
This is the test macro definition

[comment(text='This is the test macro definition'), include(path=PosixPath('/home/ben/Documents/sasdocs/a/bad/path')), dataStep(outputs=[work.test1], inputs=[work.test]), procedure(outputs=work.test2, inputs=work.test1, type='sort')]

## outer
No docstring found.

[dataStep(outputs=[work.out], inputs=[work.a]), macro(name=['inner'], arguments=None)]

## inner
 from b

[comment(text=' from b'), dataStep(outputs=[work.inn], inputs=[work.a]), macro(name=['innermost'], arguments=None)]

## innermost
No docstring found.

[dataStep(outputs=[work.inmst], inputs=[work.a])]
