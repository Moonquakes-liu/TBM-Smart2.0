# -*- coding: utf-8 -*-
# @Time : 2023/5/9 16:30
# @Author : LeiJer Wu
# @Email : Leijeer_Wu@163.com
# @File : Fracture and weak rock mass.py
# @Project : TBM-Smart
import os
import pandas as pd
import numpy as np
import joblib
from pandas import DataFrame


class FWM(object):
    def __init__(self, model_path):
        """
        :param model_path: 训练好的模型地址
        """
        self.input1 = DataFrame()
        self.input2 = DataFrame()
        self.input3 = model_path
        self.threshold = 0.52  # 模型提供的最优阈值
        self.loaded_model = joblib.load(model_path)

    def check(self):
        if not isinstance(self.input1, pd.DataFrame):
            raise TypeError('输入参数1必须是pandas DataFrame类型')
        if not isinstance(self.input2, pd.DataFrame):
            raise TypeError('输入参数2必须是pandas DataFrame类型')
        elif self.input2.shape != (9, 1):
            if self.input2.shape == (1, 9):
                self.input2 = self.input2.T
            else:
                raise ValueError('输入参数2形状应该改为(9,1)或者(9,)')
        if not os.path.isfile(self.input3):
            raise ValueError('输入参数3必须是可读取的文件地址')

    def calculate(self, TBM_key_data, TBM_Rock_index):
        self.input1 = TBM_key_data.astype('float64')
        self.input2 = TBM_Rock_index.astype('float64')
        self.check()
        input1 = self.input1.mean().to_frame()
        Input = pd.concat([input1.T, self.input2.T], axis=1)
        probability_weak = self.loaded_model.predict_proba(Input)[0][1]
        if probability_weak >= self.threshold:
            IF_weak_rock = 'Yes'
        else:
            IF_weak_rock = 'No'
        return IF_weak_rock, probability_weak
