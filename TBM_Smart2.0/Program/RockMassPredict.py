# -*- coding: utf-8 -*-
# ************************************************************************
# * Software:  RockMassPredict  for  Python                              *
# * Version:  1.0.0                                                      *
# * Date:  2023-03-30 00:00:00                                           *
# * Last  update: 2023-03-30 00:00:00                                    *
# * License:  LGPL v1.0                                                  *
# * Maintain  address:  https://pan.baidu.com/s/1SKx3np-9jii3Zgf1joAO4A  *
# * Maintain  code:  STBM                                                *
# ************************************************************************

import copy
import os
import random
from datetime import datetime
import threading
import time
import pandas as pd
import numpy as np
import joblib
import sys
from pandas import DataFrame


class RockMassPredict(threading.Thread):
    """岩体破碎概率预测（current_rock, rock_23, rock_45, support_method, risk_state）"""
    import warnings
    warnings.filterwarnings("ignore")  # 忽略警告信息

    def __init__(self, shared_data):
        """
        初始化各参量，请勿修改
        :param shared_data: 共享变量
        """
        super(RockMassPredict, self).__init__()
        self._stop_event = threading.Event()
        self.shared_data = shared_data  # 引入共享，使其变为可编辑状态

        base_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        self.RockMassPredict_2 = None
        self.model_path_2 = os.path.join(base_path, 'Pickle\\RockMassPredict_2.pkl')
        self.RockMassPredict_4 = None
        self.model_path_4 = os.path.join(base_path, 'Pickle\\RockMassPredict_4.pkl')
        self.run_fuc = 'function1'
        self.time_interval = 60
        self.time_num = copy.deepcopy(self.time_interval)
        self.load_model(option='all')
        self.load_response_2 = False
        self.load_response_4 = False

    def load_model(self, option='all'):
        current_modul = self.__class__.__name__
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        if option == 'two classification':
            self.RockMassPredict_2 = FWM(model_path=self.model_path_2)
            print('\033[0;32m%s -> Loading model <%s> successful, local time [%s]!\033[0m'
                  % (current_modul, os.path.basename(self.model_path_2), current_time))
        elif option == 'four classification':
            self.RockMassPredict_4 = Class4_Rock(model_path=self.model_path_4)
            print('\033[0;32m%s -> Loading model <%s> successful, local time [%s]!\033[0m'
                  % (current_modul, os.path.basename(self.model_path_4), current_time))
        elif option == 'all':
            self.RockMassPredict_2 = FWM(model_path=self.model_path_2)
            print('\033[0;32m%s -> Loading model <%s> successful, local time [%s]!\033[0m'
                  % (current_modul, os.path.basename(self.model_path_2), current_time))
            self.RockMassPredict_4 = Class4_Rock(model_path=self.model_path_4)
            print('\033[0;32m%s -> Loading model <%s> successful, local time [%s]!\033[0m'
                  % (current_modul, os.path.basename(self.model_path_4), current_time))
        else:
            print('\033[0;31m%s -> Option <%s> does not exist, please check!\033[0m'
                  % (self.__class__.__name__, option))

    def run(self):
        while not self._stop_event.is_set():
            current_time = datetime.now().time()
            if current_time.hour == 2 and current_time.minute == 0 and not self.load_response_2:
                self.load_model(option='two classification')
                self.load_response_2 = True
            if current_time.hour == 2 and current_time.minute == 30 and not self.load_response_4:
                self.load_model(option='four classification')
                self.load_response_4 = True
            if current_time.hour == 0 and current_time.minute == 0:
                self.load_response_2 = False
                self.load_response_4 = False
            if self.shared_data.BasicVar['raw-data'].shape[0] >= 30:
                if self.time_num == self.time_interval:
                    if self.run_fuc == 'function1':
                        current_rock, rock_23, rock_45, support_method, risk_state = self.function1()
                    elif self.run_fuc == 'function2':
                        current_rock, rock_23, rock_45, support_method, risk_state = self.function2()
                    else:
                        current_rock, rock_23, rock_45, support_method, risk_state = '--', '--', '--', '--', '--',
                        print('\033[0;31m%s -> Function <%s> does not exist, please check!\033[0m'
                              % (self.__class__.__name__, self.run_fuc))
                    self.shared_data.ShowVar['当前围岩类型'] = current_rock
                    self.shared_data.ShowVar['Ⅱ类Ⅲ类围岩概率'] = round(rock_23, 0)
                    self.shared_data.ShowVar['Ⅳ类Ⅴ类围岩概率'] = round(rock_45, 0)
                    self.shared_data.ShowVar['建议支护方式'] = support_method
                    self.shared_data.ShowVar['风险状态'] = risk_state
                    self.time_num = 0
                else:
                    self.time_num += 1
            else:
                self.shared_data.ShowVar['当前围岩类型'] = '--'
                self.shared_data.ShowVar['Ⅱ类Ⅲ类围岩概率'] = '--'
                self.shared_data.ShowVar['Ⅳ类Ⅴ类围岩概率'] = '--'
                self.shared_data.ShowVar['建议支护方式'] = '--'
                self.shared_data.ShowVar['风险状态'] = '--'
            time.sleep(1)
        print('\033[0;33m%s -> Thread stopped.\n\033[0m' % self.__class__.__name__)

    def stop(self):
        self._stop_event.set()

    def function1(self) -> [str, int, int, str, int]:
        """
        将岩体破碎概率预测相关代码放置在这里
        :return: 当前围岩类型（current_rock）->-> ('Ⅱ类 Ⅲ类', 'Ⅳ类 Ⅴ类')
                 Ⅱ、Ⅲ类围岩概率（rock_23）
                 Ⅳ、Ⅴ类围岩概率（rock_45）,
                 建议支护方式（support_method）->-> ('暂  无', '立  拱')
                 风险状态（risk_state）->-> ('安全掘进', '预警观察', '风险控制')
        """
        # 破岩指标（TPI_mean, TPI_std, FPI_mean, FPI_std, WR_mean, WR_std, a, b, r2}），请勿修改
        # 破岩指标（TPI_mean, TPI_std, FPI_mean, FPI_std, WR_mean, WR_std, a, b, r2}），请勿修改
        rock_index = copy.deepcopy(self.shared_data.BasicVar['rock-index'])  # 数据格式 DataFrame
        # 破岩关键数据(桩号, 运行时间, 刀盘转速, 刀盘转速设定值, 推进速度, 推进给定速度百分比, 刀盘推力,
        #            刀盘扭矩, 刀盘贯入度, 推进位移, 推进压力, 冷水泵压力, 控制泵压力, 撑紧压力, 左撑靴位移,
        #            右撑靴位移, 主机皮带机转速, 顶护盾压力, 左侧护盾压力, 右侧护盾压力, 左侧护盾位移,
        #            右侧护盾位移, 推进泵电机电流)，请勿修改
        key_data = copy.deepcopy(self.shared_data.BasicVar['raw-data'])  # 数据格式 DataFrame
        # 历史掘进段数据，请勿修改
        passed_data = copy.deepcopy(self.shared_data.BasicVar['passed-data'])  # 数据格式 list

        key_data = key_data.loc[:, ['刀盘转速', '刀盘转速设定值', '推进速度', '刀盘推力', '刀盘扭矩', '刀盘贯入度', '冷水泵压力',
                                    '撑紧压力', '左撑靴位移', '右撑靴位移', '顶护盾压力', '左侧护盾压力', '右侧护盾压力',
                                    '顶护盾位移', '左侧护盾位移', '右侧护盾位移']]
        #key_data.rename(columns=self.Key_Simulate, inplace=True)
        out_2 = self.RockMassPredict_2.calculate(TBM_key_data=key_data, TBM_Rock_index=rock_index)
        current_rock = 'Ⅳ类 Ⅴ类' if out_2[0] == 'Yes' else 'Ⅱ类 Ⅲ类'
        rock_45 = int(out_2[1] * 100)
        rock_23 = 100 - rock_45
        out_4 = self.RockMassPredict_4.calculate(TBM_key_data=key_data, TBM_Rock_index=rock_index)
        risk_state = '安全掘进' if out_4 == 0 else ('预警观察' if out_4 == 1 else '风险控制')
        support_method = '暂 无' if risk_state != '风险控制' else '立 拱'
        return current_rock, rock_23, rock_45, support_method, risk_state  # 返回数据，请勿修改，数据格式分别为（str, int, int, str, str）

    def function2(self) -> [str, int, int, str, int]:
        """
        将岩体破碎概率预测相关代码放置在这里
        :return: 当前围岩类型（current_rock）->-> ('Ⅱ类 Ⅲ类', 'Ⅳ类 Ⅴ类')
                 Ⅱ、Ⅲ类围岩概率（rock_23）
                 Ⅳ、Ⅴ类围岩概率（rock_45）,
                 建议支护方式（support_method）->-> ('暂  无', '立  拱')
                 风险状态（risk_state）->-> ('安全掘进', '预警观察', '风险控制')
        """
        # 破岩指标（TPI_mean, TPI_std, FPI_mean, FPI_std, WR_mean, WR_std, a, b, r2}），请勿修改
        # 破岩指标（TPI_mean, TPI_std, FPI_mean, FPI_std, WR_mean, WR_std, a, b, r2}），请勿修改
        rock_index = copy.deepcopy(self.shared_data.BasicVar['rock-index'])  # 数据格式 DataFrame
        # 破岩关键数据(桩号, 运行时间, 刀盘转速, 刀盘转速设定值, 推进速度, 推进给定速度百分比, 刀盘推力,
        #            刀盘扭矩, 刀盘贯入度, 推进位移, 推进压力, 冷水泵压力, 控制泵压力, 撑紧压力, 左撑靴位移,
        #            右撑靴位移, 主机皮带机转速, 顶护盾压力, 左侧护盾压力, 右侧护盾压力, 左侧护盾位移,
        #            右侧护盾位移, 推进泵电机电流)，请勿修改
        key_data = copy.deepcopy(self.shared_data.BasicVar['raw-data'])  # 数据格式 DataFrame
        # 历史掘进段数据，请勿修改
        passed_data = copy.deepcopy(self.shared_data.BasicVar['passed-data'])  # 数据格式 list

        # 以下代码仅在测试时使用，可将其删除
        Random_rock_23 = random.randint(0, 100)
        Random_rock_45 = 100 - Random_rock_23
        rock_23 = Random_rock_23
        rock_45 = Random_rock_45
        current_rock = 'Ⅱ类 Ⅲ类' if Random_rock_23 > 50 else 'Ⅳ类 Ⅴ类'
        risk = '安全掘进' if Random_rock_23 > 40 else ('预警观察' if Random_rock_23 > 20 else '风险控制')
        risk_state = risk
        support_method = '暂 无' if risk != '风险控制' else '立 拱'
        # 以上代码仅在测试时使用，可将其删除

        return current_rock, rock_23, rock_45, support_method, risk_state  # 返回数据，请勿修改，数据格式分别为（str, int, int, str, str）


# ************************************************************************
# * Software:  Fracture and weak rock mass(FWM)  for  Python             *
# * Version:  1.0.0                                                      *
# * Date:  2023-05-09 16:30:00                                           *
# * Author:  LeiJer Wu                                                   *
# * Email : Leijeer_Wu@163.com                                           *
# * License:  LGPL v1.0                                                  *
# ************************************************************************


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
        aaa = {'刀盘转速': '刀盘转速', '刀盘转速设定值': '刀盘给定转速', '推进速度': '推进速度(nn/M)', '刀盘推力': '总推力',
               '刀盘扭矩': '刀盘扭矩', '刀盘贯入度': '刀盘贯入度', '冷水泵压力': '冷水泵压力', '撑紧压力': '撑紧压力',
               '左撑靴位移': '左撑靴位移', '右撑靴位移': '右撑靴位移', '顶护盾压力': '顶护盾压力', '左侧护盾压力': '左侧护盾压力',
               '右侧护盾压力': '右侧护盾压力', '顶护盾位移': '顶护盾位移', '左侧护盾位移': '左侧护盾位移', '右侧护盾位移': '右侧护盾位移'}
        Input.rename(columns=aaa, inplace=True)
        probability_weak = self.loaded_model.predict_proba(Input)[0][1]
        if probability_weak >= self.threshold:
            IF_weak_rock = 'Yes'
        else:
            IF_weak_rock = 'No'
        return IF_weak_rock, probability_weak


# ************************************************************************
# * Software:  4ClassRock  for  Python                                   *
# * Version:  1.0.0                                                      *
# * Date:  2023-05-12 22:29:00                                           *
# * Author:  LeiJer Wu                                                   *
# * Email : Leijeer_Wu@163.com                                           *
# * License:  LGPL v1.0                                                  *
# ************************************************************************


class Class4_Rock(object):
    def __init__(self, model_path):
        """
        :param TBM_key_data:  DataFrame (30,n)
        :param TBM_Rock_index: DataFrame ()
        :param model_path: 训练好的模型地址
        """
        self.input1 = DataFrame()
        self.input2 = DataFrame()
        self.input3 = model_path
        self.opt_thresholds = [0.16, 0.12, 0.12, 0.04]  # 模型提供的最优阈值
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
                raise ValueError('输入参数2形状应该改为(1,9)或者(9,)')
        if not os.path.isfile(self.input3):
            raise ValueError('输入参数3必须是可读取的文件地址')

    def calculate(self, TBM_key_data, TBM_Rock_index):
        self.input1 = TBM_key_data.astype('float64')
        self.input2 = TBM_Rock_index.astype('float64')
        self.check()
        input1 = self.input1.mean().to_frame()  # 这里列名可能有问题，
        Input = pd.concat([input1.T, self.input2.T], axis=1)
        aaa = {'刀盘转速': '刀盘转速', '刀盘转速设定值': '刀盘给定转速', '推进速度': '推进速度(nn/M)', '刀盘推力': '总推力',
               '刀盘扭矩': '刀盘扭矩', '刀盘贯入度': '刀盘贯入度', '冷水泵压力': '冷水泵压力', '撑紧压力': '撑紧压力', '左撑靴位移': '左撑靴位移',
               '右撑靴位移': '右撑靴位移', '顶护盾压力': '顶护盾压力', '左侧护盾压力': '左侧护盾压力',
               '右侧护盾压力': '右侧护盾压力', '顶护盾位移': '顶护盾位移', '左侧护盾位移': '左侧护盾位移', '右侧护盾位移': '右侧护盾位移'}
        Input.rename(columns=aaa, inplace=True)
        cols = list(Input.columns)
        # 将第二列的列名修改为'New_B'
        cols[14] = '左侧护盾位移'
        # 将修改后的列名列表赋值给DataFrame的columns属性
        Input.columns = cols
        # 使用默认的阈值进行类别判断+概率判断
        y_pred, y_prob = self.loaded_model.predict(Input), self.loaded_model.predict_proba(Input)
        # 使用最优阈值+模型预测概率，重新判断类别
        y_pred_onehot = (y_prob >= self.opt_thresholds).astype(int)
        y_pred_new = np.argmax(y_pred_onehot, axis=1)
        if (y_pred == 5) or (y_pred_new == 5):
            warning = 2
        elif (y_pred == 4) or (y_pred_new == 4):
            warning = 1
        else:
            warning = 0
        return warning  # 0表示”安全掘进“，1表示”预警观察“，2表示”风险控制“
