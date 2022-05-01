import os
import re
import shutil
import zipfile

import hjson
import requests

from typing import Dict

PATTERN = re.compile(r'assets/(?P<mod_id>.+?)/lang/(?P<language>.+?)\.json')
TEMP_DIR = 'temp'
RESOURCEPACK_DIR = os.path.join(TEMP_DIR, 'resourcepack')
MODS_DIR = os.path.join(TEMP_DIR, 'assets')


def touch_dir(path: str):
    """
    Create folder if not exist.
    :param path: Folder path.
    """
    if not os.path.isdir(path):
        os.makedirs(path)


def match_lang(path):
    return PATTERN.match(path)


def unzip(file_path, dir_name):
    with zipfile.ZipFile(file_path) as archive:
        for file in archive.namelist():
            if match_lang(file):
                archive.extract(file, dir_name)


def get_resourcepack_lang() -> None:
    """
    获取汉化材质语言文件
    """
    # 下载CFPA汉化包
    cfpa_release_list = requests.get(
        'https://api.github.com/repos/CFPAOrg/Minecraft-Mod-Language-Package/releases'
    ).json()
    cfpa_pack_path = ''
    for i in cfpa_release_list:
        cfpa_pack_info = i['assets'][0]
        cfpa_pack_name = cfpa_pack_info['name']
        if '1.16' in cfpa_pack_name:
            cfpa_pack_path = os.path.join('temp', cfpa_pack_name)
            with open(cfpa_pack_path, 'wb') as file:
                file.write(
                    requests.get(cfpa_pack_info['browser_download_url']).content
                )
            break
    unzip(cfpa_pack_path, RESOURCEPACK_DIR)
    os.remove(cfpa_pack_path)

    # 下载傻白甜汉化包
    anyi_release_info = requests.get(
        'https://gitee.com/api/v5/repos/ShaBaiTianCN/Minecraft-Mod-Language-Package-Not-Included-Language-Package/releases/latest'
    ).json()['assets'][0]
    anyi_pack_path = os.path.join('temp', anyi_release_info['name'])
    with open(anyi_pack_path, 'wb') as f:
        f.write(requests.get(anyi_release_info['browser_download_url']).content)
    unzip(anyi_pack_path, RESOURCEPACK_DIR)
    os.remove(anyi_pack_path)


def get_mods_lang(path: str) -> None:
    """
    提取模组的语言文件
    :param path: mods 文件夹路径
    :return: None
    """

    # 遍历模组列表
    for i in os.listdir(path):
        file_path = os.path.join(path, i)
        # 检查为jar文件
        if zipfile.is_zipfile(file_path):
            unzip(file_path, TEMP_DIR)

    # 整理文件
    for mod_id in os.listdir(MODS_DIR):
        mod_dir = os.path.join(MODS_DIR, mod_id)
        for dirpath, dirnames, filenames in os.walk(mod_dir):
            if 'lang' in dirpath:
                for file in filenames:
                    file_path = os.path.join(dirpath, file)
                    os.renames(file_path, file_path.replace('lang\\', ''))


def check_langs():
    def get_lang(path) -> Dict[str, str] or None:
        if os.path.isfile(path):
            with open(path, encoding='utf-8') as lang_file:
                return hjson.load(lang_file)
        else:
            return None

    resourcepack_assets_path = os.path.join(RESOURCEPACK_DIR, 'assets')
    for mod_id in os.listdir(MODS_DIR):
        mod_path = os.path.join(MODS_DIR, mod_id)
        en_us_path = os.path.join(mod_path, 'en_us.json')
        zh_cn_mod_path = os.path.join(mod_path, 'zh_cn.json')
        zh_tw_mod_path = os.path.join(mod_path, 'zh_tw.json')
        zh_cn_resourcepack_path = os.path.join(
            resourcepack_assets_path,
            mod_id,
            'lang',
            'zh_cn.json'
        )
        try:
            en_us = get_lang(en_us_path)
            zh_cn_mod = get_lang(zh_cn_mod_path)
            zh_tw_mod = get_lang(zh_tw_mod_path)
            zh_cn_resourcepack = get_lang(zh_cn_resourcepack_path)
        except Exception as e:
            print(f'Please check mod {mod_id}, an error occurs: {e}')
            continue

        # 合并汉化
        zh_cn = {}
        if zh_tw_mod is not None:
            zh_cn.update(zh_tw_mod)
        if zh_cn_resourcepack is not None:
            zh_cn.update(zh_cn_resourcepack)
        if zh_cn_mod is not None:
            zh_cn.update(zh_cn_mod)

        # 判断是否可以跳过
        ignore_flag = True
        for key in en_us.keys():
            if key not in zh_cn.keys():
                ignore_flag = False
                break
        if ignore_flag:
            shutil.rmtree(mod_path)
            continue

        # 创建新汉化文件
        new_zh_cn = en_us
        for key in zh_cn.keys():
            new_zh_cn[key] = zh_cn[key]
        with open(zh_cn_mod_path, 'w', encoding='utf-8') as f:
            hjson.dumpJSON(new_zh_cn, f, indent=4, ensure_ascii=False)


def main():
    mods_path = input('mods文件夹路径：')
    touch_dir(RESOURCEPACK_DIR)
    get_mods_lang(mods_path)
    get_resourcepack_lang()
    check_langs()


if __name__ == '__main__':
    main()
