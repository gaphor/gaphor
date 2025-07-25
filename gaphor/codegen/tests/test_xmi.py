from gaphor.codegen.xmi import convert


def test_kerml_xmi_conversion():
    element_factory = convert("models/KerML-25-04-04.xmi")

    assert not element_factory.is_empty()
    assert element_factory.lookup("KerML")


def test_sysmlv2_xmi_conversion():
    element_factory = convert("models/SysMLv2-25-02-15.xmi")

    assert not element_factory.is_empty()
    assert element_factory.lookup("SysML")
