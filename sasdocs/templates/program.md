# {{program.name}}
`Last built: {{program.lastEdit}}`

`Path: {{program.path}}`

`Parsed: {{program.parsed}}`

## Documentation

{{program.documentation}}

## Summary 

| Object | Count | 
| --- | ---: | 
{% for obj, count in program.summary.items() %}| {{obj}} | {{count}} |
{% endfor %}

{% if 'libname' in program.summary.keys() %}
## Libraries
| Library | Path | Line | 
| --- | --- | --- |
{% for library in program.get_objects(objectType='libname') %}| {{library.name}} | [{{library.path}}]({{library.path}}) | {{library.start[0]}} |
{% endfor %}
{% endif %}

{% if 'include' in program.summary.keys() %}
## Includes
| Path | Line | 
| --- | --- | 
{% for include in program.get_objects(objectType='include') %}| [{{include.path}}]({{include.path.as_uri()}}) | {{include.start[0]}} | 
{% endfor %}
{% endif %}

## Raw code 

```sas
{{program.raw}}
```