#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
"""
author: song.yanlin
mail: hanxiao2100@qq.com
"""

"""
功能: 给markdown文档生成目录

用法:
"""

class GenTOC(object):
    """处理markdown文档,生成toc目录."""

    def __init__(self, file_path):
        self.file_path = file_path
        self.fp = self.open_file() # 打开的文件句柄

    def open_file(self):
        fp = open(self.file_path, "r+")
        return fp

    def anchor_filter1(self, anchor: str) -> str:
        """锚点内容含空格过滤处理

        :param anchor: str
            锚点内容
        :return: str
            过滤后的锚点内容
        """
        return anchor.replace(' ', '-')

    def anchor_filter2(self, anchor):
        """锚点内容含"("或")"过滤处理

        :param anchor: str
            锚点内容
        :return: str
            过滤后的锚点内容
        """
        ret = anchor.replace('(', '')
        ret = ret.replace(')', '')
        return ret


