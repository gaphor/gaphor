from gaphor.ui.installschemas import install_schemas_parser


def test_install_schemas(tmp_path):
    parser = install_schemas_parser()

    args = parser.parse_args(["--schemas-dir", str(tmp_path)])

    args.command(args)

    assert (tmp_path / "org.gaphor.Gaphor.gschema.xml").exists()
    assert (tmp_path / "gschemas.compiled").exists()
