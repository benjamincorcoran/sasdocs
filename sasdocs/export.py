
import jinja2 as ji

from sasdocs.program import sasProgram

simple = sasProgram('./tests/samples/simple_1.sas')
print(simple)
print(simple.get_extended_info())
print()

with open('./sasdocs/templates/program.tplt', 'r') as f:
    tmplt = f.read()

t = ji.Template(tmplt)

with open('./sasdocs/templates/out.md', 'w') as f:
    f.write(t.render(program=simple))
