def pre_safe_import_module(api):
    # PyGObject modules loaded through the gi repository are marked as MissingModules by modulegraph, so we convert them
    # to RuntimeModules in order for their hooks to be loaded and executed.
    api.add_runtime_module(api.module_name)
