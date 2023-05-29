# -*- coding: utf-8 -*-
# ************************************************************************
# * Software:  DataPreProcess  for  Python                               *
# * Version:  1.0.0                                                      *
# * Date:  2023-03-30 00:00:00                                           *
# * Last  update: 2023-03-30 00:00:00                                    *
# * License:  LGPL v1.0                                                  *
# * Maintain  address:  https://pan.baidu.com/s/1SKx3np-9jii3Zgf1joAO4A  *
# * Maintain  code:  STBM                                                *
# ************************************************************************

import threading
import time
from pandas import DataFrame
from Program.MachineInformation import MachineInformation
from Program.DataInput import DataInput
from Program.IndexCalculation import RockBreakingIndex
from Program.DataExtract import DataExtract


class DataPreProcess(threading.Thread):
    """数据预处理"""

    def __init__(self, shared_data):
        """
        初始化各参量，请勿修改
        :param shared_data: 共享变量
        """
        super(DataPreProcess, self).__init__()
        self._stop_event = threading.Event()

        self.Var = shared_data  # 引入共享，使其变为可编辑状态
        self.last_time = '2008-08-08 12:00:00'
        self.input = DataInput()
        self.extract = DataExtract()
        self.machine = MachineInformation()
        self.break_index = RockBreakingIndex()

    def run(self):
        """
        运行线程内的代码，请勿修改
        self.shared_Var.RawVar为原始的每秒数据记录，格式为DataFrame
        self.shared_Var为待汇总的数据记录，格式为dict
        """
        self.Var.ShowVar['刀盘转速-容许'] = self.machine['刀盘转速-容许']
        self.Var.ShowVar['推进速度-容许'] = self.machine['推进速度-容许']
        self.Var.ShowVar['刀盘扭矩-容许'] = self.machine['刀盘扭矩-容许']
        self.Var.ShowVar['刀盘推力-容许'] = self.machine['刀盘推力-容许']
        self.Var.ShowVar['贯入度-容许'] = self.machine['贯入度-容许']
        self.Var.ShowVar['刀盘转速-脱困'] = self.machine['刀盘转速-脱困']
        self.Var.ShowVar['推进速度-脱困'] = self.machine['推进速度-脱困']
        self.Var.ShowVar['刀盘扭矩-脱困'] = self.machine['刀盘扭矩-脱困']
        self.Var.ShowVar['刀盘推力-脱困'] = self.machine['刀盘推力-脱困']
        self.Var.ShowVar['贯入度-脱困'] = self.machine['贯入度-脱困']
        while not self._stop_event.is_set():
            self.Timer()
            time.sleep(1)
        print('\033[0;33m%s -> Thread stopped.\n\033[0m' % self.__class__.__name__)

    def stop(self):
        self._stop_event.set()

    def Timer(self):
        real_data, self.Var.ShowVar['PLC状态'] = self.input.run(Type='YS')
        self.Var.Real = real_data
        if self.Var.ShowVar['PLC状态']:
            self.Var.ShowVar['运行时间'] = real_data['运行时间']
            self.Var.ShowVar['里程'] = round(real_data['里程'], 2)
            self.Var.ShowVar['刀盘转速-当前'] = round(real_data['刀盘转速'], 2)
            self.Var.ShowVar['推进速度-当前'] = round(real_data['推进速度'], 2)
            self.Var.ShowVar['刀盘扭矩-当前'] = round(real_data['刀盘扭矩'], 2)
            self.Var.ShowVar['刀盘推力-当前'] = round(real_data['刀盘推力'], 2)
            real_P = (real_data['推进速度'] / real_data['刀盘转速']) if real_data['刀盘转速'] > 0 else 0.0
            self.Var.ShowVar['贯入度-当前'] = round(real_P, 2)
            self.Var.ShowVar['施工状态'] = self.extract.stage_judge(data=real_data)  # 当前状态('停机中', '等待掘进', '空推中', '正在掘进')
        key_data, passed_data = self.extract.run()
        if self.Var.ShowVar['施工状态'] == '正在掘进':
            if len(passed_data) > 0 and passed_data[-1]['运行时间'][0] != self.last_time:
                self.Var.ShowVar['刀盘转速-之前'] = round(passed_data[-1].loc[:, '刀盘转速'].mean(), 2)
                self.Var.ShowVar['推进速度-之前'] = round(passed_data[-1].loc[:, '推进速度'].mean(), 2)
                self.Var.ShowVar['刀盘扭矩-之前'] = round(passed_data[-1].loc[:, '刀盘扭矩'].mean(), 2)
                self.Var.ShowVar['刀盘推力-之前'] = round(passed_data[-1].loc[:, '刀盘推力'].mean(), 2)
                last_P = (self.Var.ShowVar['推进速度-之前'] / self.Var.ShowVar['刀盘转速-之前']
                          ) if self.Var.ShowVar['刀盘转速-之前'] > 0 else 0.0
                self.Var.ShowVar['贯入度-之前'] = round(last_P, 2)
                self.last_time = passed_data[-1]['运行时间'][0]
            rock_index = self.break_index.run(data=key_data)
            self.Var.ShowVar['TPI-平均'] = rock_index.loc[0, 'TPI_mean']
            self.Var.ShowVar['FPIa-平均'] = rock_index.loc[0, 'a']
            self.Var.ShowVar['FPIb-平均'] = rock_index.loc[0, 'b']
            self.Var.BasicVar = {'rock-index': rock_index, 'raw-data': key_data, 'passed-data': passed_data}
        else:
            self.Var.BasicVar = {'rock-index': DataFrame(), 'raw-data': DataFrame(), 'passed-data': passed_data}
