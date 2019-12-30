# Macro index
*Last built: {{project.buildTime}}*

## Macros 
| Macro | About |
| --- | --- | 
{% for macro in project.get_objects(objectType='macro') %}| [{{''.join(macro.name)}}](#{{''.join(macro.name)}}) | {{macro.about}} |
{% endfor %}

{% for macro in project.get_objects(objectType='macro') %}
## {{''.join(macro.name)}}
{{macro.about}}

{{macro.contents}}
{% endfor %}
