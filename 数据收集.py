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


class SharedData:
    """创建一个共享变量库，任何子程序都可对其进行修改"""
    def __init__(self):
        """初始化各参量"""
        import threading
        from pandas import DataFrame
        self.RawVar = DataFrame()  # 以每秒为单位保存原始临时数据记录
        self.RawVar = DataFrame()  # 以每秒为单位保存原始临时数据记录
        self.Var = {'里程': 0, '运行时间': '2008-01-01 12:00:00', '刀盘转速-当前': 0, '刀盘转速设定值-当前': 0,
                    '推进速度-当前': 0, '推进速度设定值-当前': 0, '刀盘扭矩-当前': 0, '刀盘推力-当前': 0, '贯入度-当前': 0,
                    '刀盘转速-之前': 0, '推进速度-之前': 0, '刀盘扭矩-之前': 0, '刀盘推力-之前': 0, '施工状态': '停机中',
                    '当前围岩类型': '待生成', 'Ⅱ类Ⅲ类围岩概率': 0, 'Ⅳ类Ⅴ类围岩概率': 0, '建议支护方式': '无',
                    '风险状态': '安全掘进', '推荐刀盘转速': 0, '推荐推进速度': 0, '刀盘扭矩预测值': 0, '刀盘推力预测值': 0,
                    '滚刀磨损速率': '低'}  # 保存汇总后的临时变量
        self.lock = threading.Lock()  # 多线程锁，防止出现多个线程对变量同时进行修改而出现卡死现象


class DataCollect(object):
    """创建多个线程，并完成数据收集工作"""
    def __init__(self, program_name):
        """
        初始化各参量
        :param program_name: 要运行的子程序名称，例如 [Class-1,Class-2,...,Class-n]
        """
        self.values = share_data.Var
        self.threads = {}  # 保存子线程
        for num, fuc in enumerate(program_name):
            self.threads.update({'sub-function-%d' % num: fuc(share_data)})  # 创建子线程
        for thread in self.threads.values():
            thread.start()  # 启动子线程


share_data = SharedData()  # 实例化共享变量库
