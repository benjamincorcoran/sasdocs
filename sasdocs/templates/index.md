# {{project.name}} Documentation
`Last built: {{project.buildTime}}`

{{project.readme}}


## Programs 
| Program | Path | Parsed | 
| --- | --- | ---: | 
{% for program in project.programs %}| [{{program.name}}](./{{program.name}}.md) | [{{program.path}}]({{program.path.as_uri()}}) | {{program.parsed}} |
{% endfor %}

## Macros 
| Macro | About |
| --- | --- | 
{% for macro in project.get_objects(objectType='macro') %}| [{{macro.name}}](./macroIndex.md#{{macro.name}}) | {{macro.about}} |
{% endfor %}

## Libraries
| Library | Path | 
| --- | --- | 
{% for library in project.get_objects(objectType='libname') %}| {{library.name}} | [{{library.path}}]({{library.path.as_uri()}}) |
{% endfor %}
