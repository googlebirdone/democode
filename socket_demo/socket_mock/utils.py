#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2023/7/18 17:51
# @Author  : GuQingJun
# @Site    : 
# @File    : utils.py
# @Software: PyCharm
import threading
import socket
from typing import Literal


class Utils:
    def __init__(self):
        pass

    def _build_xml(self, ):
        pass

    @staticmethod
    def _int2bytes(num: int, byte_len, byte_type: Literal['little', 'big']):
        return num.to_bytes(byte_len, byte_type)




