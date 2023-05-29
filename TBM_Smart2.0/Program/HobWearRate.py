# -*- coding: utf-8 -*-
# ************************************************************************
# * Software:  HobWearRate  for  Python                                  *
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
import time


class HobWearRate(threading.Thread):
    """滚刀磨损速率预测（prediction_hob）"""

    def __init__(self, shared_data):
        """
        初始化各参量，请勿修改
        :param shared_data: 共享变量
        """
        super(HobWearRate, self).__init__()
        self._stop_event = threading.Event()
        self.shared_data = shared_data  # 引入共享，使其变为可编辑状态

        self.run_fuc = 'function1'
        self.time_interval = 120
        self.time_num = copy.deepcopy(self.time_interval)

    def run(self):
        """
        运行线程内的代码，请勿修改
        self.shared_data.RawVar为原始的每秒数据记录，格式为DataFrame
        self.shared_data为待汇总的数据记录，格式为dict"""
        while not self._stop_event.is_set():  # 循环运行
            if self.shared_data.BasicVar['raw-data'].shape[0] >= 30:
                if self.time_num == self.time_interval:
                    try:
                        if self.run_fuc == 'function1':
                            predict_hob = self.function1()
                        elif self.run_fuc == 'function2':
                            predict_hob = self.function2()
                        else:
                            predict_hob = '--'
                            print('\033[0;31m%s -> Function <%s> does not exist, please check!\033[0m'
                                  % (self.__class__.__name__, self.run_fuc))
                        self.shared_data.ShowVar['滚刀磨损速率'] = predict_hob
                    except Exception as e:
                        print('\033[0;31m%s -> Error, %s !!!\033[0m' % (self.__class__.__name__, e))
                    self.time_num = 0
                else:
                    self.time_num += 1
            else:
                self.shared_data.ShowVar['滚刀磨损速率'] = '--'
            time.sleep(1)
        print('\033[0;33m%s -> Thread stopped.\n\033[0m' % self.__class__.__name__)

    def stop(self):
        self._stop_event.set()

    def function1(self) -> str:
        """
        将滚刀磨损速率预测相关代码放置在这里
        :return: 滚刀磨损速率预测（prediction_hob）->-> ('低', '中', '高')
        """
        # 破岩指标（TPI_mean, TPI_std, FPI_mean, FPI_std, WR_mean, WR_std, a, b, r2}），请勿修改
        rock_index = copy.deepcopy(self.shared_data.BasicVar['rock-index'])  # 数据格式 DataFrame
        # 破岩关键数据(桩号, 运行时间, 刀盘转速, 刀盘给定转速显示值, 推进速度, 推进给定速度百分比, 总推进力,
        #            刀盘扭矩, 贯入度, 推进位移, 推进压力, 冷水泵压力, 控制泵压力, 撑紧压力, 左撑靴油缸行程检测,
        #            右撑靴油缸行程检测, 主机皮带机转速, 顶护盾压力, 左侧护盾压力, 右侧护盾压力, 左侧护盾位移,
        #            右侧护盾位移, 推进泵电机电流)，请勿修改
        key_data = copy.deepcopy(self.shared_data.BasicVar['raw-data'])  # 数据格式 DataFrame
        # 历史掘进段数据，请勿修改
        passed_data = copy.deepcopy(self.shared_data.BasicVar['passed-data'])  # 数据格式 list

        # 以下代码仅在测试时使用，可将其删除
        prediction_hob = '--'
        # 以上代码仅在测试时使用，可将其删除

        return prediction_hob  # 返回数据，请勿修改，数据格式为 str

    def function2(self) -> str:
        """
        将滚刀磨损速率预测相关代码放置在这里
        :return: 滚刀磨损速率预测（prediction_hob）->-> ('低', '中', '高')
        """
        # 破岩指标（TPI_mean, TPI_std, FPI_mean, FPI_std, WR_mean, WR_std, a, b, r2}），请勿修改
        rock_index = copy.deepcopy(self.shared_data.BasicVar['rock-index'])  # 数据格式 DataFrame
        # 破岩关键数据(桩号, 运行时间, 刀盘转速, 刀盘给定转速显示值, 推进速度, 推进给定速度百分比, 总推进力,
        #            刀盘扭矩, 贯入度, 推进位移, 推进压力, 冷水泵压力, 控制泵压力, 撑紧压力, 左撑靴油缸行程检测,
        #            右撑靴油缸行程检测, 主机皮带机转速, 顶护盾压力, 左侧护盾压力, 右侧护盾压力, 左侧护盾位移,
        #            右侧护盾位移, 推进泵电机电流)，请勿修改
        key_data = copy.deepcopy(self.shared_data.BasicVar['raw-data'])  # 数据格式 DataFrame
        # 历史掘进段数据，请勿修改
        passed_data = copy.deepcopy(self.shared_data.BasicVar['passed-data'])  # 数据格式 list

        # 以下代码仅在测试时使用，可将其删除
        Random = random.randint(0, 300)
        prediction_hob = '低' if Random < 100 else ('中' if Random < 200 else '高')
        # 以上代码仅在测试时使用，可将其删除

        return prediction_hob  # 返回数据，请勿修改，数据格式为 str
