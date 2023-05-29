# -*- coding: utf-8 -*-
# ************************************************************************
# * Software:  IndexCalculation  for  Python                             *
# * Version:  1.0.0                                                      *
# * Date:  2023-03-30 00:00:00                                           *
# * Last  update: 2023-03-30 00:00:00                                    *
# * License:  LGPL v1.0                                                  *
# * Maintain  address:  https://pan.baidu.com/s/1SKx3np-9jii3Zgf1joAO4A  *
# * Maintain  code:  STBM                                                *
# ************************************************************************

import numpy as np
import pandas as pd
from pandas import DataFrame
from sklearn.linear_model import LinearRegression


class RockBreakingIndex(object):
    @staticmethod  # 不强制要求传递参数
    def remove_outliers(data: DataFrame, method='3sigma') -> DataFrame:
        """
        :param data: DataFrame格式数据
        :param method: 此函数包括，3σ方法、4分位法，默认采用3σ
        :return: 去除异常值后的数组
        """
        for col in ['刀盘扭矩', '刀盘贯入度', '刀盘转速', '推进速度', '刀盘推力']:
            if method == '3sigma':
                mean, std = data.loc[:, col].mean(), data.loc[:, col].std()  # 计算均值、方差
                lower_limit, upper_limit = mean - 3 * std, mean + 3 * std  # 剔除3sigma范围外的异常值
                data = data[(data[col] >= lower_limit) & (data[col] <= upper_limit)]
            elif method == "4Quartile":
                Q1, Q3 = data.quantile(q=0.25), data.quantile(q=0.75)  # 计算Q1 Q3
                IQR = Q3 - Q1
                lower_limit, upper_limit = Q1 - 1.5 * IQR, Q1 + 1.5 * IQR  # 计算上下限
                data = data[(data[col] >= lower_limit) & (data[col] <= upper_limit)]  # 剔除3sigma范围外的异常值
        data = data.reset_index(drop=True)
        return data

    @staticmethod  # 不强制要求传递参数
    def fitting(x, y):
        x = pd.DataFrame(x)
        reg = LinearRegression().fit(x, y)  # 因为这里要求x.shape = (n,1) y.shape = (n,)
        a, b, r2 = reg.coef_[0], reg.intercept_, reg.score(x, y)
        return a, b, r2

    def run(self, data: DataFrame) -> DataFrame:
        """破岩指标计算TPI, FPI, WR, F=a*P+b"""
        data = data[(data['刀盘贯入度'] > 1) & (data['刀盘推力'] >= 3000)].reset_index(drop=True)
        data = self.remove_outliers(data)
        if not data.empty:
            tpi = (data['刀盘扭矩'] / data['刀盘贯入度'])
            fpi = (data['刀盘推力'] / data['刀盘贯入度'])
            wr = (2000 * np.pi * data['刀盘扭矩'] * data['刀盘转速']) / (data['推进速度'] * data['刀盘推力'])
            a, b, r2 = self.fitting(data['刀盘贯入度'], data['刀盘推力'])
            results = {'TPI_mean': tpi.mean(), "TPI_std": tpi.std(), "FPI_mean": fpi.mean(), "FPI_std": fpi.std(),
                       "WR_mean": wr.mean(), "WR_std": wr.std(), 'a': a, 'b': b, 'r2': r2}
        else:
            results = {'TPI_mean': 0, "TPI_std": 0, "FPI_mean": 0, "FPI_std": 0,
                       "WR_mean": 0, "WR_std": 0, 'a': 0, 'b': 0, 'r2': 0}
        rock_index = pd.DataFrame([results])  # 最后的返回值
        return rock_index
