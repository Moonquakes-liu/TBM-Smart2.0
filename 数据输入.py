#!/usr/bin/env python
# -*- coding: utf-8 -*-
# ************************************************************************
# * Software:  DataInput  for  Python                                    *
# * Version:  1.0.0                                                      *
# * Date:  2023-03-30 00:00:00                                           *
# * Last  update: 2023-03-30 00:00:00                                    *
# * License:  LGPL v1.0                                                  *
# * Maintain  address:  https://pan.baidu.com/s/1SKx3np-9jii3Zgf1joAO4A  *
# * Maintain  code:  STBM                                                *
# ************************************************************************

import threading
import time
import pandas as pd


class DataInput(threading.Thread):
    """数据输入"""
    def __init__(self, shared_Var):
        """
        初始化各参量
        :param shared_Var: 共享变量
        """
        threading.Thread.__init__(self)  # 实例化多线程库
        self.shared_Var = shared_Var  # 引入共享，使其变为可编辑状态
        self.data = pd.read_csv('D:\\浏览器下载\\百度云盘下载\\CREC188_20160517.csv', encoding='gb2312')  # 读取文件

    def loop(self):
        """
        待运行的代码
        self.shared_Var.RawVar为原始的每秒数据记录，格式为DataFrame
        self.shared_Var为待汇总的数据记录，格式为dict
        """
        for num in range(self.data.shape[0]):
            self.shared_Var.RawVar = self.data.loc[num, :]
            self.shared_Var.Var['里程'] = self.data.loc[num, '桩号']
            self.shared_Var.Var['运行时间'] = self.data.loc[num, '运行时间']
            self.shared_Var.Var['刀盘转速-当前'] = self.data.loc[num, '刀盘转速']
            self.shared_Var.Var['刀盘转速设定值-当前'] = self.data.loc[num, '刀盘转速']
            self.shared_Var.Var['推进速度-当前'] = self.data.loc[num, '推进速度']
            self.shared_Var.Var['推进速度设定值-当前'] = self.data.loc[num, '推进速度']
            self.shared_Var.Var['刀盘扭矩-当前'] = self.data.loc[num, '刀盘扭矩']
            self.shared_Var.Var['刀盘推力-当前'] = self.data.loc[num, '总推进力']
            if self.data.loc[num, '刀盘转速'] != 0:
                self.shared_Var.Var['贯入度-当前'] = self.data.loc[num, '推进速度'] / self.data.loc[num, '刀盘转速']
            else:
                self.shared_Var.Var['贯入度-当前'] = 0
            time.sleep(1)  # 每秒读取一次，请勿修改

    def run(self):
        """运行线程内的代码，请勿修改"""
        while True:  # 循环运行
            self.loop()  # 运行代码
