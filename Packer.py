import os
import time
import json
import shutil
import zipfile

LOCAL_TIME = time.localtime()
TIME = time.strftime("%Y/%m/%d %H:%M:%S", LOCAL_TIME)
VERSION = time.strftime("%Y%m%d%H%M%S", LOCAL_TIME)


def touch_dir(path: str):
    """
    Create folder if not exist.
    :param path: Folder path.
    """
    if not os.path.isdir(path):
        os.makedirs(path)


def copy(file_path: str, check_dir: bool = True):
    """
    Copy file to release folder.
    :param file_path: File path.
    :param check_dir: Enable check dir exist.
    """
    target_path = os.path.join(VERSION, file_path)
    if check_dir:
        touch_dir(os.path.dirname(target_path))
    shutil.copyfile(file_path, target_path)


def main():
    # Touch folder
    touch_dir(VERSION)

    # Basic files
    copy('LICENSE', False)
    copy('pack.png', False)
    copy('README.md', False)
    with open(
            os.path.join(VERSION, 'pack.mcmeta'),
            'w',
            encoding='utf-8'
    ) as f:
        json.dump({
            "pack": {
                "pack_format": 6,
                "description": f"§d安逸汉化组§r\n打包时间：{TIME}"
            }
        }, f, indent=2, ensure_ascii=False)

    # Copy assets
    for mod_id in os.listdir('assets'):
        file_path = os.path.join('assets', mod_id, 'lang', 'zh_cn.json')
        if os.path.isfile(file_path):
            copy(file_path)

    # Set version
    print(f'::set-output name=version::{VERSION}')

if __name__ == '__main__':
    main()
