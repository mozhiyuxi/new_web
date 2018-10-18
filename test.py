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

x = [{123:123}, {123:123}]
x = []
print([xx[123] if xx else None for xx in x])
print([xx[123] for xx in x])
i = 0
seq = ['one', 'two', 'three']
for x in enumerate(seq):
    print(x)

import qiniu
access_key = "X78oHPbfASfWQ8gzVzwDeRd2a1mKEMUefYBgKCVI"
secret_key = "kxDYcWZcJKBsRbxWkVcyfWTbvllCjOvMQ81YYFTp"
bucket_name = "py-04-yun"

def test(file):
    q = qiniu.Auth(access_key, secret_key)
    token = q.upload_token(bucket_name)
    ret, info = qiniu.put_data(token, None, file)
    if ret is not None:
        print('All is OK')
    else:
        print(info) # error message in info


if __name__ == '__main__':
    file_location = input("文件位置")
    with open(file_location, "rb") as f:
        test(f.read())