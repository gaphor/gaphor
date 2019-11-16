# Saving and Loading Gaphor Diagrams

The root element of Gaphor models is the `Gaphor` tag, all other elements are
contained in this. The Gaphor element delimits the beginning and the end of an
Gaphor model.

The idea is to keep the file format as simple and extensible as
possible: UML elements (including Diagram) are at the top level with no nesting.
A UML element can have two tags: `Reference` and `Value`. Reference is used to
point to other UML elements, Value has a value inside (an integer or a string).

Diagram is a special case. Since this element contains a diagram canvas
inside, it may become pretty big (with lots of nested elements). This is
handled by the load and save function of the Diagram class. All elements
inside a canvas have a tag `Item`.

```xml 
<?xml version="1.0" ?>
<Gaphor version="1.0" gaphor_version="0.3">
  <Package id="1">
    <ownedElement>
      <reflist>
        <ref refid="2"/>
        <ref refid="3"/>
        <ref refid="4"/>
      </reflist>
    </ownedElement>
  </Package>
  <Diagram id="2">
    <namespace>
      <ref refid="1"/>
    </namespace>
    <canvas extents="(9.0, 9.0, 189.0, 247.0)" grid_bg="0xFFFFFFFF"
     grid_color="0x80ff" grid_int_x="10.0" grid_int_y="10.0"
     grid_ofs_x="0.0" grid_ofs_y="0.0" snap_to_grid="0"
     static_extents="0" affine="(1.0, 0.0, 0.0, 1.0, 0.0, 0.0)"
     id="DCE:xxxx">
      <item affine="(1.0, 0.0, 0.0, 1.0, 150.0, 50.0)" cid="0x8293e74"
         height="78.0" subject="3" type="ActorItem" width="38.0"/>
      <item affine="(1.0, 0.0, 0.0, 1.0, 10.0, 10.0)" cid="0x82e7d74"
         height="26.0" subject="5" type="CommentItem" width="100.0"/>
    </canvas>
  </Diagram>
  <Actor id="3">
    <name>
      <val><![CDATA[Actor]]></val>
    </name>
    <namespace>
      <ref refid="1"/>
    </namespace>
  </Actor>
  <UseCase id="4">
    <namespace>
      <ref refid="1"/>
    </namespace>
  </UseCase>
  <Comment id="5"/>
</Gaphor>
```
