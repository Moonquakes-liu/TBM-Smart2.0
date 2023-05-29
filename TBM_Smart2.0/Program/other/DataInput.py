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

import time
import pandas as pd
from pandas import DataFrame
import urllib.request
import json
from PyQt5.QtCore import QTimer, QCoreApplication
from PyQt5.QtWidgets import QApplication
import os


class DataInput(object):
    """数据输入"""
    def __init__(self):
        """初始化各参量"""
        self.YS_Resource = 'D:\\YStest'
        self.YS_csv_list, self.YS_csv_num, self.YS_csv_col = None, 0, 0
        self.YC_Resource = 'D:\\YStest'
        self.YC_csv_list, self.YC_csv_num, self.YC_csv_col = None, 0, 0
        self.PLC_Simulate_URL = 'http://127.0.0.1:8888/api/realtime?id=3'
        self.PLC_Practical_URL = 'http://127.0.0.1:8888/api/realtime?id=3'
        self.Raw_Data = DataFrame()
        self.Key = {'db47_16': '桩号', 'time_str': '运行时间', 'db40_1330': '刀盘转速',
                    'db40_2138': '推进速度', 'db40_1346': '刀盘扭矩', 'db40_1518': '总推进力'}

    def run(self, Type='PLC') -> [DataFrame, bool]:
        """
        将第原始数据读取相关代码放置在这里
        :param Type: 'YS'、'YC'、'PLC'
        :return: 每秒数据（per_data）, PLC状态（True/False）
        """
        if Type == 'YS':
            return self.Read_YS_Data()  # 返回每秒数据，请勿修改，数据格式为 DataFrame
        if Type == 'YC':
            return self.Read_YC_Data()  # 返回每秒数据，请勿修改，数据格式为 DataFrame
        if Type == 'PLC':
            return self.Read_PLC_Data()  # 返回每秒数据，请勿修改，数据格式为 DataFrame

    def Read_PLC_Data(self):
        try:
            html = urllib.request.urlopen(self.PLC_Simulate_URL, timeout=0.5)
            data = json.loads(html.read())  # json格式解析
            per_data = pd.DataFrame([data])
            per_data.rename(columns=self.Key, inplace=True)
            return per_data.loc[0, :], True
        except urllib.error.URLError:
            return DataFrame(), False

    def Read_YS_Data(self):
        if os.path.exists(self.YS_Resource):
            self.YS_csv_list = os.listdir(self.YS_Resource)
            if self.Raw_Data.empty or self.YS_csv_col > self.Raw_Data.shape[0] - 1:
                csv_path = os.path.join(self.YS_Resource, self.YS_csv_list[self.YS_csv_num])
                self.Raw_Data = pd.read_csv(csv_path, encoding='gb2312')
                self.YS_csv_num += 1
                self.YS_csv_col = 0
            per_data = self.Raw_Data.loc[self.YS_csv_col, :]
            self.YS_csv_col += 1
            return per_data, True
        else:
            print('路径 %s 不存在' % self.YS_Resource)
            return DataFrame(), False

    def Read_YC_Data(self):
        if os.path.exists(self.YC_Resource):
            self.YC_csv_list = os.listdir(self.YC_Resource)
            if self.Raw_Data.empty or self.YC_csv_col > self.Raw_Data.shape[0] - 1:
                csv_path = os.path.join(self.YC_Resource, self.YC_csv_list[self.YC_csv_num])
                self.Raw_Data = pd.read_csv(csv_path, encoding='gb2312')
                self.YC_csv_num += 1
                self.YC_csv_col = 0
            per_data = self.Raw_Data.loc[self.YC_csv_col, :]
            self.YC_csv_col += 1
            return per_data, True
        else:
            print('路径 %s 不存在' % self.YC_Resource)
            return DataFrame(), False
