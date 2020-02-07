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
{% for include in program.get_objects(objectType='include') %}| [{{include.path}}]({{include.uri}}) | {{include.start[0]}} | 
{% endfor %}
{% endif %}

{% if program.dataObjects | length > 0 %}
## Datasets
| Library | Dataset | Line | 
| --- | --- | --- |
{% for UID, lst in program.dataObjects.items() %} | {{''.join(lst[0]['obj'].library)}} | {{''.join(lst[0]['obj'].dataset)}} | {% for ref in lst %} {{ref['start'][0]}}:{{ref['end'][0]}}, {% endfor %} |
{% endfor %}
{% endif %}

{%if program.hasNodes %}
## Network 

<script>

$(document).ready(function(){
    createNetworkGraph({{program.networkJSON}},'{{program.name.replace(" ","")}}Network');
});

</script>

<div><svg id='{{program.name.replace(" ","")}}Network'></svg></div>
{% endif %}

## Raw code 

```sas
{{program.raw}}
```
