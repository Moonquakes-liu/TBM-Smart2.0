# -*- coding: utf-8 -*-
# ************************************************************************
# * Software:  ResponseParmPredict  for  Python                          *
# * Version:  1.0.0                                                      *
# * Date:  2023-03-30 00:00:00                                           *
# * Last  update: 2023-03-30 00:00:00                                    *
# * License:  LGPL v1.0                                                  *
# * Maintain  address:  https://pan.baidu.com/s/1SKx3np-9jii3Zgf1joAO4A  *
# * Maintain  code:  STBM                                                *
# ************************************************************************
import copy
import random
import threading
from datetime import datetime
import time
import os
import shutil
import tarfile
import torch
from statsmodels.tsa.holtwinters import SimpleExpSmoothing
from statsmodels.tsa.arima.model import ARIMA
import numpy as np
import pandas as pd


class ResponseParmPredict(threading.Thread):
    """响应参数预测（prediction_T、prediction_F）"""

    def __init__(self, shared_data):
        """
        初始化各参量，请勿修改
        :param shared_data: 共享变量
        """
        super(ResponseParmPredict, self).__init__()
        self._stop_event = threading.Event()
        self.shared_data = shared_data  # 引入共享，使其变为可编辑状态

        base_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        self.PredictTF_CNN = None
        self.model_path_CNN = os.path.join(base_path, 'Pickle\\ResponseParmPredict.tar')
        self.PredictTF_other = None
        self.model_path_other = None
        self.run_fuc = 'function2'
        self.time_interval = 3
        self.time_num = copy.deepcopy(self.time_interval)
        self.load_model(option='All')
        self.load_response_CNN = False
        self.load_response_other = False
    
    def load_model(self, option='All'):
        current_modul = self.__class__.__name__
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        if option == 'CNN Module':
            self.PredictTF_CNN = PredictTF(model_path=self.model_path_CNN)
            print('\033[0;32m%s -> Loading model <%s> successful, local time [%s]!\033[0m'
                  % (current_modul, os.path.basename(self.model_path_CNN), current_time))
        elif option == 'Other Module':
            self.PredictTF_other = None
            print('\033[0;32m%s -> Loading model <%s> successful, local time [%s]!\033[0m'
                  % (current_modul, os.path.basename(self.model_path_other), current_time))
        elif option == 'All':
            self.PredictTF_CNN = PredictTF(model_path=self.model_path_CNN)
            print('\033[0;32m%s -> Loading model <%s> successful, local time [%s]!\033[0m'
                  % (current_modul, os.path.basename(self.model_path_CNN), current_time))
            # self.PredictTF_other = None
            # print('\033[0;32m%s -> Loading model <%s> successful, local time [%s]!\033[0m'
            #     # % (current_modul, os.path.basename(self.model_path_other), current_time))
        else:
            print('\033[0;31m%s -> Option <%s> does not exist, please check!\033[0m'
                  % (self.__class__.__name__, option))

    def run(self):
        """
        运行线程内的代码，请勿修改
        self.shared_Var.RawVar为原始的每秒数据记录，格式为DataFrame
        self.shared_Var为待汇总的数据记录，格式为dict
        """
        while not self._stop_event.is_set():  # 循环运行
            current_time = datetime.now().time()
            if current_time.hour == 3 and current_time.minute == 0 and not self.load_response_CNN:
                self.load_model(option='CNN Module')
                self.load_response_CNN = True
            if current_time.hour == 3 and current_time.minute == 30 and not self.load_response_other:
                # self.load_model(option='Other Module')
                self.load_response_other = True
            if current_time.hour == 0 and current_time.minute == 0:
                self.load_response_CNN = False
                self.load_response_other = False
            if self.shared_data.BasicVar['raw-data'].shape[0] >= 30:
                if self.time_num == self.time_interval:
                    try:
                        if self.run_fuc == 'function1':
                            recommend_T, recommend_F = self.function1()
                        elif self.run_fuc == 'function2':
                            recommend_T, recommend_F = self.function2()
                        else:
                            recommend_T, recommend_F = '--', '--'
                            print('\033[0;31m%s -> Function <%s> does not exist, please check!\033[0m'
                                  % (self.__class__.__name__, self.run_fuc))
                        self.shared_data.ShowVar['刀盘扭矩-预测'] = round(recommend_T, 2)
                        self.shared_data.ShowVar['刀盘推力-预测'] = round(recommend_F, 2)
                    except Exception as e:
                        print('\033[0;31m%s -> Error, %s !!!\033[0m' % (self.__class__.__name__, e))
                    self.time_num = 0
                else:
                    self.time_num += 1
            else:
                self.shared_data.ShowVar['刀盘扭矩-预测'] = '--'
                self.shared_data.ShowVar['刀盘推力-预测'] = '--'
            time.sleep(1)
        print('\033[0;33m%s -> Thread stopped.\n\033[0m' % self.__class__.__name__)

    def stop(self):
        self._stop_event.set()

    def function1(self) -> [float, float]:
        """
        将第一种响应参数预测相关代码放置在这里
        :return: 刀盘扭矩预测值（predict_T）
                 刀盘推力预测值（predict_F）
        """
        # 破岩指标（TPI_mean, TPI_std, FPI_mean, FPI_std, WR_mean, WR_std, a, b, r2}），请勿修改
        rock_index = copy.deepcopy(self.shared_data.BasicVar['rock-index'])  # 数据格式 DataFrame
        # 破岩关键数据(桩号, 运行时间, 刀盘转速, 刀盘给定转速显示值, 推进速度, 推进给定速度百分比, 刀盘推力,
        #            刀盘扭矩, 贯入度, 推进位移, 推进压力, 冷水泵压力, 控制泵压力, 撑紧压力, 左撑靴油缸行程检测,
        #            右撑靴油缸行程检测, 主机皮带机转速, 顶护盾压力, 左侧护盾压力, 右侧护盾压力, 左侧护盾位移,
        #            右侧护盾位移, 推进泵电机电流)，请勿修改
        key_data = copy.deepcopy(self.shared_data.BasicVar['raw-data'])  # 数据格式 DataFrame
        # 历史掘进段数据，请勿修改
        passed_data = copy.deepcopy(self.shared_data.BasicVar['passed-data'])  # 数据格式 list

        # 以下代码为正式代码，可将其修改
        data_T = key_data.loc[-30:, '刀盘扭矩'].values.tolist()
        data_F = key_data.loc[-30:, '刀盘推力'].values.tolist()
        # fit model
        model_F = ARIMA(data_F, order=(1, 1, 1))
        model_T = ARIMA(data_T, order=(1, 1, 1))
        # make prediction
        model_fit_F = model_F.fit()
        model_fit_T = model_T.fit()
        # make prediction
        predict_T = round(model_fit_T.predict(len(data_T), len(data_T), typ='levels')[0], 2)
        predict_F = round(model_fit_F.predict(len(data_F), len(data_F), typ='levels')[0], 2)
        # 以上代码为正式代码，可将其修改

        return predict_T, predict_F  # 返回数据，请勿修改，数据格式分别为（float, float）

    def function2(self) -> [float, float]:
        """
        将第二种响应参数预测相关代码放置在这里
        :return: 刀盘扭矩预测值（predict_T）
                 刀盘推力预测值（predict_F）
        """
        # 破岩指标（TPI_mean, TPI_std, FPI_mean, FPI_std, WR_mean, WR_std, a, b, r2}），请勿修改
        rock_index = self.shared_data.BasicVar['rock-index']  # 数据格式 DataFrame
        # 破岩关键数据(桩号, 运行时间, 刀盘转速, 刀盘给定转速显示值, 推进速度, 推进给定速度百分比, 刀盘推力,
        #            刀盘扭矩, 贯入度, 推进位移, 推进压力, 冷水泵压力, 控制泵压力, 撑紧压力, 左撑靴油缸行程检测,
        #            右撑靴油缸行程检测, 主机皮带机转速, 顶护盾压力, 左侧护盾压力, 右侧护盾压力, 左侧护盾位移,
        #            右侧护盾位移, 推进泵电机电流)，请勿修改
        key_data = self.shared_data.BasicVar['raw-data']  # 数据格式 DataFrame
        # 历史掘进段数据，请勿修改
        passed_data = self.shared_data.BasicVar['passed-data']  # 数据格式 list

        # 以下代码仅在测试时使用，可将其删除
        predict_TF = self.PredictTF_CNN.calculate(TBM_key_data=key_data)
        predict_F = predict_TF[1]
        predict_T = predict_TF[0]
        # 以上代码仅在测试时使用，可将其删除

        return predict_T, predict_F  # 返回数据，请勿修改，数据格式分别为（float, float）


# ************************************************************************
# * Software:  PredictTF  for  Python                                    *
# * Version:  1.0.0                                                      *
# * Date:  2023-05-15 16:30:00                                           *
# * Author:  Yao min                                                     *
# * Email : 20121140@bjtu.edu.cn                                         *
# * License:  LGPL v1.0                                                  *
# ************************************************************************


class CNN_TF(torch.nn.Module):
    def __init__(self):
        super(CNN_TF, self).__init__()
        self.conv1 = torch.nn.Sequential(
            torch.nn.Conv2d(in_channels=1, out_channels=32, kernel_size=(1, 4)),
            torch.nn.ReLU()
        )
        self.conv2 = torch.nn.Sequential(
            torch.nn.Conv2d(in_channels=1, out_channels=32, kernel_size=(30, 1)),
            torch.nn.ReLU()
        )
        self.conv3 = torch.nn.Sequential(
            torch.nn.Conv2d(in_channels=1, out_channels=32, kernel_size=(1, 32)),
            torch.nn.ReLU()
        )
        self.conv4 = torch.nn.Sequential(
            torch.nn.Conv2d(in_channels=1, out_channels=32, kernel_size=(32, 1)),
            torch.nn.ReLU()
        )
        self.fc1 = torch.nn.Linear(32 * 32, 512)
        self.fc2 = torch.nn.Linear(2, 512)
        self.fc3 = torch.nn.Linear(1024, 2)

    def forward(self, x):
        x[0] = torch.unsqueeze(x[0], 1)
        out = self.conv1(x[0])
        out = out.transpose(1, 3)
        out = self.conv2(out)
        out = out.transpose(1, 2)
        out = self.conv3(out)
        out = out.transpose(1, 3)
        out = self.conv4(out)
        out = out.transpose(1, 2)
        out = out.view(out.size(0), -1)
        out = self.fc1(out)
        _out = self.fc2(x[1].view(x[1].size(0), -1))
        out = torch.cat((out, _out), 1)
        out = self.fc3(out)
        return out


class PredictTF(object):
    def __init__(self, model_path):
        self.train_X = None
        self.train_Y = None
        self.CNN_TF = CNN_TF()
        self.load_model(path=model_path)

    def load_model(self, path):
        target_folder = os.path.join(os.path.dirname(path), os.path.basename(path)[:-3])
        with tarfile.open(path, 'r') as tar:
            tar.extractall(path=target_folder)
        model_cnn = os.path.join(target_folder, 'CNN_TF.pth.tar')
        self.CNN_TF.load_state_dict(torch.load(model_cnn, map_location='cpu')['state_dict'])
        self.train_X = np.load(os.path.join(target_folder, 'Train_X.npy'), allow_pickle=True)
        self.train_Y = np.load(os.path.join(target_folder, 'Train_Y.npy'), allow_pickle=True)
        shutil.rmtree(target_folder)

    def train_data(self):
        # #获取训练数据：特征和标签。
        train_size = 1
        data = list(zip(self.train_X, self.train_Y))
        train_num = int(train_size * len(data))
        train_data = data[:train_num]
        # x1：上升段TFnv；x2：稳定段nv；Y：稳定段TF
        train_data_x1 = np.array([x[0][0] for x in train_data])
        train_data_x2 = np.array([x[0][1] for x in train_data])
        # 归一化处理的四个参数
        train_data_x1_mean = train_data_x1.reshape(-1, 4).mean(axis=0)  # x1上升段TFnv的均值
        train_data_x1_std = train_data_x1.reshape(-1, 4).std(axis=0)  # x1上升段TFnv的均值
        train_data_x2_mean = train_data_x2.mean(axis=0)  # x2稳定段nv的均值
        train_data_x2_std = train_data_x2.std(axis=0)  # x2稳定段nv的方差
        return train_data_x1_mean, train_data_x1_std, train_data_x2_mean, train_data_x2_std

    def calculate(self, TBM_key_data):
        train_data_x1_mean, train_data_x1_std, train_data_x2_mean, train_data_x2_std = self.train_data()
        np.random.seed(111)
        perm_N = np.random.permutation(TBM_key_data.shape[0])[:30]
        TBM_key_data = TBM_key_data.reset_index(drop=True)  # 重建提取数据的行索引
        test_data_x1 = np.array([TBM_key_data.loc[perm_N, ['刀盘转速', '刀盘扭矩', '刀盘推力', '推进速度']].values])
        test_data_x2 = np.array([TBM_key_data.loc[TBM_key_data.shape[0] - 1, ['刀盘转速', '推进速度']].values])
        test_data_x1 = ((test_data_x1 - train_data_x1_mean) / train_data_x1_std).astype(float)
        test_data_x2 = ((test_data_x2 - train_data_x2_mean) / train_data_x2_std).astype(float)
        result_TF = pd.DataFrame((self.CNN_TF([torch.FloatTensor(test_data_x1),
                                               torch.FloatTensor(test_data_x2)])).detach().numpy())
        return round(result_TF.iloc[0, 0], 2), round(result_TF.iloc[0, 1], 2)
