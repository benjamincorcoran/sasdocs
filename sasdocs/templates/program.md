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

## Libraries
| Library | Path | 
| --- | --- | 
{% for library in program.get_objects(objectType='libname') %}| {{library.name}} | [{{library.path}}]({{library.path}}) |
{% endfor %}

## Include
| Path | 
| --- | 
{% for include in program.get_objects(objectType='include') %}| [{{include.path}}]({{include.path.as_uri()}}) |
{% endfor %}

## Raw code 

```sas
{{program.raw}}
```