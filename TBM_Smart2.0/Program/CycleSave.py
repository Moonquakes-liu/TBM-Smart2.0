# -*- coding: utf-8 -*-
# ************************************************************************
# * Software:  CycleSave  for  Python                                    *
# * Version:  1.0.0                                                      *
# * Date:  2023-03-30 00:00:00                                           *
# * Last  update: 2023-03-30 00:00:00                                    *
# * License:  LGPL v1.0                                                  *
# * Maintain  address:  https://pan.baidu.com/s/1SKx3np-9jii3Zgf1joAO4A  *
# * Maintain  code:  STBM                                                *
# ************************************************************************
import copy
import os
import csv
import threading
import time
from datetime import datetime
import pandas as pd
from pandas import DataFrame


class CycleSave(threading.Thread):
    """循环段保存"""

    def __init__(self, shared_data):
        """
        初始化各参量，请勿修改
        :param shared_data: 共享变量
        """
        super(CycleSave, self).__init__()
        self._stop_event = threading.Event()
        self.shared_data = shared_data  # 引入共享，使其变为可编辑状态

        self.key_data = ['里程', '运行时间', '刀盘转速', '刀盘转速设定值', '推进速度', '推进速度设定值', '刀盘推力',
                         '刀盘扭矩', '刀盘贯入度', '推进位移', '推进压力', '顶护盾压力', '左侧护盾压力', '右侧护盾压力',
                         '顶护盾位移', '左侧护盾位移', '右侧护盾位移', '撑紧压力', '左撑靴位移', '右撑靴位移',
                         '冷水泵压力', '控制泵压力', '主机皮带机速度', '推进泵电机电流']
        self.base_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        self.add_temp_cycle = DataFrame()
        self.num_cycle = 1
        self.add_temp_display = DataFrame()
        self.per_day_path = None
        self.per_day_csv = None
        self.per_cycle_path = None
        self.per_display_path = None
        self.creative_dir()
        self.last_information = {'num': 0, 'data': DataFrame(), '推荐刀盘转速': 0, '推荐推进速度': 0, '当前围岩类型': 'Ⅱ类Ⅲ类',
                                 'Ⅱ类Ⅲ类围岩概率': 0, 'Ⅳ类Ⅴ类围岩概率': 0, '建议支护方式': '--', '风险状态': '--',
                                 'TPI-平均': 0, 'FPIa-平均': 0, 'FPIb-平均': 0}
        self.last_time = '2008-08-08 12:00:00'

    def run(self):
        """
        运行线程内的代码，请勿修改
        self.shared_Var.RawVar为原始的每秒数据记录，格式为DataFrame
        self.shared_Var为待汇总的数据记录，格式为dict
        """
        while not self._stop_event.is_set():  # 循环运行
            self.save_display()
            if not self.shared_data.Real.empty:
                if self.shared_data.Real.loc['运行时间'] != self.last_time:
                    self.save_daily()
                    self.save_cycle()
                self.last_time = copy.deepcopy(self.shared_data.Real.loc['运行时间'])
            time.sleep(1)  # 每20秒读取一次，请勿修改
        print('\033[0;33m%s -> Thread stopped.\n\033[0m' % self.__class__.__name__)

    def stop(self):
        self._stop_event.set()

    def creative_dir(self):
        self.per_cycle_path = os.path.join(self.base_path, 'SaveData\\Per-Cycle')
        if not os.path.exists(self.per_cycle_path):
            os.mkdir(self.per_cycle_path)  # 创建相关文件夹
        self.per_day_path = os.path.join(self.base_path, 'SaveData\\Per-Day')
        if not os.path.exists(self.per_day_path):
            os.mkdir(self.per_day_path)  # 创建相关文件夹
        self.per_display_path = os.path.join(self.base_path, 'SaveData\\Per-Display')
        if not os.path.exists(self.per_display_path):
            os.mkdir(self.per_display_path)  # 创建相关文件夹

    def save_cycle(self):
        if not self.shared_data.Real.empty:
            if self.shared_data.Real.loc['刀盘转速'] > 0.1:
                if '--' not in [self.shared_data.ShowVar['当前围岩类型'], self.shared_data.ShowVar['Ⅱ类Ⅲ类围岩概率'],
                                self.shared_data.ShowVar['Ⅳ类Ⅴ类围岩概率'], self.shared_data.ShowVar['建议支护方式'],
                                self.shared_data.ShowVar['风险状态'], self.shared_data.ShowVar['推荐刀盘转速'],
                                self.shared_data.ShowVar['推荐推进速度']]:
                    self.last_information['当前围岩类型'] = self.shared_data.ShowVar['当前围岩类型']
                    self.last_information['Ⅱ类Ⅲ类围岩概率'] = self.shared_data.ShowVar['Ⅱ类Ⅲ类围岩概率']
                    self.last_information['Ⅳ类Ⅴ类围岩概率'] = self.shared_data.ShowVar['Ⅳ类Ⅴ类围岩概率']
                    self.last_information['建议支护方式'] = self.shared_data.ShowVar['建议支护方式']
                    self.last_information['风险状态'] = self.shared_data.ShowVar['风险状态']
                    self.last_information['TPI-平均'] = self.shared_data.ShowVar['TPI-平均']
                    self.last_information['FPIa-平均'] = self.shared_data.ShowVar['FPIa-平均']
                    self.last_information['FPIb-平均'] = self.shared_data.ShowVar['FPIb-平均']
                    self.last_information['推荐刀盘转速'] = int(self.shared_data.ShowVar['推荐刀盘转速'])
                    self.last_information['推荐推进速度'] = int(self.shared_data.ShowVar['推荐推进速度'])
                real_data = self.shared_data.Real.to_frame().T.loc[:, self.key_data]
                self.add_temp_cycle = pd.concat([self.add_temp_cycle, real_data], ignore_index=True, axis=0)
            else:
                if not self.add_temp_cycle.empty:
                    Length = max(self.add_temp_cycle.loc[:, '推进位移']) - min(
                        self.add_temp_cycle.loc[:, '推进位移'])  # 掘进长度最小值大于规定值
                    V_max = max(self.add_temp_cycle.loc[:, '推进速度'])
                    if Length > 10 and V_max > 1 and self.add_temp_cycle.shape[0] >= 200:
                        self.last_information['num'] = self.num_cycle
                        self.last_information['data'] = self.add_temp_cycle
                        if len(self.shared_data.History) >= 10:
                            self.shared_data.History.pop(0)
                        self.shared_data.History.append(copy.deepcopy(self.last_information))
                        Mark = round(self.add_temp_cycle.loc[0, '里程'], 2)  # 获取每个掘进段的起始桩号
                        Time = self.add_temp_cycle.loc[0, '运行时间']  # 获取每个掘进段的时间记录
                        Time = pd.to_datetime(Time, format='%Y-%m-%d %H:%M:%S')  # 对时间类型记录进行转换
                        year, mon, d, h, m, s = Time.year, Time.month, Time.day, Time.hour, Time.minute, Time.second
                        csv_name = (self.num_cycle, Mark, int(year), int(mon), int(d), int(h), int(m), int(s))  # 文件名
                        csv_name = '%00005d %.2f %04d年%02d月%02d日 %02d时%02d分%02d秒.csv' % csv_name
                        csv_path = os.path.join(self.per_cycle_path, csv_name)
                        self.add_temp_cycle.to_csv(csv_path, index=False, encoding='gb2312')  # 循环段保存为csv文件
                        self.num_cycle += 1
                    self.add_temp_cycle = DataFrame()

    def save_daily(self):
        if not self.shared_data.Real.empty:
            current_time = datetime.now().time()
            if current_time.hour == 0 and current_time.minute == 0 or not self.per_day_csv:
                year = datetime.now().year
                month = datetime.now().month
                day = datetime.now().day
                self.per_day_csv = os.path.join(self.per_day_path, '%4d年%d月%2d日.csv' % (year, month, day))
            if self.per_day_csv:
                with open(self.per_day_csv, 'a', newline='') as csv_file:
                    writer = csv.writer(csv_file)
                    if csv_file.tell() == 0:  # 如果文件是空的，写入列名
                        writer1 = csv.DictWriter(csv_file, fieldnames=list(self.shared_data.Real.to_frame().T))
                        writer1.writeheader()
                    writer.writerow(self.shared_data.Real)

    def save_display(self):
        if self.shared_data.ShowVar['施工状态'] == '正在掘进':
            real_display = pd.DataFrame([copy.deepcopy(self.shared_data.ShowVar)])
            self.add_temp_display = pd.concat([self.add_temp_display, real_display], ignore_index=True, axis=0)
        else:
            if not self.add_temp_display.empty:
                Mark = round(self.add_temp_display.loc[0, '里程'], 2)  # 获取每个掘进段的起始桩号
                Time = self.add_temp_display.loc[0, '运行时间']  # 获取每个掘进段的时间记录
                Time = pd.to_datetime(Time, format='%Y-%m-%d %H:%M:%S')  # 对时间类型记录进行转换
                year, mon, d, h, m, s = Time.year, Time.month, Time.day, Time.hour, Time.minute, Time.second
                csv_name = (self.num_cycle, Mark, int(year), int(mon), int(d), int(h), int(m), int(s))  # 文件名
                csv_name = '%00005d %.2f %04d年%02d月%02d日 %02d时%02d分%02d秒.csv' % csv_name
                csv_path = os.path.join(self.per_display_path, csv_name)
                self.add_temp_display.to_csv(csv_path, index=False, encoding='gb2312')  # 循环段保存为csv文件
                self.add_temp_display = DataFrame()
