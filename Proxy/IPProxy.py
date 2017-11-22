#! /usr/bin/env python
# -*- coding utf-8 -*-
# 使用ProxyPool获取了足够的IP地址
import requests as rq
import random
import ast


def getIPProxies():
    url = 'http://47.104.17.141:5010/get_all'  # Proxy IP Server
    IPAddr = rq.get(url).text
    IPAddr = ast.literal_eval(IPAddr)  # String to List Conversion
    # print(type(IPAddr))
    max = len(IPAddr)
    item = random.randint(0, max - 1)
    proxies = {
        "https": "https://{}" .format(IPAddr[item])
    }
    print("Using Proxy at {}".format(proxies))  # Will be Removed!
    return proxies
