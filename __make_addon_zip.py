# coding: UTF-8
import os
from pathlib import Path
import zipfile
import shutil

parent_path = Path(__file__).parent


def get_tg_dir() -> Path:
    tg_dir = parent_path.joinpath(parent_path.name)
    if tg_dir.exists():
        shutil.rmtree(tg_dir)
    tg_dir.mkdir()

    return tg_dir


def copy_files() -> Path:
    tg_dir = get_tg_dir()
    sub_dir = tg_dir.joinpath(parent_path.name)
    sub_dir.mkdir()

    for file in parent_path.glob('*'):
        if file.is_dir():
            if file.name == parent_path.name: continue
            if file.name.startswith('__') or file.name.startswith('.'): continue
            if file.is_dir() and file.name == 'docs': continue

            shutil.copytree(file, sub_dir.joinpath(file.name))

        elif file.is_file():
            if file.name == __file__: continue

            shutil.copy(file, sub_dir.joinpath(file.name))

    return tg_dir


def get_bl_addon_info() -> dict:
    import re
    rule = re.compile(r'bl_info\s*=\s*{.*?}', re.DOTALL)
    with open(parent_path.joinpath('__init__.py'), 'r', encoding='utf-8') as f:
        _bl_info = rule.findall(f.read())

    if not _bl_info:
        raise RuntimeError('bl_info not found')
    bl_info = eval(_bl_info[0].split('=')[1])

    return bl_info


def zip_dir():
    # read bl_info
    bl_info = get_bl_addon_info()
    print(f'Addon name: {bl_info.get("name", "")}')
    print(f'Version: {bl_info.get("version", "")}')

    tg_dir = copy_files()
    final_name = parent_path.name + ' v' + '.'.join([str(num) for num in bl_info['version']]) + '.zip'
    zip_file = parent_path.joinpath(final_name)
    if zip_file.exists():
        os.remove(zip_file)

    with zipfile.ZipFile(zip_file, 'w') as zip:
        for root, dirs, files in os.walk(tg_dir):
            for file in files:
                zip.write(os.path.join(root, file), arcname=os.path.join(root, file).replace(str(tg_dir), ''))
    print(f'Output: "{zip_file}"')
    shutil.rmtree(tg_dir)
    print('Cleaning')


if __name__ == '__main__':
    copy_files()
    zip_dir()


