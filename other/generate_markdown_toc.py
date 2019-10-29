#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
"""
author: song.yanlin
mail: hanxiao2100@qq.com


功能: 给markdown文档生成目录

用法: python generate_markdown_toc.py markdown文件路径

"""

import sys


class GenTOC(object):
    """处理markdown文档,生成toc目录."""

    count = 0 # 调用toc_concat 方法的次数

    def __init__(self, file_path):
        self.file_path = file_path
        self.fp = self._open_file() # 打开的文件句柄
        self.toc = ''  # 目录
        self.lines = []  # 接受读取文件所有行

    def _open_file(self):
        fp = open(self.file_path, "r+", encoding='utf-8')
        return fp

    def _save_file(self):
        """写入目录到源文件中并保存

        :return: bool
            目录是否成功写入源文件
            True: 是
            False: 没有生成目录，文件为重写
        """
        if self.toc:
            self.fp.seek(0, 0)
            self.fp.writelines(self.lines)
            self.fp.flush()
            self.fp.close()
            return True
        else:
            self.fp.close()
            return False

    def anchor_filter(self, anchor : str) -> str:
        """处理锚点内容中的特殊字符

        如空格改为-
        , ， 、 ( ) [ ] < > # ! ！ ?特殊字符直接去掉

        :param anchor: str
            锚点内容
        :return: str
            处理后的锚点内容
        """
        anchor = anchor.strip()
        ret = anchor.replace(' ', '-')
        ret = ret.replace(',', '')
        ret = ret.replace('，', '')
        ret = ret.replace('(', '')
        ret = ret.replace(')', '')
        ret = ret.replace('[', '')
        ret = ret.replace(']', '')
        ret = ret.replace('<', '')
        ret = ret.replace('>', '')
        ret = ret.replace('#', '')
        ret = ret.replace('?', '')
        ret = ret.replace('？', '')
        ret = ret.replace('!', '')
        ret = ret.replace('！', '')
        return ret

    def _toc_concat(self, title, title_leve):
        """目录拼接

        :param title: str
            标题内容，未过滤处理
        :param title_leve: int
            标题级别，范围[1, 6]
        :return: None
        """
        if self.count == 0:
            self.toc = '# Table Of Contents\n'
        title = title.split('\n')[0]
        anchor = self.anchor_filter(title)
        # 一条目录格式：
        # 空格* [链接文本](#锚点)
        self.toc = '%s%s* [%s](#%s)\n' %(self.toc, ' ' * 4 * (title_leve - 1), title, anchor)
        self.count = self.count + 1

    def _find_title(self):
        """查找标题

        遍历所有行查找标题，调用toc_concat目录拼接方法

        :return:
        """
        self.lines = self.fp.readlines()
        h1 = '#'
        h2 = '#' * 2
        h3 = '#' * 3
        h4 = '#' * 4
        h5 = '#' * 5
        h6 = '#' * 6
        h1_b2 = '=='  # 一级标题另外一种写法
        h2_b2 = '--'  # 二级标题另外一种写法
        # for line in self.lines:
        for i in range(len(self.lines)):
            if i == 0 or (i == 1): # 跳过最前面两行
                continue
            line = self.lines[i]
            line_split = []
            title_leve = 0
            if line.startswith(h6):
                line_split = line.split(h6)
                title_leve = 6
            elif line.startswith(h5):
                line_split = line.split(h5)
                title_leve = 5
            elif line.startswith(h4):
                line_split = line.split(h4)
                title_leve = 4
            elif line.startswith(h3):
                line_split = line.split(h3)
                title_leve = 3
            elif line.startswith(h2_b2):
                line_split = [0, self.lines[i - 1]]
                title_leve = 2
            elif line.startswith(h2):
                line_split = line.split(h2)
                title_leve = 2
            elif line.startswith(h1_b2):
                line_split = [0, self.lines[i -1]]
                title_leve = 1
            elif line.startswith(h1):
                line_split = line.split(h1)
                title_leve = 1

            if title_leve != 0:
                self._toc_concat(line_split[1], title_leve)

    def insert_toc(self):
        """向源文件头部插入目录

        :return: bool
            True: 已插入目录到self.lines
            False: 没有目录要插入
        """
        if self.toc:
            self.toc = self.toc + '\n\n'
            self.lines.insert(3, self.toc)
            return True
        else:
            return False

    def start(self):
        """开始执行

        :return:
        """
        self._find_title()
        try:
            self.insert_toc()
            status = self._save_file()
            if status:
                print('目录已经成功生成')
            else:
                print('无标题内容，未生成目录.')
        except Exception as e:
            print(e)


if __name__ == '__main__':
    if len(sys.argv) >= 2:
        file_path = sys.argv[1]
        gtoc = GenTOC(file_path)
        gtoc.start()
    else:
        print('请输入markdwon文件路径')