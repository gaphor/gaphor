from gaphor.core.modeling import UnlimitedNatural, ValueChange


def set_value_change_property_value(
    value_change: ValueChange, new_value: None | str | int | UnlimitedNatural | bool
):
    if new_value is None:
        value_change.property_value = None
        value_change.property_type = None
    elif isinstance(new_value, str):
        value_change.property_value = new_value
        value_change.property_type = "str"
    elif isinstance(new_value, bool):
        value_change.property_value = str(new_value)
        value_change.property_type = "bool"
    elif isinstance(new_value, int):
        value_change.property_value = str(new_value)
        value_change.property_type = "int"
    elif isinstance(new_value, UnlimitedNatural):
        value_change.property_value = str(new_value)
        value_change.property_type = "UnlimitedNatural"


def get_value_change_property_value(
    value_change,
) -> None | str | int | UnlimitedNatural | bool:
    if value_change.property_value is None:
        return None
    elif value_change.property_type == "str":
        return str(value_change.property_value)
    elif value_change.property_type == "int":
        return int(value_change.property_value)
    elif value_change.property_type == "bool":
        return bool(value_change.property_value == "True")
    elif (
        value_change.property_type == "UnlimitedNatural"
        and value_change.property_value == "*"
    ):
        return "*"
    elif value_change.property_type == "UnlimitedNatural":
        return int(value_change.property_value)
    else:
        return None
