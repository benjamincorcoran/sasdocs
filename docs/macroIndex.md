# Macro index
*Last built: 2020-01-03 12:37*

## Macros 
| Macro | About |
| --- | --- | 
| [test](#test) | This is the test macro definition |
| [outer](#outer) | No docstring found. |
| [inner](#inner) | No docstring found. |
| [innermost](#innermost) | No docstring found. |



## test
This is the test macro definition

[comment(text='This is the test macro definition'), include(path=WindowsPath('a/bad/path')), dataStep(outputs=[work.test1], inputs=[work.test]), procedure(outputs=[work.test2], inputs=[work.test1], type='sort')]

## outer
No docstring found.

[dataStep(outputs=[work.out], inputs=[work.a]), macro(ref=['inner'], arguments=None)]

## inner
No docstring found.

[procedure(outputs=[work.a], inputs=[work.b], type='sql'), dataStep(outputs=[work.inn], inputs=[work.a]), macro(ref=['innermost'], arguments=None)]

## innermost
No docstring found.

[dataStep(outputs=[work.inmst], inputs=[work.a])]
