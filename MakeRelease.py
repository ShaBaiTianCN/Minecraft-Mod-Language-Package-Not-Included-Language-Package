import os
import time
import shutil
import zipfile

NAME = 'Minecraft-Mod-Language-Package-Not-Included-Language-Package'
RELEASE_NAME = f'{NAME}-{time.strftime("%Y%m%d%H%M%S", time.localtime())}'
RELEASE_DIR = os.path.join('temp', RELEASE_NAME)


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
    target_path = os.path.join(RELEASE_DIR, file_path)
    if check_dir:
        touch_dir(os.path.dirname(target_path))
    shutil.copyfile(file_path, target_path)


def main():
    # Touch folder
    touch_dir(RELEASE_DIR)

    # Copy base files
    copy('LICENSE', False)
    copy('pack.mcmeta', False)
    copy('pack.png', False)
    copy('README.md', False)

    # Copy assets
    for mod_id in os.listdir('assets'):
        file_path = os.path.join('assets', mod_id, 'lang', 'zh_cn.json')
        if os.path.isfile(file_path):
            copy(file_path)

    # Make Zipfile
    with zipfile.ZipFile(
            f'{RELEASE_DIR}.zip',
            mode='w',
            compression=zipfile.ZIP_DEFLATED
    ) as archive:
        for dirpath, dirnames, filenames in os.walk(RELEASE_DIR):
            for filename in filenames:
                file_path = os.path.join(dirpath, filename)
                archive.write(
                    file_path,
                    arcname=file_path.replace(RELEASE_DIR, '')
                )

    # Remove folder
    shutil.rmtree(RELEASE_DIR)


if __name__ == '__main__':
    main()