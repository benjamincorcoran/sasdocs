Usage
======

The sasdocs module exists as a series of parsers and abstracted SAS programming language objects. 
These objects aim to be fairly intuitive in their purpose. 

SASProgram vs SASProject
^^^^^^^^^^^^^^^^^^^^^^^^

In adddition to the parsers there are two objects that exists to represent the usage of SAS software
outside of the programming language. These are the SASProgram and SASProject objects. These two objects 
are very similar in structure and usage. 

The SASProgram object represents as single `.sas` file, capturing any code and parsing it into the SASProgam's 
`contents` attribute. The SASProgam also contains meta information about the file it has parsed.

The SASProject is a collection of SASProgram files that would consititue work on a single project. The project
is defined by a root path, through which the directory is searched recursively for `.sas` files to parse. These 
parsed files are added to the projects `programs` attribute. The SASProject also contains meta information about 
the project folder and programs contained within. 

Simple example
^^^^^^^^^^^^^^

In the `tests/samples` folder in this repository there are three `.sas` files.  

::

    ├───samples
    │       macro_1.sas
    │       macro_2.sas
    │       simple_1.sas

Using the below code, we can generate a SASProject object that will collect all of these files and parse them. 

.. code-block:: python

   from sasdocs.project import sasProject

   prj = sasProject("./tests/samples")

This `prj` instance now contains several attributes that can be used to describe the project and in the individual
programs contained within. 

.. code-block:: python

    print(prj.name)
    >> "samples"

    print(prj.programs)
    >> [macro_1.sas, macro_2.sas, simple_1.sas]

    print(prj.summary)
    >> {'dataStep': 7, 'macro': 4, 'include': 2, 'procedure': 3}

Each item in the `prj.programs` list is a instance of the `sasProgram` object

.. code-block:: python 

    simple = prj.programs[2]
    
    print(type(simple))
    >> "<class 'sasdocs.program.sasProgram'>"

    print(simple.name)
    >> "simple_1"
    print(simple.parsed)
    >> "100.00%"
    print(simple.summary)
    >> {'include': 1, 'dataStep': 1, 'procedure': 1}
    print(simple.contents)
    >> [include(path=WindowsPath('a/bad/path')), 
        dataStep(outputs=[work.test1], inputs=[work.test]), 
        procedure(outputs=[work.test2], inputs=[work.test1], type='sort')]

Please refer to the object index :doc:`objects` to see all available objects and attributes. 

`get_objects()`
^^^^^^^^^^^^^^^

Both the sasProject and sasProgram class have a `get_objects` function attached. This 
will loop over the associated object and yield each parsed object found.

This following code 

.. code-block:: python

    from sasdocs.project import sasProject
    
    prj = sasProject("./tests/samples")

    for obj in prj.get_objects():
        print(obj, type(obj))

will produce an output of 

.. code-block:: python 

    dataStep(outputs=[work.test1], inputs=[work.a])                   "<class 'sasdocs.objects.dataStep'>"
    include(path=WindowsPath('a/bad/path'))                           "<class 'sasdocs.objects.include'>"
    dataStep(outputs=[work.test1], inputs=[work.test])                "<class 'sasdocs.objects.dataStep'>"
    procedure(outputs=[work.test2], inputs=[work.test1], type='sort'  "<class 'sasdocs.objects.procedure'>"
    dataStep(outputs=[work.test], inputs=[work.a])                    "<class 'sasdocs.objects.dataStep'>"
    dataStep(outputs=[work.out], inputs=[work.a])                     "<class 'sasdocs.objects.dataStep'>"
    procedure(outputs=[work.a], inputs=[work.b], type='sql')          "<class 'sasdocs.objects.procedure'>"
    dataStep(outputs=[work.inn], inputs=[work.a])                     "<class 'sasdocs.objects.dataStep'>"
    dataStep(outputs=[work.inmst], inputs=[work.a])                   "<class 'sasdocs.objects.dataStep'>"
    include(path=WindowsPath('a/bad/path'))                           "<class 'sasdocs.objects.include'>"
    dataStep(outputs=[work.test1], inputs=[work.test])                "<class 'sasdocs.objects.dataStep'>"
    procedure(outputs=[work.test2], inputs=[work.test1], type='sort') "<class 'sasdocs.objects.procedure'>"

The get_objects function also takes the optional `objectType` keyword to specify only a single object type
be returned, the below example

.. code-block:: python

    for obj in prj.get_objects(objectType="include"):
        print(obj, type(obj))

produces the following 

.. code-block:: python

    include(path=WindowsPath('a/bad/path')) "<class 'sasdocs.objects.include'>"
    include(path=WindowsPath('a/bad/path')) "<class 'sasdocs.objects.include'>"

get_objects() will automatically search `macro` contents instead of returning the macro object. In order to get 
all the macros stored in your project use

.. code-block:: python 

    prj.get_objects(objectType="macro")
    

