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
import re


class GenTOC(object):
    """处理markdown文档,生成toc目录."""

    count = 0 # 调用toc_concat 方法的次数

    def __init__(self, file_path):
        self.file_path = file_path
        self.fp = self._open_file()  # 打开的文件句柄
        self.toc = ''  # 目录内容
        self.title_info = []  # 用于记录标题信息，结构：[{'title': title, 'level': title_leve}, ]
        self.lines = []  # 接受读取文件所有行
        self.is_in_codeblock_flag = False  # 是否进入代码块内，默认为否

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
        if len(self.title_info) != 0 and self.toc:
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
        ,，、()[]<>#!！?\"'“”~+＋:：%$特殊字符直接去掉

        :param anchor: str
            锚点内容
        :return: str
            处理后的锚点内容
        """
        s = " ,，、()[]<>#!！?\"'“”~+＋:：%$"
        anchor = anchor.strip()
        for i in s:
            if i == ' ':
                anchor = anchor.replace(i, '-')
            else:
                anchor = anchor.replace(i, '')
        return anchor

    def _record_title_info(self, title, title_leve):
        """记录找到的标题信息

        每调用一次记录一行传递过来的标题信息到self.toc列表中

        :param title: str
            标题内容，未过滤处理
        :param title_leve: int
            标题级别，范围[1, 6]
        :return: None
        """
        if len(title) > 0 and (title_leve >= 1 and title_leve <= 6):
            if len(title.strip()) == 0:
                return None
            title_dic = {'title': title, 'level': title_leve}
            self.title_info.append(title_dic)

    def _toc_concat(self):
        """目录拼接

        :return: None
        """
        if len(self.title_info) == 0:
            return
        self.toc = '# Table Of Contents\n'

        highest_title_level = 6
        # 找出标题级别最高的值
        for t in self.title_info:
            if t['level'] < highest_title_level:
                highest_title_level = t['level']

        # 一条目录格式：
        # 空格* [链接文本](#锚点)
        regex = r"\s*\[(\S+)]((\S+))"  # 标题内容原本就是一个连接，对于这种标题直接保留，如：[...](...)
        for i in self.title_info:
            title = i['title'].strip()
            if re.match(regex, title):
                self.toc = self.toc + title + '\n'
            else:
                anchor = self.anchor_filter(title)
                level = i['level']
                self.toc = '%s%s* [%s](#%s)\n' % (self.toc, ' ' * 4 * (level - highest_title_level), title, anchor)

    def _is_in_codeblock(self, line_content):
        """是否在代码块内

        :param line_content: str
            一行文本内容
        :return: bool
            True: 是
            False: 否
        """
        line_content = line_content.strip()

        # 代码块```开头行
        if not self.is_in_codeblock_flag:
            if line_content.startswith('```'):
                # 一行代码块排除, 如：```  ```
                if len(line_content) != 3:
                    if line_content.endswith('```'):
                        return self.is_in_codeblock_flag
                self.is_in_codeblock_flag = True

        # 已经进入代码块内，判断是否为代码块结束符，代码块结束符为'```'
        if self.is_in_codeblock_flag:
            if line_content == '```':
                self.is_in_codeblock_flag = False
            elif line_content.endswith('```') and (not line_content.endswith('\```')):
                self.is_in_codeblock_flag = False

        return self.is_in_codeblock_flag

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
        h1_b2 = '=='  # 一级标题另外一种写法，且优先于h2写法
        h2_b2 = '--'  # 二级标题另外一种写法，且优先于h1写法

        for i in range(len(self.lines)):
            if i == 0 or (i == 1): # 跳过最前面两行
                continue
            line = self.lines[i]
            line_split = []
            title_leve = 0
            # 行在代码块内跳过
            if self._is_in_codeblock(line):
                continue

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
                # # 排除```开头的文本块情况
                # if self.lines[i - 1].startswith('```'):
                #     continue
                # # 排除上一行--开头的文本块情况，在sql文本块里为注释
                # if self.lines[i - 1].startswith('--'):
                #     continue
                title_leve = 2
            elif line.startswith(h2):
                line_split = line.split(h2)
                title_leve = 2
            elif line.startswith(h1_b2):
                line_split = [0, self.lines[i -1]]
                # # 排除上一行```开头的文本块情况
                # if self.lines[i -1].startswith('```'):
                #     continue
                # # 排除上一行--开头的文本块情况，在sql文本块里为注释
                # if self.lines[i -1].startswith('--'):
                #     continue
                title_leve = 1
            elif line.startswith(h1):
                line_split = line.split(h1)
                title_leve = 1

            if title_leve != 0:
                title = line_split[1].split('\n')[0]  # 把标题的换行符去掉
                title = title.strip()
                self._record_title_info(title, title_leve)

    def _insert_toc(self):
        """向源文件头部插入目录

        :return: bool
            True: 已插入目录到self.lines
            False: 没有目录要插入
        """
        self._toc_concat()
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
            self._insert_toc()
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