# -*- coding: utf-8 -*-
# @Time    : 2018/10/13 11:09
# @Author  : Medo-z
# @Site    : 
# @File    : test.py
# @Software: PyCharm

# 测试python交互redis

from redis import StrictRedis

sr = StrictRedis()
sr.set("name", "laowang")

