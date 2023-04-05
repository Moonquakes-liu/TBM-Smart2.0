# -*- coding: utf-8 -*-
# ************************************************************************
# * Software:  RockPredict  for  Python                                  *
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


class RockPredict(threading.Thread):
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
            Random_rock_23 = random.randint(0, 100)
            Random_rock_45 = 100 - Random_rock_23
            self.shared_Var.Var['Ⅱ类Ⅲ类围岩概率'] = Random_rock_23
            self.shared_Var.Var['Ⅳ类Ⅴ类围岩概率'] = Random_rock_45
            self.shared_Var.Var['当前围岩类型'] = 'Ⅱ类 Ⅲ类' if Random_rock_23 > 50 else 'Ⅳ类 Ⅴ类'
            risk = '安全掘进' if Random_rock_23 > 40 else ('预警观察' if Random_rock_23 > 20 else '风险控制')
            self.shared_Var.Var['风险状态'] = risk
            self.shared_Var.Var['建议支护方式'] = '暂 无' if risk != '风险控制' else '立 拱'
        elif self.shared_Var.Var['施工状态'] == '停机中':
            self.shared_Var.Var['Ⅱ类Ⅲ类围岩概率'] = 0
            self.shared_Var.Var['Ⅳ类Ⅴ类围岩概率'] = 0
            self.shared_Var.Var['当前围岩类型'] = '——'
            self.shared_Var.Var['风险状态'] = '——'
            self.shared_Var.Var['建议支护方式'] = '——'
        time.sleep(30)  # 每秒读取一次，请勿修改

    def run(self):
        """运行线程内的代码，请勿修改"""
        while True:  # 循环运行
            self.loop()  # 运行代码
