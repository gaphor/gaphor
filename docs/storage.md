# Saving and Loading models

The root element of Gaphor models is the `Gaphor` tag, all other elements are
contained in this. The Gaphor element delimits the beginning and the end of an
Gaphor model.

The idea is to keep the file format as simple and extensible as
possible: UML elements (including Diagram) are at the top level with no nesting.
A UML element can have two tags: references (`ref`) and values (`val`). References are used to point to other UML elements. Values have a value inside (an integer or a string).

Diagram is a special case. All items on a canvas are embedded in the Diagram
element's.

Since many references are bi-directional, you'll find both ends defined in the file (e.g. `Package.ownedType` - `Actor.package`, and `Diagram.ownedPresentation` and `UseCaseItem.diagram`).

```xml
<?xml version="1.0" ?>
<Gaphor version="1.0" gaphor_version="0.3">
  <Package id="1">
    <ownedClassifier>
      <reflist>
        <ref refid="2"/>
        <ref refid="3"/>
        <ref refid="4"/>
      </reflist>
    </ownedClassifier>
  </Package>
  <Diagram id="2">
    <package>
      <ref refid="1"/>
    </package>
    <ownedPresentation>
      <reflist>
        <ref refid="5"/>
        <ref refid="6"/>
      </reflist>
    </ownedPresentation>
    <canvas>
     <item id="5" type="ActorItem">
        <matrix>
          <val>(1.0, 0.0, 0.0, 1.0, 147.0, 132.0)</val>
        </matrix>
        <width>
          <val>38.0</val>
        </width>
        <height>
          <val>60.0</val>
        </height>
        <diagram>
          <ref refid="2"/>
        </diagram>
        <subject>
          <ref refid="3"/>
        </subject>
      </item>
      <item id="6" type="UseCaseItem">
        <matrix>
          <val>(1.0, 0.0, 0.0, 1.0, 341.0, 144.0)</val>
        </matrix>
        <width>
          <val>98.0</val>
        </width>
        <height>
          <val>30.0</val>
        </height>
        <diagram>
          <ref refid="2"/>
        </diagram>
        <subject>
          <ref refid="4"/>
        </subject>
      </item>
    </canvas>
  </Diagram>
  <Actor id="3">
    <name>
      <val>Actor></val>
    </name>
    <package>
      <ref refid="1"/>
    </package>
  </Actor>
  <UseCase id="4">
    <package>
      <ref refid="1"/>
    </package>
  </UseCase>
  <Comment id="5"/>
</Gaphor>
```
