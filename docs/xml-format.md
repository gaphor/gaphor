# File Format (XML)

Since Gaphor generates the Python data model from a Gaphor model file, it
would be possible to also generate a Document Type Definition (DTD) as well.

These are the things that should be distinguished:
- Model elements
- Associations with other model elements (referenced by ID):
  - Relations with multiplicty of zero to one (0..1)
  - Relations with multiplicty of zero or more (0..*)
- Attributes, which always have a multiplicity of zero to one (0..1)
- Diagrams
  - One canvas
  - Several canvas items
- Derived attributes and associations are not saved
- Model elements should have their class name as tag name:

```xml
<Class id="DCE:xxx.xxx...">
  ...
</Class>
<Package id="DCE:xxx...">
  ...
</Package>
```

- Support for the two types of Associations, single and multiple:

```xml
<Class id="DCE:xxx.xxx...">
  <package>
    <ref refid="DCE:xxx.../>
  </package>
</Class>
<Package id="DCE:xxx...">
  <ownedClassifier>
     <reflist>
       <ref refid="DCE:xxx.xxx..."/>
   ...
     </reflist>
  </ownedClassifier>
</Package>
```

- Associations contain primitive data, this can always be displayed as
strings:

```xml
<Class id="DCE:xxx.xxx...">
  <name>
    <![CDATA[My name]]>
  </name>
  <intvar>4</intvar>
</Class>
```

- Canvas is the tag in which all canvas related stuff is placed. This is
the same way it is done now:

```xml
<Diagram id="...">
  <canvas>
   <item type="AssociationItem">
     <subject> <ref refid="DCE:..."/> </subject> <width><val>100.0</val></width>
        </item>
  </canvas>
</Diagram>
```

Most of the time you do not want to have anything to do with the canvas. The
data stored there is specific to Gaphor. The model elements however, are
interesting for other things such as code generators and conversion tools.
Gaphor is also able to export diagrams into a SVG image, so that they can be
used outside of the tool.

