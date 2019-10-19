# Gaphor XML format

This format is meant to be a shorter and more obvious version of
Gaphor's file format. The current format makes it pretty hard to do
some decent XSLT parsing. In the current file format one has to compare
the @name attribute with the model element name one wishes.

Since the data model is generated from a Gaphor (0.2) model it would be
a piece of cake to generate a DTD too.

These are the things that should be distinguished: - model elements -
associations with other model elements (referenced by ID):

-   0..1 relations
-   0..\* relations

-   attributes (always have a multiplicity of 0..1)
-   diagrams
    -   one canvas
    -   several canvas items
-   derived attributes and associations are not saved of course.

Model elements should have their class name as tag name, e.g.:

    <Class id="DCE:xxx.xxx...">
      ...
    </Class>
    <Package id="DCE:xxx...">
      ...
    </Package>

Associations are in two flavors: single and multiple:

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

Associations contain primitive data, this can always be displayed as
strings:

    <Class id="DCE:xxx.xxx...">
      <name>
        <![CDATA[My name]]>
      </name>
      <intvar>4</intvar>
    </Class>

Canvas is the tag in which all canvas related stuff is placed. This is
the same way it is done now:

    <Diagram id="...">
      <canvas>
        <item type="AssociationItem">
          <subject>
        <ref refid="DCE:..."/>
      </subject>
      <width><val>100.0</val></width>
        </item>
      </canvas>
    </Diagram>

Most of the time you do not want to have anything to do with the canvas.
The data stored there is specific to Gaphor. The model elements however,
are interesting for other things such as code generators and conversion
tools. Gaphor has export filters for SVG graphics, so diagrams can be
exported in a independant way.
