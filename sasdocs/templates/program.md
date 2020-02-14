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
{% for library in program.get_objects(objectType='libname') %}| {{library.name}} | {% if library.type == 'path' %} {% if library.resolved %}`[{{library.path}}]({{library.uri}})` {% else %} `{{library.path}}` {% endif %} {% else %} `{{library.pointer}}` {% endif %} | {{library.start[0]}} |
{% endfor %}
{% endif %}

{% if 'include' in program.summary.keys() %}
## Includes
| Path | Line | 
| --- | --- | 
{% for include in program.get_objects(objectType='include') %}| {% if include.resolved %}`[{{include.path}}]({{include.uri}})` {% else %} `{{include.path}}` {% endif %} | {{include.start[0]}} | 
{% endfor %}
{% endif %}

{% if program.dataObjects | length > 0 %}
## Datasets
| Library | Dataset | Line | 
| --- | --- | --- |
{% for UID, lst in program.dataObjects.items() %} | {{lst[0]['obj']._lib}} | {{lst[0]['obj']._ds}} | {% for ref in lst %} {{ref['start'][0]}}:{{ref['end'][0]}}, {% endfor %} |
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

<script>
$(document).ready(function(){
    var textArea = $("#cma{{program.name.replace(' ','')}}");
    textArea.val(String.raw`{{program.raw}}`);	
	var cmConfig = {mode:"sas",lineNumbers:true,readOnly:true,gutter:true,lineWrapping:true,autoRefresh: true};
    var codeMirror = CodeMirror.fromTextArea(document.getElementById("cma{{program.name.replace(' ','')}}"), cmConfig);
});
</script>

<textarea id="cma{{program.name.replace(' ','')}}"></textarea>

