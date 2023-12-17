import bpy
import yaml
from pathlib import Path


def enum_imexporter(self, context) -> dict[str, list[dict]]:
    """Read imexporter from yaml file and return a dict

    Returns:
        dict[category:str, list[dict]]
    example:
        {
        'Import': [
            {
                'name': 'Collada (.dae)',
                'bl_idname': 'import_dae',
                ...
                },
            ...
            ],
        'Export': [
            {},
            ...
            ],
        ...
        }
    """
    # version = bpy.app.version
    # if version >= (4,0,0):
    p = Path(__file__).parent.joinpath('4.0')

    catalog_item_dict = {}

    for file in p.iterdir():
        if file.suffix != '.yaml': continue

        with open(file, 'r', encoding='utf-8') as f:
            data = yaml.load(f, Loader=yaml.FullLoader)
            # print(data)

        for item in data:
            category = item['category']
            if category not in catalog_item_dict:
                catalog_item_dict[category] = []
            catalog_item_dict[category].append(item)

    # print(catalog_item_dict)
    return catalog_item_dict


# enum_imexporter(None, None)
