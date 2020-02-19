# Macro index

| Macro | About |
| --- | --- | 
{% for macro in program.get_objects(objectType='macro') %}| [{{macro.name}}](#{{macro.name}}) | {{macro.shortDesc}} |
{% endfor %}

{% for macro in program.get_objects(objectType='macro') %}
## `{{macro.name}}`
{{macro.about}}

```sas
%{{macro.name}}({% if macro.arguments is not none %}{% for arg in macro.arguments %}{{arg._arg}}{{ ", " if not loop.last }}{% endfor %}{% endif %})
```

{% if macro.arguments is not none %}
| Argument | Default | About | 
| --- | --- | --- |
{% for argument in macro.arguments %}| {{argument._arg}} | {{argument._default}} | {{argument._doc}} |
{% endfor %}
{% endif %}


{% endfor %}
