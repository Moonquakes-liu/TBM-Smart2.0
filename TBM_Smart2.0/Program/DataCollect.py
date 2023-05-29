#!/usr/bin/env python
# -*- coding: utf-8 -*-
# ************************************************************************
# * Software:  DataCollect and SharedData  for  Python                   *
# * Version:  1.0.0                                                      *
# * Date:  2023-03-30 00:00:00                                           *
# * Last  update: 2023-03-30 00:00:00                                    *
# * License:  LGPL v1.0                                                  *
# * Maintain  address:  https://pan.baidu.com/s/1SKx3np-9jii3Zgf1joAO4A  *
# * Maintain  code:  STBM                                                *
# ************************************************************************
import threading
from pandas import DataFrame
import time


class SharedData(object):
    """创建一个共享变量库，任何子程序都可对其进行修改"""

    def __init__(self):
        """初始化各参量"""
        self.BasicVar = {'rock-index': DataFrame(), 'raw-data': DataFrame(), 'passed-data': []}  # 以每秒为单位保存用于模型预测临时数据记录
        self.History = []
        self.Real = DataFrame()  # 以每秒为单位保存用于模型预测临时数据记录
        self.ShowVar = {'PLC状态': False, '里程': 0, '运行时间': '2008-01-01 12:00:00',
                        '刀盘转速-当前': '--', '推进速度-当前': '--', '刀盘扭矩-当前': '--', '刀盘推力-当前': '--', '贯入度-当前': '--',
                        '刀盘转速-预测': '--', '推进速度-预测': '--', '刀盘扭矩-预测': '--', '刀盘推力-预测': '--', '贯入度-预测': '--',
                        '刀盘转速-之前': '--', '推进速度-之前': '--', '刀盘扭矩-之前': '--', '刀盘推力-之前': '--', '贯入度-之前': '--',
                        '刀盘转速-容许': 9, '推进速度-容许': 120, '刀盘扭矩-容许': 4000, '刀盘推力-容许': 20000, '贯入度-容许': 20,
                        '刀盘转速-脱困': 12, '推进速度-脱困': 150, '刀盘扭矩-脱困': 5000, '刀盘推力-脱困': 25000, '贯入度-脱困': 25,
                        '施工状态': '停机中', '当前围岩类型': '--', 'Ⅱ类Ⅲ类围岩概率': '--', 'Ⅳ类Ⅴ类围岩概率': '--',
                        '建议支护方式': '--', '风险状态': '--', 'TPI-平均': 0, 'FPIa-平均': 0, 'FPIb-平均': 0,
                        '推荐刀盘转速': '--', '推荐推进速度': '--', '滚刀磨损速率': '--', '渣片分析状况': '--'}  # 以每秒为单位保存用于展示的临时数据记录
        self.lock = threading.Lock()  # 多线程锁，防止出现多个线程对变量同时进行修改而出现卡死现象


class DataCollect(object):
    """创建多个线程，并完成数据收集工作"""

    def __init__(self, program_name):
        """
        初始化各参量
        :param program_name: 要运行的子程序名称，例如 [Class-1,Class-2,...,Class-n]
        """
        self.values = share_data
        self.threads = {}  # 保存子线程
        for num, fuc in enumerate(program_name):
            self.threads.update({'sub-function-%d' % num: fuc(share_data)})  # 创建子线程
        for thread in self.threads.values():
            thread.start()  # 启动子线程


share_data = SharedData()  # 实例化共享变量库
