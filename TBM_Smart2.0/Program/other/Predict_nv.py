# -*- coding: utf-8 -*-
import os
import shutil
import tarfile
import numpy as np
import pandas as pd
import torch


class CNN_nv(torch.nn.Module):
    def __init__(self):
        super(CNN_nv, self).__init__()
        self.conv1 = torch.nn.Sequential(
            torch.nn.Conv2d(in_channels=1, out_channels=32, kernel_size=(1, 4)),
            torch.nn.ReLU()
        )
        self.conv2 = torch.nn.Sequential(
            torch.nn.Conv2d(in_channels=1, out_channels=32, kernel_size=(30, 1)),
            torch.nn.ReLU()
        )
        self.conv3 = torch.nn.Sequential(
            torch.nn.Conv2d(in_channels=1,out_channels=32,kernel_size=(1, 32)),
            torch.nn.ReLU()
        )
        self.conv4 = torch.nn.Sequential(
            torch.nn.Conv2d(in_channels=1,out_channels=32,kernel_size=(32, 1)),
            torch.nn.ReLU()
        )
        self.fc1 = torch.nn.Linear(32 * 32, 512)
        self.fc2 = torch.nn.Linear(512, 2)

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
        out = self.fc2(out)
        return out


class PredictNv(object):
    def __init__(self, model_path):
        self.train_X = None
        self.train_Y = None
        self.CNN_nv = CNN_nv()
        self.load_model(path=model_path)

    def load_model(self, path):
        target_folder = os.path.join(os.path.dirname(path), os.path.basename(path)[:-3])
        with tarfile.open(path, 'r') as tar:
            tar.extractall(path=target_folder)
        model_cnn = os.path.join(target_folder, 'CNN_nv.pth.tar')
        self.CNN_nv.load_state_dict(torch.load(model_cnn, map_location='cpu')['state_dict'])
        self.train_X = np.load(os.path.join(target_folder, 'Train_X.npy'), allow_pickle=True)
        self.train_Y = np.load(os.path.join(target_folder, 'Train_Y.npy'), allow_pickle=True)
        shutil.rmtree(target_folder)

    def train_data(self):
        # #获取训练数据：特征和标签。
        train_size = 1
        data = list(zip(self.train_X, self.train_Y))
        train_num = int(train_size * len(data))
        train_data = data[:train_num]
        # x1：上升段TFnv；x2：稳定段nv；Y
        train_data_x1 = np.array([x[0] for x in train_data])
        # 归一化处理的四个参数
        train_data_x1_mean = train_data_x1.reshape(-1, 4).mean(axis=0)  # x1上升段TFnv的均值
        train_data_x1_std = train_data_x1.reshape(-1, 4).std(axis=0)  # x1上升段TFnv的均值
        return train_data_x1_mean, train_data_x1_std

    def calculate(self, TBM_key_data):
        train_data_x1_mean, train_data_x1_std = self.train_data()
        np.random.seed(111)
        perm_N = np.random.permutation(TBM_key_data.shape[0])[:30]
        TBM_key_data = TBM_key_data.reset_index(drop=True)  # 重建提取数据的行索引
        test_data_x1 = np.array([TBM_key_data.loc[perm_N, ['刀盘转速', '刀盘扭矩', '总推进力', '推进速度']].values])
        test_data_x1 = ((test_data_x1 - train_data_x1_mean) / train_data_x1_std).astype(float)
        result_nv = pd.DataFrame((self.CNN_nv([torch.FloatTensor(test_data_x1)])).detach().numpy())
        return round(result_nv.iloc[0, 0], 2), round(result_nv.iloc[0, 1], 2)
