import os
import re
import zipfile
import requests
from typing import List

PATTERN = re.compile(r'assets/(?P<mod_id>.+?)/lang/(?P<language>.+?)\.json')


def match_lang(path):
    return PATTERN.match(path)


def get_exist_mod_id() -> List[str]:
    """
    获取 Language Package 已有模组列表
    """
    return_list = []

    # 使用 GitHub API 获取所有 Release
    release_list = requests.get(
        'https://api.github.com/repos/CFPAOrg/Minecraft-Mod-Language-Package/releases'
    ).json()
    pack_name = ''

    # 下载最新版1.16汉化包
    for i in release_list:
        pack_info = i['assets'][0]
        if '1.16' in pack_info['name']:
            pack_name = pack_info['name']
            with open(pack_info['name'], 'wb') as file:
                file.write(
                    requests.get(pack_info['browser_download_url']).content
                )
            break

    # 遍历列表获取 ModID
    with zipfile.ZipFile(pack_name) as archive:
        for file in archive.namelist():
            match = match_lang(file)
            if match:
                return_list.append(match.groupdict()['mod_id'])

    os.remove(pack_name)
    return list(set(return_list))


def extract_lang(path: str, blacklist: List[str]) -> None:
    """
    提取模组的语言文件
    :param path: jar文件路径
    :param blacklist: 黑名单
    :return: None
    """
    extract_list = []
    with zipfile.ZipFile(path) as archive:
        # 遍历压缩包文件
        for file in archive.namelist():
            # 匹配正则为语言文件
            match = match_lang(file)
            if match:
                info = match.groupdict()
                # 忽略已有汉化
                if info['language'] == 'zh_cn' or info['mod_id'] in blacklist:
                    return
                # 保存其他文件
                elif info['language'] in ['en_us', 'zh_hk', 'zh_tw']:
                    extract_list.append(file)
        # 解压语言文件
        for i in extract_list:
            archive.extract(i, os.path.join('temp', 'Extracted'))


def main():
    dir_path = input('mods文件夹路径：')
    blacklist = get_exist_mod_id()
    for i in os.listdir(dir_path):
        file_path = os.path.join(dir_path, i)
        # 检查为jar文件
        if zipfile.is_zipfile(file_path):
            extract_lang(file_path, blacklist)


if __name__ == '__main__':
    main()
