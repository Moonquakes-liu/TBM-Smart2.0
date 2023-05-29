# -*- coding: utf-8 -*-
# ************************************************************************
# * Software:  DataExtract  for  Python                                  *
# * Version:  1.0.0                                                      *
# * Date:  2023-03-30 00:00:00                                           *
# * Last  update: 2023-03-30 00:00:00                                    *
# * License:  LGPL v1.0                                                  *
# * Maintain  address:  https://pan.baidu.com/s/1SKx3np-9jii3Zgf1joAO4A  *
# * Maintain  code:  STBM                                                *
# ************************************************************************
import pandas as pd
from pandas import DataFrame
import copy


class DataExtract(object):
    def __init__(self):
        self.key_name = ['里程', '运行时间', '刀盘转速', '刀盘转速设定值', '推进速度', '推进速度设定值', '刀盘推力',
                         '刀盘扭矩', '刀盘贯入度', '推进位移', '推进压力', '顶护盾压力', '左侧护盾压力', '右侧护盾压力',
                         '顶护盾位移', '左侧护盾位移', '右侧护盾位移', '撑紧压力', '左撑靴位移', '右撑靴位移',
                         '冷水泵压力', '控制泵压力', '主机皮带机速度', '推进泵电机电流']
        self.passed_data = []  # 保存历史循环段数据
        self.key_data = DataFrame()  # 保存最新数据
        self.stage = '停机中'

    def stage_judge(self, data: DataFrame) -> str:
        """
        掘进状态判断
        :param data: 每秒实时数据(DataFrame)
        :return: 当前状态 ('停机中', '等待掘进', '空推中', '正在掘进')
        """
        # 以下代码仅在测试时使用，可将其删除
        if data['刀盘转速'] >= 0.1:
            if data['推进速度'] >= 1:
                if self.key_data.shape[0] >= 30:
                    self.stage = '正在掘进'
                else:
                    self.stage = '空推中'
            else:
                self.stage = '等待掘进'
        else:
            self.stage = '停机中'
        # 以上代码仅在测试时使用，可将其删除
        self.data_extract(data=data)
        return copy.deepcopy(self.stage)  # 返回每秒机械状态，请勿修改，数据格式为 str

    def data_extract(self, data: DataFrame):
        """
        破岩数据提取及历史掘进段保存
        :param data: 每秒实时数据（DataFrame格式）
        """
        if self.stage in ['正在掘进', '空推中']:
            data['刀盘贯入度'] = (data['推进速度'] / data['刀盘转速']) if data['刀盘转速'] > 0 else 0.0
            new_data = data.to_frame().T.loc[:, self.key_name]
            self.key_data = pd.concat([self.key_data, new_data], ignore_index=True, axis=0)
        else:
            if self.key_data.shape[0] >= 30:
                self.passed_data.append(self.key_data)
            if not self.key_data.empty:
                self.key_data = DataFrame()

    def run(self):
        """
        :return: 每秒实时破岩数据 [至少30条记录]， 历史掘进段数据 [round1, round2,...,round9, round10]
        """
        if self.stage == '正在掘进':
            return copy.deepcopy(self.key_data), copy.deepcopy(self.passed_data)  # 返回数据，请勿修改， 数据格式分别为 （DataFrame, list）
        else:
            return DataFrame(), copy.deepcopy(self.passed_data)  # 返回数据，请勿修改， 数据格式分别为 （DataFrame, list）
