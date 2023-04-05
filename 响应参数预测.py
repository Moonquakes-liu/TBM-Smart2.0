# -*- coding: utf-8 -*-
# ************************************************************************
# * Software:  ParmPredict  for  Python                                  *
# * Version:  1.0.0                                                      *
# * Date:  2023-03-30 00:00:00                                           *
# * Last  update: 2023-03-30 00:00:00                                    *
# * License:  LGPL v1.0                                                  *
# * Maintain  address:  https://pan.baidu.com/s/1SKx3np-9jii3Zgf1joAO4A  *
# * Maintain  code:  STBM                                                *
# ************************************************************************
import random
import threading
import time


class ParmPredict(threading.Thread):
    """施工状态判断"""
    def __init__(self, shared_Var):
        """
        初始化各参量
        :param shared_Var: 共享变量
        """
        threading.Thread.__init__(self)  # 实例化多线程库
        self.shared_Var = shared_Var  # 引入共享，使其变为可编辑状态

    def loop(self):
        """
        待运行的代码
        self.shared_Var.RawVar为原始的每秒数据记录，格式为DataFrame
        self.shared_Var为待汇总的数据记录，格式为dict
        """
        if self.shared_Var.Var['施工状态'] == '正在掘进':
            Random_F = random.randint(500000, 2500000)
            Random_T = random.randint(100000, 500000)
            abrasion = '中'
            if Random_F < (500000 + 0.5 * (2500000 - 500000)) and Random_T < (100000 + 0.5 * (500000 - 100000)):
                abrasion = '低'
            elif Random_F > (500000 + 0.8 * (2500000 - 500000)) and Random_T > (100000 + 0.8 * (500000 - 100000)):
                abrasion = '高'
            self.shared_Var.Var['刀盘扭矩预测值'] = Random_T / 100
            self.shared_Var.Var['刀盘推力预测值'] = Random_F / 100
            self.shared_Var.Var['滚刀磨损速率'] = abrasion
        elif self.shared_Var.Var['施工状态'] == '停机中':
            self.shared_Var.Var['刀盘扭矩预测值'] = 0
            self.shared_Var.Var['刀盘推力预测值'] = 0
            self.shared_Var.Var['滚刀磨损速率'] = '——'

        time.sleep(5)  # 每秒读取一次，请勿修改

    def run(self):
        """运行线程内的代码，请勿修改"""
        while True:  # 循环运行
            self.loop()  # 运行代码
