# -*- coding: utf-8 -*-
# ************************************************************************
# * Software:  Main  for  Python                                         *
# * Version:  1.0.0                                                      *
# * Date:  2023-03-30 00:00:00                                           *
# * Last  update: 2023-03-30 00:00:00                                    *
# * License:  LGPL v1.0                                                  *
# * Maintain  address:  https://pan.baidu.com/s/1SKx3np-9jii3Zgf1joAO4A  *
# * Maintain  code:  STBM                                                *
# ************************************************************************

import sys

from PyQt5.QtWidgets import QApplication
from Program.DataPreProcess import DataPreProcess
from Program.RockMassPredict import RockMassPredict
from Program.HobWearRate import HobWearRate
from Program.ResponseParmPredict import ResponseParmPredict
from Program.ControlParmRecommend import ControlParmRecommend
from Program.SoilConditionAnalysis import SoilConditionAnalysis
from Program.Window import Window
from Program.DataCollect import DataCollect
from Program.CycleSave import CycleSave

app = QApplication(sys.argv)
window = Window()
window.show()
collect = DataCollect([DataPreProcess, CycleSave, RockMassPredict, HobWearRate, ResponseParmPredict,
                       ControlParmRecommend, SoilConditionAnalysis])
window.threads = collect.threads
window.values = collect.values.ShowVar
window.History = collect.values.History
sys.exit(app.exec_())
