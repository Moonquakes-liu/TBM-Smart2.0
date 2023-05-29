#!/usr/bin/env python
# -*- coding: utf-8 -*-
# ************************************************************************
# * Software:  MachineInformation  for  Python                           *
# * Version:  1.0.0                                                      *
# * Date:  2023-03-30 00:00:00                                           *
# * Last  update: 2023-03-30 00:00:00                                    *
# * License:  LGPL v1.0                                                  *
# * Maintain  address:  https://pan.baidu.com/s/1SKx3np-9jii3Zgf1joAO4A  *
# * Maintain  code:  STBM                                                *
# ************************************************************************


def MachineInformation() -> dict:
    """设备信息录入"""
    machine_info = {'刀盘转速-容许': 9, '推进速度-容许': 120, '刀盘扭矩-容许': 4000, '刀盘推力-容许': 20000, '贯入度-容许': 20,
                    '刀盘转速-脱困': 12, '推进速度-脱困': 150, '刀盘扭矩-脱困': 5000, '刀盘推力-脱困': 25000, '贯入度-脱困': 25}
    return machine_info  # 设备信息，请勿修改， 格式为dict

