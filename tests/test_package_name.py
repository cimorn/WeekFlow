import importlib


def test_weekflow_package_exposes_main_module():
    package = importlib.import_module("WeekFlow")
    main_module = importlib.import_module("WeekFlow.main")

    assert package.__doc__ is not None
    assert callable(main_module.main)
