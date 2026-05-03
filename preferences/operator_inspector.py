import bpy


RUNTIME_PROPERTY_NAMES = {
    "filepath",
    "directory",
    "files",
    "filename",
    "filter_glob",
    "check_existing",
    "hide_props_region",
}


def normalize_bl_idname(bl_idname):
    bl_idname = (bl_idname or "").strip()
    if bl_idname.startswith("bpy.ops."):
        bl_idname = bl_idname[8:]
    if bl_idname.endswith("()"):
        bl_idname = bl_idname[:-2]
    return bl_idname


def get_operator(bl_idname):
    bl_idname = normalize_bl_idname(bl_idname)
    if "." not in bl_idname:
        raise AttributeError(f'Invalid operator id "{bl_idname}"')
    category, name = bl_idname.split(".", 1)
    return getattr(getattr(bpy.ops, category), name)


def operator_exists(bl_idname):
    try:
        get_operator(bl_idname).get_rna_type()
    except Exception:
        return False
    return True


def get_operator_rna(bl_idname):
    return get_operator(bl_idname).get_rna_type()


def get_operator_label(bl_idname):
    try:
        return get_operator_rna(bl_idname).bl_rna.name
    except Exception:
        return normalize_bl_idname(bl_idname) or "No Operator"


def get_operator_description(bl_idname):
    try:
        return get_operator_rna(bl_idname).bl_rna.description
    except Exception:
        return ""


def is_runtime_property(prop):
    identifier = prop.identifier
    return (
        identifier in RUNTIME_PROPERTY_NAMES
        or identifier.startswith("filter_")
        or identifier == "rna_type"
        or getattr(prop, "is_readonly", False)
    )


def iter_operator_properties(bl_idname):
    try:
        properties = get_operator_rna(bl_idname).properties
    except Exception:
        return []

    items = []
    for prop in properties:
        if is_runtime_property(prop):
            continue
        try:
            default = prop.default
        except Exception:
            default = ""
        enum_items = []
        if prop.type == "ENUM":
            try:
                enum_items = [item.identifier for item in prop.enum_items]
            except Exception:
                enum_items = []
        items.append(
            {
                "identifier": prop.identifier,
                "name": prop.name,
                "description": prop.description,
                "type": prop.type,
                "default": default,
                "enum_items": enum_items,
            }
        )
    return items


def default_property_value(prop_info):
    value = prop_info.get("default", "")
    if prop_info.get("type") == "ENUM" and not value:
        enum_items = prop_info.get("enum_items") or []
        value = enum_items[0] if enum_items else ""
    return str(value)


def iter_registered_operators():
    operators = []
    for category in dir(bpy.ops):
        if category.startswith("_"):
            continue
        try:
            op_module = getattr(bpy.ops, category)
        except Exception:
            continue
        for name in dir(op_module):
            if name.startswith("_"):
                continue
            bl_idname = f"{category}.{name}"
            try:
                rna = get_operator_rna(bl_idname)
            except Exception:
                continue
            label = rna.bl_rna.name
            if not label or label == bl_idname:
                continue
            operators.append((bl_idname, label, rna.bl_rna.description or ""))
    return sorted(operators, key=lambda item: (item[1].lower(), item[0]))
