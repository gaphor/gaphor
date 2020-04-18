import ast
import sys
from collections import OrderedDict


def msg(s):
    print(s, file=sys.stderr)


class Writer:
    def __init__(self, overrides=None):
        self.overrides = overrides
        self.classdefs: OrderedDict = OrderedDict()
        self.features = []

    def write(self, filename, header):
        if filename:
            out = hasattr(filename, "write") and filename or open(filename, "w")
        else:
            out = sys.stdout

        try:
            out.write(header)
            if self.overrides:
                out.write(self.overrides.header)
            for cls in self.classdefs.values():
                if cls[0].endswith(":"):
                    for d in cls:
                        out.write(d)
                        out.write("\n")
                    if len(cls) == 1:
                        out.write("    pass\n")
                else:
                    out.write(cls[0])
                    out.write("\n")

                out.write("\n\n")

            for d in self.features:
                out.write(d)
                out.write("\n")
        finally:
            out.close()

    def add_classdef(self, clazz):
        """
        Write a class definition (class xx(x): pass).
        First the parent classes are examined. After that its own definition
        is written. It is ensured that class definitions are only written
        once.
        """
        if not clazz.written:
            s = ""
            for g in clazz.generalization:
                self.add_classdef(g)
                if s:
                    s += ", "
                s = s + g["name"]
            override = self.overrides.get_override(clazz["name"])
            if override:
                self.classdefs[clazz["name"]] = [override]
            else:
                line = f"class {clazz['name']}"
                if s:
                    line += f"({s})"
                line += ":"
                self.classdefs[clazz["name"]] = [line]
        clazz.written = True

    def add_comment(self, line):
        self.features.append(f"# {line}")

    def add_property(self, class_name, name, value, type):
        """
        Write a property to the file. If the property is overridden, use the
        overridden value. value is
        free format text.
        """
        full_name = f"{class_name}.{name}"
        if self.overrides.has_override(full_name):
            type = self.overrides.get_type(full_name)
            impl = self.overrides.get_override(full_name)
        else:
            impl = f"{class_name}.{name} = {value}"

        decl = f"    {name}: {type}"
        if decl in self.classdefs[class_name]:
            msg(f"feature '{class_name}.{name}' is already defined; skipping")
            assert (
                impl in self.features
            ), f"The implementations for {class_name}.{name} should match"
        else:
            self.classdefs[class_name].append(decl)
            self.features.append(impl)

    def add_attribute(self, a, enumerations={}):
        """
        Write a definition for attribute a. Enumerations may be a dict
        of enumerations, indexed by ID. These are used to identify enums.
        """
        params = {}
        type = a.typeValue
        if type is None:
            raise ValueError(
                f"ERROR! type is not specified for property {a.class_name}.{a.name}"
            )

        if type.lower() == "boolean":
            type = "int"
        elif type.lower() in ("integer", "unlimitednatural"):
            type = "int"
        elif type.lower() == "string":
            type = "str"

        default = a.defaultValue
        # Make sure types are represented the Python way:
        if default and default.lower() in ("true", "false"):
            default = default.title()  # True or False...
        if default is not None:
            params["default"] = str(default)

        if ast.literal_eval(a.isDerived or "0") and not self.overrides.has_override(
            f"{a.class_name}.{a.name}"
        ):
            msg(f"ignoring derived attribute {a.class_name}.{a.name}): no definition")
        elif type.endswith("Kind") or type.endswith("Sort"):
            e = list(filter(lambda e: e["name"] == type, list(enumerations.values())))[
                0
            ]
            self.add_property(
                a.class_name,
                a.name,
                f"enumeration('{a.name}', {e.enumerates}, '{default or e.enumerates[0]}')",
                type="enumeration",
            )
        else:
            if params:
                attribute = "attribute('{}', {}, {})".format(
                    a.name, type, ", ".join(map("=".join, list(params.items())))
                )
            else:
                attribute = f"attribute('{a.name}', {type})"
            self.add_property(
                a.class_name, a.name, attribute, type=f"attribute[{type}]"
            )

    def add_operation(self, o):
        full_name = f"{o.class_name}.{o.name}"
        if self.overrides.has_override(full_name):
            self.add_property(
                o.class_name,
                o.name,
                self.overrides.get_override(full_name),
                self.overrides.get_type(full_name),
            )
        else:
            msg(f"No override for operation {full_name}")

    def add_association(self, head, tail):
        """
        Write an association for head.
        The association should not be a redefine or derived association.
        """
        if head.written:
            return

        assert head.navigable
        # Derived unions and redefines are handled separately
        assert not head.derived
        assert not head.redefines

        a = f"association('{head.name}', {head.opposite_class_name}"
        if head.lower not in ("0", 0):
            a += f", lower={head.lower}"
        if head.upper != "*":
            a += f", upper={head.upper}"
        if head.composite:
            a += ", composite=True"

        # Add the opposite property if the head itself is navigable:
        if tail.navigable:
            try:
                # o_derived, o_name = parse_association_name(tail['name'])
                o_name = tail.name
                o_derived = tail.derived
            except KeyError:
                msg(
                    f"ERROR! no name, but navigable: {tail.id} ({tail.class_name}.{tail.name})"
                )
            else:
                assert not (
                    head.derived and not o_derived
                ), "One end is derived, the other end not ???"
                a += f", opposite='{o_name}'"

        extension_association_hack = (
            (head.class_name == "Extension" and head.name == "ownedEnd")
            and "  # type: ignore[assignment]"
            or ""
        )

        self.add_property(
            head.class_name,
            head.name,
            a + ")",
            type=f"relation_one[{head.opposite_class_name}]{extension_association_hack}"
            if head.upper == "1"
            else f"relation_many[{head.opposite_class_name}]",
        )

    def add_derivedunion(self, d):
        """
        Write a derived union. If there are no subsets a warning
        is issued. The derivedunion is still created though.

        Derived unions may be created for associations that were returned
        False by add_association().
        """
        subs = ""
        for u in d.union:
            if u.derived and not u.written:
                self.add_derivedunion(u)
            if subs:
                subs += ", "
            subs += f"{u.class_name}.{u.name}"
        if subs:
            self.add_property(
                d.class_name,
                d.name,
                "derivedunion(%s, '%s', %s, %s, %s, %s)"
                % (
                    d.class_name,
                    d.name,
                    d.opposite_class_name,
                    d.lower,
                    d.upper == "*" and "'*'" or d.upper,
                    subs,
                ),
                type=f"relation_one[{d.opposite_class_name}]"
                if d.upper == "1"
                else f"relation_many[{d.opposite_class_name}]",
            )
        else:
            if not self.overrides.has_override(f"{d.class_name}.{d.name}"):
                msg(
                    f"no subsets for derived union: {d.class_name}.{d.name}[{d.lower}..{d.upper}]"
                )
            self.add_property(
                d.class_name,
                d.name,
                "derivedunion(%s, '%s', %s, %s, %s)"
                % (
                    d.class_name,
                    d.name,
                    d.opposite_class_name,
                    d.lower,
                    d.upper == "*" and "'*'" or d.upper,
                ),
                type=f"relation_one[{d.opposite_class_name}]"
                if d.upper == "1"
                else f"relation_many[{d.opposite_class_name}]",
            )
        d.written = True

    def add_redefine(self, r):
        """
        Redefines may be created for associations that were returned
        False by add_association().
        """
        self.add_property(
            r.class_name,
            r.name,
            "redefine(%s, '%s', %s, %s, %s)"
            % (
                r.class_name,
                r.name,
                r.opposite_class_name,
                r.upper == "*" and "'*'" or r.upper,
                r.redefines,
            ),
            type=f"relation_one[{r.opposite_class_name}]  # type: ignore[assignment]"
            if r.upper == "1"
            else f"relation_many[{r.opposite_class_name}]  # type: ignore[assignment]",
        )
