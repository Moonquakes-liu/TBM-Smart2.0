#!/usr/bin/env python
# -*- coding: utf-8 -*-
# ************************************************************************
# * Software:  Window  for  Python                                       *
# * Version:  1.0.0                                                      *
# * Date:  2023-05-12 00:00:00                                           *
# * Last  update: 2023-03-30 00:00:00                                    *
# * License:  LGPL v1.0                                                  *
# * Maintain  address:  https://pan.baidu.com/s/1SKx3np-9jii3Zgf1joAO4A  *
# * Maintain  code:  STBM                                                *
# ************************************************************************

import copy
import math
import os
import sys
import traceback
import numpy as np
import pandas as pd
import psutil
from PyQt5.QtChart import QScatterSeries, QDateTimeAxis, QChart, QChartView
from PyQt5.QtChart import QPieSeries, QLineSeries, QValueAxis, QAreaSeries, QLegend, QPolarChart, QCategoryAxis
from PyQt5.QtCore import Qt, QPoint, QRectF, QPointF, QTimer, QDateTime, QRect, QMargins
from PyQt5.QtGui import QColor, QPixmap, QBrush, QPalette, QPainter, QFont, QPolygon, QPen, QRadialGradient, QRegion
from PyQt5.QtWidgets import QApplication, QWidget, QGridLayout, QMainWindow, QMessageBox
from PyQt5.QtWidgets import QLabel, QProgressBar, QDesktopWidget, QPushButton, QGraphicsTextItem
from matplotlib import pyplot as plt
from matplotlib.figure import Figure
from matplotlib.patches import Wedge
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas


class Window(QMainWindow):
    def __init__(self, time_interval=1):
        super().__init__()
        self.threads = []
        self.values = {'PLC状态': False, '里程': '--', '运行时间': '--',
                       '刀盘转速-当前': '--', '推进速度-当前': '--', '刀盘扭矩-当前': '--', '刀盘推力-当前': '--', '贯入度-当前': '--',
                       '刀盘转速-预测': '--', '推进速度-预测': '--', '刀盘扭矩-预测': '--', '刀盘推力-预测': '--', '贯入度-预测': '--',
                       '刀盘转速-之前': '--', '推进速度-之前': '--', '刀盘扭矩-之前': '--', '刀盘推力-之前': '--', '贯入度-之前': '--',
                       '刀盘转速-容许': 1, '推进速度-容许': 1, '刀盘扭矩-容许': 1, '刀盘推力-容许': 1, '贯入度-容许': 1,
                       '刀盘转速-脱困': 2, '推进速度-脱困': 2, '刀盘扭矩-脱困': 2, '刀盘推力-脱困': 2, '贯入度-脱困': 2,
                       '施工状态': '--', '当前围岩类型': '--', 'Ⅱ类Ⅲ类围岩概率': '--', 'Ⅳ类Ⅴ类围岩概率': '--',
                       '建议支护方式': '--', '风险状态': '--', 'TPI-平均': 0, 'FPIa-平均': 0, 'FPIb-平均': 0,
                       '推荐刀盘转速': '--', '推荐推进速度': '--', '滚刀磨损速率': '--', '渣片分析状况': '--'}
        self.values_last = copy.deepcopy(self.values)
        self.values_last['PLC状态'] = True
        self.timeout = 5
        self.time_count = 0
        self.History = []
        self.history_window = History_info()
        self.showFullScreen()
        # self.setFixedSize(1024, 768)
        # 将图形添加到主窗口
        widget = QWidget()
        BGImage = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'Resources\\BGImages.png')
        brush = QBrush(QPixmap(BGImage))
        palette = QPalette()
        palette.setBrush(QPalette.Background, brush)
        widget.setPalette(palette)
        widget.setAutoFillBackground(True)  # 需要将自动填充背景设置为True
        Width, Height = (self.size().width() - 34) / 42, (self.size().height() - 40) / 22
        self.Module1 = Module1(width=(self.size().width() - 22) / 42 * 42, height=(self.size().height() - 45) / 22 * 1)
        self.Module2 = Module2(width=Width * 14, height=Height * 6)
        self.Module3 = Module3(width=Width * 14, height=Height * 6)
        self.Module4 = Module4(width=Width * 14, height=Height * 6)
        self.Module5 = Module5(width=Width * 14, height=Height * 7)
        self.Module6 = Module6(width=Width * 14, height=Height * 7)
        self.Module7 = Module7(width=Width * 14, height=Height * 8)
        self.Module8 = Module8(width=Width * 14, height=Height * 8)
        self.Module9 = Module9(width=Width * 14, height=Height * 14)
        self.ModuleWarning = {'object': WarningWindows(), 'switch': False}
        self.Widget10 = QWidget()
        palette = QPalette()
        palette.setColor(QPalette.Window, QColor(255, 255, 255, 0))
        self.Widget10.setPalette(palette)
        self.Widget10.setAutoFillBackground(True)  # 需要将自动填充背景设置为True
        self.layout10 = QGridLayout()
        # 创建一个按钮
        self.button_1 = QPushButton("历史信息")
        self.button_1.setFixedSize(100, 30)
        self.button_1.clicked.connect(self.open_history_window)
        self.button_2 = QPushButton("日报/周报")
        self.button_2.setFixedSize(100, 30)
        self.button_2.clicked.connect(self.open_report_window)
        self.button_3 = QPushButton("退  出")
        self.button_3.setFixedSize(100, 30)
        self.button_3.clicked.connect(self.closeEvent)
        # 将按钮添加到布局中
        layout10 = QGridLayout()
        layout10.addWidget(self.button_1, 0, 0, 1, 1)
        layout10.addWidget(self.button_2, 0, 1, 1, 1)
        layout10.addWidget(self.button_3, 0, 2, 1, 1)
        self.Widget10.setLayout(layout10)
        self.layout = QGridLayout()
        self.layout.addWidget(self.Module1, 0, 0, 1, 42)
        self.layout.addWidget(self.Module2, 1, 0, 6, 14)
        self.layout.addWidget(self.Module3, 1, 14, 6, 14)
        self.layout.addWidget(self.Module4, 1, 28, 6, 14)
        self.layout.addWidget(self.Module5, 7, 0, 7, 14)
        self.layout.addWidget(self.Module6, 7, 28, 7, 14)
        self.layout.addWidget(self.Module8, 14, 0, 8, 14)
        self.layout.addWidget(self.Module7, 14, 28, 8, 14)
        self.layout.addWidget(self.Module9, 7, 14, 14, 14)
        self.layout.addWidget(self.Widget10, 21, 14, 1, 14)
        widget.setLayout(self.layout)
        self.setCentralWidget(widget)
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_figure)
        self.timer.start(int(time_interval * 1000))
        self.timer1 = QTimer(self)
        self.timer1.timeout.connect(self.update_roll)
        self.timer1.start(30)

    def update_figure(self):
        if {key: self.values[key] for key in ['PLC状态']} != {key: self.values_last[key] for key in ['PLC状态']}:
            self.time_count = self.timeout
        if not self.values['PLC状态'] and self.time_count >= 0:
            self.time_count -= 1
        if not self.values['PLC状态'] and self.time_count == 0:
            self.layout.addWidget(self.ModuleWarning['object'], 1, 0, 21, 42)
            self.ModuleWarning['switch'] = True
        if self.values['PLC状态'] and self.time_count == self.timeout and self.ModuleWarning['switch']:
            self.layout.removeWidget(self.ModuleWarning['object'])
            self.ModuleWarning['object'].deleteLater()
            self.ModuleWarning = {'object': WarningWindows(), 'switch': False}
        # noinspection PyBroadException
        try:
            self.Module2.set_changeable(real_values=self.values, last_values=self.values_last)
            self.Module3.set_changeable(real_values=self.values, last_values=self.values_last)
            self.Module4.set_changeable(real_values=self.values, last_values=self.values_last)
            self.Module5.set_changeable(real_values=self.values, last_values=self.values_last)
            self.Module6.set_changeable(real_values=self.values, last_values=self.values_last)
            self.Module7.set_changeable(self.values)
            self.Module8.set_changeable(real_values=self.values, last_values=self.values_last)
            self.Module9.set_changeable(real_values=self.values, last_values=self.values_last)
        except Exception:
            QMessageBox.critical(self, 'Error', 'Module9:\n' + traceback.format_exc())
        self.values_last = copy.deepcopy(self.values)

    def update_roll(self):
        rock, probability = '待生成', '待生成'
        if '--' not in [self.values['当前围岩类型'], self.values['Ⅱ类Ⅲ类围岩概率'], self.values['Ⅳ类Ⅴ类围岩概率']]:
            rock = self.values['当前围岩类型']
            if self.values['Ⅱ类Ⅲ类围岩概率'] > self.values['Ⅳ类Ⅴ类围岩概率']:
                probability = '%s%% - 当前' % self.values['Ⅱ类Ⅲ类围岩概率']
            else:
                probability = '%s%% - 当前' % self.values['Ⅳ类Ⅴ类围岩概率']
        text = '预测围岩类别：%s  概率：%s' % (rock, probability)
        if not self.values['PLC状态']:
            text = 'PLC连接已断开，正在尝试重连...'
        self.Module1.set_changeable(text)

    def open_history_window(self):
        if len(self.history_window.history) > 0:
            self.history_window.update_figure(-1)
            self.history_window.Button['页面导航'].setText('第%d页/共%d页' % (1, len(self.history_window.history)))
        else:
            self.history_window.Button['页面导航'].setText('第%d页/共%d页' % (0, len(self.history_window.history)))
        self.history_window.history = self.History
        self.history_window.show()

    @staticmethod  # 不强制要求传递参数
    def open_report_window():
        message_box = QMessageBox()
        message_box.setIcon(QMessageBox.Information)
        message_box.setText('此功能正在努力开发中...')
        message_box.setWindowTitle('提示')
        message_box.setStandardButtons(QMessageBox.Ok)
        message_box.setDefaultButton(QMessageBox.Ok)
        message_box.exec_()

    def closeEvent(self, event):
        # 点击按钮时退出窗口并结束程序
        reply = QMessageBox.question(self, '提示', '确认退出吗？', QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        if reply == QMessageBox.Yes:
            for thread in self.threads.values():  # 停止相关线程
                thread.stop()
            QApplication.quit()  # 如果用户确认退出，则退出应用程序


class WarningWindows(QWidget):
    def __init__(self):
        super(WarningWindows, self).__init__()
        palette = QPalette()
        palette.setColor(QPalette.Window, QColor(255, 255, 255, 0))
        self.setPalette(palette)
        self.setAutoFillBackground(True)  # 需要将自动填充背景设置为True

    def paintEvent(self, event):
        width = self.width()
        height = self.height()
        painter = QPainter(self)  # 初始化painter
        painter.setPen(QColor(255, 0, 0))
        painter.setRenderHint(QPainter.Antialiasing)  # 打开抗锯齿提示
        painter.translate(width / 2, height / 2)  # 坐标轴变换，调用translate()将坐标原点平移至窗口中心
        plot_1 = QPolygon(
            [QPoint(width / 5, height / 10), QPoint(width / 5, -height / 10), QPoint(-width / 5, -height / 10),
             QPoint(-width / 5, height / 10)])
        painter.drawPolygon(plot_1)
        plot_2 = QPolygon(
            [QPoint(width / 5.8, height / 16), QPoint(width / 5.5, height / 16), QPoint(width / 5.5, -height / 16),
             QPoint(width / 5.8, -height / 16)])
        painter.drawPolyline(plot_2)
        plot_3 = QPolygon(
            [QPoint(-width / 5.8, height / 16), QPoint(-width / 5.5, height / 16), QPoint(-width / 5.5, -height / 16),
             QPoint(-width / 5.8, -height / 16)])
        painter.drawPolyline(plot_3)
        plot_4 = QPolygon([QPoint(-width / 20, height / 23), QPoint(width / 20, height / 23)])
        painter.drawPolyline(plot_4)
        plot_5 = QPolygon([QPoint(-width / 20, -height / 23), QPoint(width / 20, -height / 23)])
        painter.drawPolyline(plot_5)
        plot_6 = QPolygon([QPoint(0 - width / 7, -height / 30), QPoint(-width / 50 - width / 7, height / 30),
                           QPoint(width / 50 - width / 7, height / 30)])
        painter.drawPolygon(plot_6)
        plot_7 = QPolygon([QPoint(0 + width / 7, -height / 30), QPoint(-width / 50 + width / 7, height / 30),
                           QPoint(width / 50 + width / 7, height / 30)])
        painter.drawPolygon(plot_7)
        painter.setFont(QFont('黑体', 25))
        painter.drawText(0 + width / 7.3, height / 45, '!')
        painter.drawText(0 - width / 6.75, height / 45, '!')
        painter.setFont(QFont('黑体', 20))
        painter.drawText(0 - width / 10.5, height / 100, 'PLC CONNECTION FAILURE!')
        painter.setBrush(QColor(255, 0, 0, 0.8 * 255))
        painter.setPen(Qt.NoPen)
        for i in range(-int(width / 5.3), int(width / 5.2), int(2 * width / 5 / 40)):
            pts, pts1 = QPolygon(), QPolygon()
            pts.setPoints(5 + i, -6 + 90, 10 + i, -6 + 90, -5 + i, 6 + 90, -10 + i, 6 + 90)
            pts1.setPoints(5 + i, -6 - 90, 10 + i, -6 - 90, -5 + i, 6 - 90, -10 + i, 6 - 90)
            painter.drawConvexPolygon(pts), painter.drawConvexPolygon(pts1)
        painter.setBrush(QColor(255, 0, 0, 0.3 * 255))
        pts2 = QPolygon()
        pts2.setPoints(width / 5, height / 10, width / 5, -height / 10, -width / 5, -height / 10, -width / 5,
                       height / 10)
        painter.drawConvexPolygon(pts2)


class Module1(QWidget):
    def __init__(self, width, height):
        super(Module1, self).__init__()
        self.setFixedSize(int(width), int(height))
        palette = QPalette()
        palette.setColor(QPalette.Window, QColor(255, 255, 255, 20))
        self.setPalette(palette)
        self.setAutoFillBackground(True)  # 需要将自动填充背景设置为True
        self.label = QLabel('预测围岩类别：待生成     概率：待生成')
        self.label.setFont(QFont('黑体'))
        self.label.setStyleSheet('color: white; font-size: 24px;; background-color: rgba(0,0,0,0)')
        self.label.setFixedSize(500, int(height / 2))  # 设置QLabel的位置和大小
        self.label.setAlignment(Qt.AlignTop)
        self.layout = QGridLayout()
        self.setLayout(self.layout)
        self.layout.addWidget(self.label)

    def set_changeable(self, text):
        current_pos = self.label.pos()
        new_pos = current_pos - QPoint(5, 0)
        self.label.move(new_pos)
        # 如果已经滚出屏幕，则重新开始滚动
        if self.label.pos().x() + self.label.width() < 0:
            self.label.setText(text)
            self.label.move(QPoint(self.width(), self.label.pos().y()))


class Module2(QWidget):
    def __init__(self, width, height):
        super(Module2, self).__init__()
        self.setFixedSize(int(width), int(height))
        self.width, self.height = width, height
        palette = QPalette()
        palette.setColor(QPalette.Window, QColor(255, 255, 255, 20))
        self.setPalette(palette)
        self.setAutoFillBackground(True)  # 需要将自动填充背景设置为True
        self.Var = {'建议支护方式': '--', '预测围岩分类': '--', '风险掘进提示': '--'}
        self.module = {'建议支护方式': QRect(55, 68, 240, 60), '预测围岩分类': QRect(55, 192, 240, 60),
                       '风险掘进提示': QRect(385, 110, 30, 120)}

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setPen(QPen(QColor(0, 170, 208)))
        painter.setRenderHint(QPainter.Antialiasing)  # 打开抗锯齿提示
        self.set_invariant(painter)

    def set_invariant(self, Object):
        def ax(x):
            return int(x * self.width / 640)

        def ay(y):
            return int(y * self.height / 295)

        plot_1 = QPolygon([QPoint(ax(48), ay(168)), QPoint(ax(176), ay(168)), QPoint(ax(192), ay(191)),
                           QPoint(ax(288), ay(191)), QPoint(ax(288), ay(250)), QPoint(ax(48), ay(250))])
        Object.drawPolygon(plot_1)
        Object.setFont(QFont('Simhei', 12))
        Object.drawText(ax(50), ay(170), ax(128), ay(23), Qt.AlignHCenter | Qt.AlignVCenter, '建议支护方式')
        plot_2 = QPolygon([QPoint(ax(48), ay(44)), QPoint(ax(176), ay(44)), QPoint(ax(192), ay(67)),
                           QPoint(ax(288), ay(67)), QPoint(ax(288), ay(126)), QPoint(ax(48), ay(126))])
        Object.drawPolygon(plot_2)
        Object.drawText(ax(50), ay(46), ax(128), ay(23), Qt.AlignHCenter | Qt.AlignVCenter, '预测围岩分类')
        plot_3 = QPolygon([QPoint(ax(356), ay(44)), QPoint(ax(592), ay(44)), QPoint(ax(592), ay(235)),
                           QPoint(ax(572), ay(250)), QPoint(ax(336), ay(250)), QPoint(ax(336), ay(60))])
        Object.setFont(QFont('Simhei', 17))
        Object.drawText(ax(342), ay(63), ax(243), ay(30), Qt.AlignHCenter | Qt.AlignVCenter, '风险掘进提示')
        Object.drawPolygon(plot_3)
        Object.setFont(QFont('Simhei', 15))
        Object.setPen(QPen(QColor(242, 242, 242)))
        Object.drawText(ax(55), ay(68), ax(240), ay(60), Qt.AlignHCenter | Qt.AlignVCenter, self.Var['预测围岩分类'])
        Object.drawText(ax(55), ay(192), ax(240), ay(60), Qt.AlignHCenter | Qt.AlignVCenter, self.Var['建议支护方式'])
        Object.setFont(QFont('Simhei', 12))
        Object.drawText(ax(412), ay(115), ax(150), ay(23), Qt.AlignHCenter | Qt.AlignVCenter, '安全掘进')
        Object.drawText(ax(412), ay(160), ax(150), ay(23), Qt.AlignHCenter | Qt.AlignVCenter, '预警观察')
        Object.drawText(ax(412), ay(205), ax(150), ay(23), Qt.AlignHCenter | Qt.AlignVCenter, '风险控制')
        a = [QColor(242, 242, 242), QColor(0, 255, 0, 0)]
        b = [QColor(242, 242, 242), QColor(255, 215, 0, 0)]
        c = [QColor(242, 242, 242), QColor(255, 0, 0, 0)]
        if self.Var['风险掘进提示'] == '安全掘进':
            a = [QColor(242, 242, 242, 0), QColor(0, 255, 0)]
        elif self.Var['风险掘进提示'] == '预警观察':
            b = [QColor(242, 242, 242, 0), QColor(255, 215, 0)]
        elif self.Var['风险掘进提示'] == '风险控制':
            c = [QColor(242, 242, 242, 0), QColor(255, 0, 0)]
        Object.setPen(a[0]), Object.setBrush(a[1])
        Object.drawEllipse(ax(397), ay(119), ax(17), ay(17))
        Object.setPen(b[0]), Object.setBrush(b[1])
        Object.drawEllipse(ax(397), ay(164), ax(17), ay(17))
        Object.setPen(c[0]), Object.setBrush(c[1])
        Object.drawEllipse(ax(397), ay(209), ax(17), ay(17))
        region = QRegion(self.module['预测围岩分类']) + QRegion(self.module['建议支护方式']) + QRegion(self.module['风险掘进提示'])
        Object.setClipRegion(region)  # 设置绘图区域为矩形区域

    def set_changeable(self, real_values, last_values):
        keys = ['当前围岩类型', 'Ⅱ类Ⅲ类围岩概率', 'Ⅳ类Ⅴ类围岩概率']
        if {key: real_values[key] for key in keys} != {key: last_values[key] for key in keys}:
            if '--' not in [real_values['当前围岩类型'], real_values['Ⅱ类Ⅲ类围岩概率'], real_values['Ⅳ类Ⅴ类围岩概率']]:
                if real_values['Ⅱ类Ⅲ类围岩概率'] > real_values['Ⅳ类Ⅴ类围岩概率']:
                    probability = real_values['Ⅱ类Ⅲ类围岩概率']
                else:
                    probability = real_values['Ⅳ类Ⅴ类围岩概率']
                rock = '%s（%d%%）' % (real_values['当前围岩类型'], probability)
            else:
                rock = '--'
            self.Var['预测围岩分类'] = rock
            self.update(self.module['预测围岩分类'])  # 只重绘标签1和标签2
        if real_values['建议支护方式'] != last_values['建议支护方式']:
            self.Var['建议支护方式'] = real_values['建议支护方式']
            self.update(self.module['建议支护方式'])  # 只重绘标签1和标签2
        if real_values['风险状态'] != last_values['风险状态']:
            self.Var['风险掘进提示'] = real_values['风险状态']
            self.update(self.module['风险掘进提示'])  # 只重绘标签1和标签2


class Module3(QWidget):
    def __init__(self, width, height):
        super(Module3, self).__init__()
        self.setFixedSize(int(width), int(height))
        self.width, self.height = width, height
        palette = QPalette()
        palette.setColor(QPalette.Window, QColor(255, 255, 255, 20))
        self.setPalette(palette)
        self.setAutoFillBackground(True)  # 需要将自动填充背景设置为True
        self.Var = {'推荐推进速度': '--', '推荐刀盘转速': '--'}
        self.module = {'推荐推进速度': QRect(419, 175, 60, 28), '推荐刀盘转速': QRect(139, 175, 60, 28)}
        self.Pointer = {'推荐推进速度': QPolygon(), '推荐刀盘转速': QPolygon()}
        self.angle = {'推荐推进速度': -270 / 100 * 50, '推荐刀盘转速': -270 / 100 * 50}
        self.module = {'推荐刀盘转速': QRect(80, 40, 200, 200), '推荐推进速度': QRect(360, 40, 200, 200)}

    def paintEvent(self, event):
        painter = QPainter(self)  # 初始化painter
        # 启用反锯齿，使画出的曲线更平滑
        painter.setRenderHints(QPainter.Antialiasing | QPainter.TextAntialiasing)
        self.set_invariant(painter)

    def ax(self, x):
        return int(x * self.width / 640)

    def ay(self, y):
        return int(y * self.height / 295)

    def set_invariant(self, Object):
        self.board(Object, x=self.ax(80), y=self.ay(40), r=self.ax(90))
        self.pointer(Object=Object, name='推荐刀盘转速', x=self.ax(80 + 90), y=self.ay(40) + self.ax(90))
        Object.setFont(QFont("黑体", 14))
        Object.setPen(QColor(255, 255, 255))  # 还是用自己选的颜色
        Object.drawText(self.ax(98), self.ay(240), '推荐刀盘转速')
        Object.setFont(QFont("黑体", 24))
        Object.drawText(self.ax(139), self.ay(175), self.ax(60), self.ay(28),
                        Qt.AlignHCenter | Qt.AlignVCenter, self.Var['推荐刀盘转速'])
        self.board(Object, x=self.ax(360), y=self.ay(40), r=self.ax(90))
        self.pointer(Object=Object, name='推荐推进速度', x=self.ax(360 + 90), y=self.ay(40) + self.ax(90))
        Object.setFont(QFont("黑体", 14))
        Object.setPen(QColor(255, 255, 255))  # 还是用自己选的颜色
        Object.drawText(self.ax(378), self.ay(240), '推荐推进速度')
        Object.setFont(QFont("黑体", 24))
        Object.drawText(self.ax(419), self.ay(175), self.ax(60), self.ay(28),
                        Qt.AlignHCenter | Qt.AlignVCenter, self.Var['推荐推进速度'])
        region = QRegion(self.module['推荐刀盘转速']) + QRegion(self.module['推荐推进速度'])
        Object.setClipRegion(region)  # 设置绘图区域为矩形区域

    def set_changeable(self, real_values, last_values):
        if real_values['推荐刀盘转速'] != last_values['推荐刀盘转速']:
            if real_values['推荐刀盘转速'] == '--':
                self.Var['推荐刀盘转速'] = '--'
                self.angle['推荐刀盘转速'] = -270 / 100 * 50
            else:
                self.Var['推荐刀盘转速'] = '%2d%%' % real_values['推荐刀盘转速']
                self.angle['推荐刀盘转速'] = 270 / 100 * (real_values['推荐刀盘转速'] - 50)
            self.update(self.module['推荐刀盘转速'])  # 只重绘标签1和标签2
        if real_values['推荐推进速度'] != last_values['推荐推进速度']:
            if real_values['推荐推进速度'] == '--':
                self.Var['推荐推进速度'] = '--'
                self.angle['推荐推进速度'] = -270 / 100 * 50
            else:
                self.Var['推荐推进速度'] = '%2d%%' % real_values['推荐推进速度']
                self.angle['推荐推进速度'] = 270 / 100 * (real_values['推荐推进速度'] - 50)
            self.update(self.module['推荐推进速度'])  # 只重绘标签1和标签2

    def board(self, Object, x, y, r=90):
        radius = r  # 半径
        Object.setPen(Qt.NoPen)
        rect = QRectF(x, y, radius * 2, radius * 2)  # 扇形所在圆区域
        # 计算三色圆环范围角度。green：blue：red = 1：2：1
        angleAll = 360.0 - 45 - 45  # self.startAngle = 45, self.endAngle = 45
        angleStart = int(angleAll * 0.20)
        angleMid = angleAll * 0.6
        angleEnd = angleAll * 0.20
        # 圆的中心部分填充为透明色，形成环的样式
        rg = QRadialGradient(radius + x, radius + y, radius, radius + x, radius + y)  # 起始圆心坐标，半径，焦点坐标
        ratio = 0.8  # 透明：实色 = 0.8 ：1
        # 绘制绿色环
        rg.setColorAt(0, Qt.transparent)  # 透明色
        rg.setColorAt(ratio, Qt.transparent)
        rg.setColorAt(ratio + 0.01, QColor(63, 191, 127))
        rg.setColorAt(1, QColor(63, 191, 127))
        Object.setBrush(rg)
        Object.drawPie(rect, (270 - 45 - angleStart) * 16, angleStart * 16)
        # 绘制蓝色环
        rg.setColorAt(0, Qt.transparent)
        rg.setColorAt(ratio, Qt.transparent)
        rg.setColorAt(ratio + 0.01, QColor(255, 155, 0))
        rg.setColorAt(1, QColor(255, 155, 0))
        Object.setBrush(rg)
        Object.drawPie(rect, (270 - 45 - angleStart - angleMid) * 16, angleMid * 16)
        # 绘制红色环
        rg.setColorAt(0, Qt.transparent)
        rg.setColorAt(ratio, Qt.transparent)
        rg.setColorAt(ratio + 0.01, QColor(222, 0, 0))
        rg.setColorAt(1, QColor(222, 0, 0))
        Object.setBrush(rg)
        Object.drawPie(rect, (270 - 45 - angleStart - angleMid - angleEnd) * 16, angleEnd * 16)

        radius = r - 29
        offset = 5.5
        start_angle, end_angle = 5 * np.pi / 4, -1 * np.pi / 4
        for i in range(11):  # self.scaleMajor = 8, 8个主刻度
            # 正余弦计算
            sina, cosa = math.sin(start_angle - i * 3 / 2 * np.pi / 10), math.cos(start_angle - i * 3 / 2 * np.pi / 10)
            # 刻度值计算
            value = math.ceil((1.0 * i * ((100 - 0) / 10) + 0))
            strValue = str(int(value))
            # 字符的宽度和高度
            textWidth = self.fontMetrics().width(strValue)
            textHeight = self.fontMetrics().height()
            # 字符串的起始位置。注意考虑到字符宽度和高度进行微调
            X = r + x + 8 + radius * cosa - textWidth / 2
            Y = r + y - radius * sina + textHeight / 4
            Object.setFont(QFont("宋体", 6))
            Object.setPen(QColor(255, 255, 255))  # 还是用自己选的颜色
            Object.drawText(X - offset, Y, strValue)

        for i in range(50):  # self.scaleMajor = 8, 8个主刻度
            sina, cosa = math.sin(start_angle - i * 3 / 2 * np.pi / 50), math.cos(start_angle - i * 3 / 2 * np.pi / 50)
            x1, y1 = r + x + self.ax(89 * cosa), r + y - self.ax(89 * sina)
            x2, y2 = r + x + self.ax(73 * cosa), r + y - self.ax(73 * sina)
            x3, y3 = r + x + self.ax(84 * cosa), r + y - self.ax(84 * sina)
            if i % 5 == 0:
                Object.drawLine(x1, y1, x2, y2)
            else:
                Object.drawLine(x1, y1, x3, y3)

    def pointer(self, Object, name, x, y):
        Object.save()
        Object.translate(x, y)  # 坐标轴变换，调用translate()将坐标原点平移至窗口中心
        Object.setBrush(QBrush(QColor(0, 170, 208)))
        Object.setPen(QPen(QColor(0, 170, 208)))
        self.Pointer[name].setPoints(self.ax(- 5), self.ax(0), self.ax(0), self.ax(8),
                                     self.ax(5), self.ax(0), self.ax(0), self.ax(- 65))
        Object.rotate(self.angle[name])
        Object.drawPolygon(self.Pointer[name])
        Object.restore()


class Module4(QWidget):
    def __init__(self, width, height):
        super(Module4, self).__init__()
        self.setFixedSize(int(width), int(height))
        palette = QPalette()
        palette.setColor(QPalette.Window, QColor(255, 255, 255, 20))
        self.setPalette(palette)
        self.setAutoFillBackground(True)  # 需要将自动填充背景设置为True
        self.label_raw = {'刀盘扭矩预测值': QLabel('扭矩预测值'), '刀盘推力预测值': QLabel('推力预测值'),
                          '滚刀磨损速率': QLabel('滚刀磨损速率'), '渣片分析状况': QLabel('渣片状况分析')}
        self.label_new = {'刀盘扭矩-预测': QLabel('--'), '刀盘推力-预测': QLabel('--'),
                          '滚刀磨损速率': QLabel('--'), '渣片分析状况': QLabel('--')}
        self.progress = {'刀盘扭矩-预测': QProgressBar(), '刀盘推力-预测': QProgressBar(),
                         '滚刀磨损速率': QProgressBar(), '渣片分析状况': QProgressBar()}
        self.layout = QGridLayout()
        self.set_invariant()
        self.setLayout(self.layout)  # 设置 QWidget 的布局管理器

    def set_invariant(self):
        label_title = QLabel('>>> 参数预测')
        label_title.setFont(QFont('黑体', 18))
        label_title.setStyleSheet("color: white; font-size: 22px; background-color: rgba(0,0,0,0)")
        self.layout.addWidget(label_title, 0, 0, 2, 12)
        for row_rew, row_new, num in zip(self.label_raw.values(), self.label_new.values(), [4, 6, 8, 10]):
            row_rew.setStyleSheet("color: white; font-size: 18px; background-color: rgba(0,0,0,0)")
            row_rew.setAlignment(Qt.AlignCenter)
            row_rew.setFont(QFont('黑体', 13))
            row_new.setStyleSheet("color: white; font-size: 18px; background-color: rgba(0,0,0,0)")
            row_new.setAlignment(Qt.AlignCenter)
            row_new.setFont(QFont('黑体', 13))
            self.layout.addWidget(row_rew, num, 0, 2, 8), self.layout.addWidget(row_new, num, 40, 2, 6)
        for pro, num in zip(self.progress.values(), [4, 6, 8, 10]):
            pro.setFormat("")  # 将文本格式设置为空字符串，使文本不可见
            pro.setStyleSheet('''
                    QProgressBar {border-radius: 8px; background-color: rgba(221, 221, 221, 20%);  height: 18px}
                    QProgressBar::chunk {border-radius: 9px;  background-color: #2196F3;}''')
            self.layout.addWidget(pro, num, 8, 2, 30)

    def set_changeable(self, real_values, last_values):
        Var = {'刀盘扭矩-预测': [0, 100, 100], '刀盘推力-预测': [0, 100, 100], '滚刀磨损速率': [0, 40, 70], '渣片分析状况': [0, 40, 70]}
        if '--' not in [real_values['刀盘扭矩-预测'], real_values['刀盘推力-预测']]:
            Var['刀盘扭矩-预测'] = [real_values['刀盘扭矩-预测'] / real_values['刀盘扭矩-脱困'] * 100,
                              real_values['刀盘扭矩-容许'] / real_values['刀盘扭矩-脱困'] * 100, 100]
            Var['刀盘推力-预测'] = [real_values['刀盘推力-预测'] / real_values['刀盘推力-脱困'] * 100,
                              real_values['刀盘推力-容许'] / real_values['刀盘推力-脱困'] * 100, 100]
            Var['滚刀磨损速率'][0] = 100 / 3 if real_values['滚刀磨损速率'] == '低' else (
                200 / 3 if real_values['滚刀磨损速率'] == '中' else (100 if real_values['滚刀磨损速率'] == '高' else 0))
            Var['渣片分析状况'][0] = 100 / 3 if real_values['渣片分析状况'] == '良好' else (
                200 / 3 if real_values['渣片分析状况'] == '软弱' else (100 if real_values['渣片分析状况'] == '破碎' else 0))
        for name, pro, row_new in zip(self.progress.keys(), self.progress.values(), self.label_new.values()):
            Var[name][0] = Var[name][0] if Var[name][0] < 100 else 100
            if real_values[name] != last_values[name]:
                if Var[name][0] < Var[name][1]:
                    pro.setStyleSheet('''
                        QProgressBar {border-radius: 8px; background-color: rgba(221, 221, 221, 20%); height: 18px;}
                        QProgressBar::chunk {border-radius: 9px;  background-color: #00AAD0;}''')
                elif Var[name][1] <= Var[name][0] < Var[name][2]:
                    pro.setStyleSheet('''
                        QProgressBar {border-radius: 8px; background-color: rgba(221, 221, 221, 20%); height: 18px;}
                        QProgressBar::chunk {border-radius: 9px;  background-color: #FF9900;}''')
                elif Var[name][0] >= Var[name][2]:
                    pro.setStyleSheet('''
                        QProgressBar {border-radius: 8px; background-color: rgba(221, 221, 221, 20%); height: 18px;}
                        QProgressBar::chunk {border-radius: 9px;  background-color: #FF3300;}''')
                pro.setValue(Var[name][0])
                row_new.setText('%s' % (real_values[name] if real_values[name] != '--' else '--'))


class Module5(QChartView, QChart):
    def __init__(self, width, height):
        super(Module5, self).__init__()
        self.setFixedSize(int(width), int(height))
        palette = QPalette()
        palette.setColor(QPalette.Window, QColor(255, 255, 255, 20))
        self.setPalette(palette)
        self.pieSeries = QPieSeries()
        self.set_invariant()
        self.setRenderHint(QPainter.Antialiasing)
        self.chart().setBackgroundBrush(QBrush(QColor(255, 255, 255, 0)))
        self.chart().legend().setVisible(False)  # 不显示图例

    def set_invariant(self):
        pieSeries1 = QPieSeries()
        pieSeries1.setPieSize(0.65)
        pieSeries1.setHoleSize(0.645)
        pieSlice2 = pieSeries1.append('1', 1)
        pieSlice2.setBorderWidth(0)
        pieSlice2.setColor(QColor(0, 170, 208))
        pieSlice2.setBorderColor(QColor(0, 170, 208))
        self.chart().addSeries(pieSeries1)
        pieSeries2 = QPieSeries()
        pieSeries2.setPieSize(0.21)
        pieSlice3 = pieSeries2.append('1', 1)
        pieSlice3.setBorderWidth(0)
        pieSlice3.setColor(QColor(175, 213, 245))
        pieSlice3.setBorderColor(QColor(175, 213, 245))
        self.chart().addSeries(pieSeries2)
        textItem = QGraphicsTextItem(">>> 预测围岩分类")
        textItem.setPos(10, 10)
        textItem.setDefaultTextColor(Qt.white)
        textItem.setFont(QFont('黑体', 13))
        self.chart().scene().addItem(textItem)

    def set_changeable(self, real_values, last_values):
        keys = ['Ⅱ类Ⅲ类围岩概率', 'Ⅳ类Ⅴ类围岩概率']
        if {key: real_values[key] for key in keys} != {key: last_values[key] for key in keys}:
            if '--' not in [real_values['Ⅱ类Ⅲ类围岩概率'], real_values['Ⅳ类Ⅴ类围岩概率']]:
                self.pieSeries.clear()
                self.pieSeries.setHoleSize(0.23)
                self.pieSeries.setPieSize(0.60)
                pieSlice1 = self.pieSeries.append('Ⅳ类Ⅴ类 %d%%' % real_values['Ⅳ类Ⅴ类围岩概率'], real_values['Ⅳ类Ⅴ类围岩概率'])
                pieSlice1.setLabelVisible()  # 设置标签可见,缺省不可见
                pieSlice1.setBorderWidth(0)
                pieSlice1.setColor(QColor(252, 232, 0))
                pieSlice1.setLabelColor(QColor(252, 232, 0))
                pieSlice1.setBorderColor(QColor(0, 170, 208, 0))
                pieSlice1.setLabelFont(QFont('Simhei', 13))
                pieSlice1.setLabelArmLengthFactor(0.3)
                pieSlice2 = self.pieSeries.append('Ⅱ类Ⅲ类 %d%%' % real_values['Ⅱ类Ⅲ类围岩概率'], real_values['Ⅱ类Ⅲ类围岩概率'])
                pieSlice2.setLabelVisible()  # 设置标签可见,缺省不可见
                pieSlice2.setBorderWidth(0)
                pieSlice2.setColor(QColor(0, 170, 208))
                pieSlice2.setLabelColor(QColor(0, 170, 208))
                pieSlice2.setBorderColor(QColor(0, 170, 208, 0))
                pieSlice2.setLabelFont(QFont('Simhei', 13))
                pieSlice2.setLabelArmLengthFactor(0.3)
                self.chart().addSeries(self.pieSeries)
            else:
                self.pieSeries.clear()
            self.update()


class Module6(QWidget):
    def __init__(self, width, height):
        super(Module6, self).__init__()
        self.setFixedSize(int(width), int(height))
        palette = QPalette()
        palette.setColor(QPalette.Window, QColor(255, 255, 255, 20))
        self.setPalette(palette)
        self.setAutoFillBackground(True)  # 需要将自动填充背景设置为True
        self.label_raw = {'title': QLabel(''), '刀盘转速': QLabel('刀盘转速n(r/min)'), '推进速度': QLabel('推进速度v(mm/min)'),
                          '刀盘扭矩': QLabel('刀盘扭矩T(kN.m)'), '刀盘推力': QLabel('刀盘推力F(kN)'), '贯入度': QLabel('贯入度p(mm/r)')}
        self.label_now = {'title': QLabel('当前段实时值'), '刀盘转速': QLabel('--'), '推进速度': QLabel('--'),
                          '刀盘扭矩': QLabel('--'), '刀盘推力': QLabel('--'), '贯入度': QLabel('--')}
        self.label_predict = {'title': QLabel('当前段预测值'), '刀盘转速': QLabel('--'), '推进速度': QLabel('--'),
                              '刀盘扭矩': QLabel('--'), '刀盘推力': QLabel('--'), '贯入度': QLabel('--')}
        self.label_last = {'title': QLabel('前一段平均值'), '刀盘转速': QLabel('--'), '推进速度': QLabel('--'),
                           '刀盘扭矩': QLabel('--'), '刀盘推力': QLabel('--'), '贯入度': QLabel('--')}
        self.label_title = {'里程': QLabel('里程：--'), '日期': QLabel('日期：--'),
                            '时间': QLabel('时间：--'), '工作状态': QLabel('工作状态：--')}
        self.layout = QGridLayout()
        self.set_invariant()
        self.setLayout(self.layout)  # 设置 QWidget 的布局管理器

    def set_invariant(self):
        for name, col in zip(self.label_title.values(), [0, 20, 40, 60, 80]):
            self.layout.addWidget(name, 0, col, 1, 20)
            name.setStyleSheet("color: white; font-size: 17px; background-color: rgba(0,0,0,0)")
            name.setAlignment(Qt.AlignCenter)
            name.setFont(QFont('黑体', 13))
        for Label, row in zip([self.label_raw.values(), self.label_now.values(), self.label_predict.values(),
                               self.label_last.values()], [0, 20, 40, 60]):
            for name, col in zip(Label, [1, 2, 3, 4, 5, 6]):
                self.layout.addWidget(name, col, row, 1, 20)
                name.setStyleSheet("color: white; font-size: 18px; background-color: rgba(0,0,0,0)")
                name.setAlignment(Qt.AlignCenter)
                name.setFont(QFont('黑体', 13))

    def set_changeable(self, real_values, last_values):
        if '--' not in [real_values['运行时间'], real_values['里程'], real_values['施工状态']]:
            if real_values['运行时间'] != last_values['运行时间']:
                Time = pd.to_datetime(real_values['运行时间'], format='%Y-%m-%d %H:%M:%S')  # 对时间类型记录进行转换
                year, mon, d, h, m, s = Time.year, Time.month, Time.day, Time.hour, Time.minute, Time.second
                self.label_title['日期'].setText('日期：%4d-%02d-%02d' % (year, mon, d))
                self.label_title['时间'].setText('时间：%02d:%02d:%02d' % (h, m, s))
            if real_values['里程'] != last_values['里程']:
                self.label_title['里程'].setText('里程：%.2f m' % real_values['里程'])
            if real_values['施工状态'] != last_values['施工状态']:
                self.label_title['工作状态'].setText('工作状态：%4s' % real_values['施工状态'])
        if real_values['刀盘转速-当前'] != last_values['刀盘转速-当前']:
            self.label_now['刀盘转速'].setText('%s' % real_values['刀盘转速-当前'])
        if real_values['推进速度-当前'] != last_values['推进速度-当前']:
            self.label_now['推进速度'].setText('%s' % real_values['推进速度-当前'])
        if real_values['刀盘扭矩-当前'] != last_values['刀盘扭矩-当前']:
            self.label_now['刀盘扭矩'].setText('%s' % real_values['刀盘扭矩-当前'])
        if real_values['刀盘推力-当前'] != last_values['刀盘推力-当前']:
            self.label_now['刀盘推力'].setText('%s' % real_values['刀盘推力-当前'])
        if real_values['贯入度-当前'] != last_values['贯入度-当前']:
            self.label_now['贯入度'].setText('%s' % real_values['贯入度-当前'])
        if real_values['刀盘转速-预测'] != last_values['刀盘转速-预测']:
            self.label_predict['刀盘转速'].setText('%s' % real_values['刀盘转速-预测'])
        if real_values['推进速度-预测'] != last_values['推进速度-预测']:
            self.label_predict['推进速度'].setText('%s' % real_values['推进速度-预测'])
        if real_values['刀盘扭矩-预测'] != last_values['刀盘扭矩-预测']:
            self.label_predict['刀盘扭矩'].setText('%s' % real_values['刀盘扭矩-预测'])
        if real_values['刀盘推力-预测'] != last_values['刀盘推力-预测']:
            self.label_predict['刀盘推力'].setText('%s' % real_values['刀盘推力-预测'])
        if real_values['贯入度-预测'] != last_values['贯入度-预测']:
            self.label_predict['贯入度'].setText('%s' % real_values['贯入度-预测'])
        if real_values['刀盘转速-之前'] != last_values['刀盘转速-之前']:
            self.label_last['刀盘转速'].setText('%s' % real_values['刀盘转速-之前'])
        if real_values['推进速度-之前'] != last_values['推进速度-之前']:
            self.label_last['推进速度'].setText('%s' % real_values['推进速度-之前'])
        if real_values['刀盘扭矩-之前'] != last_values['刀盘扭矩-之前']:
            self.label_last['刀盘扭矩'].setText('%s' % real_values['刀盘扭矩-之前'])
        if real_values['刀盘推力-之前'] != last_values['刀盘推力-之前']:
            self.label_last['刀盘推力'].setText('%s' % real_values['刀盘推力-之前'])
        if real_values['贯入度-之前'] != last_values['贯入度-之前']:
            self.label_last['贯入度'].setText('%s' % real_values['贯入度-之前'])


class Module7(QChartView, QChart):
    series3 = {'转速(r/min)*10   ': QScatterSeries(), '速度(mm/min)   ': QScatterSeries(),
               '扭矩(kN.m)   ': QScatterSeries(), '推力(kN)/10   ': QScatterSeries()}
    axisX_B, axisX_T = None, None

    def __init__(self, width, height):
        super(Module7, self).__init__()
        self.setFixedSize(int(width), int(height))
        palette = QPalette()
        palette.setColor(QPalette.Window, QColor(255, 255, 255, 20))
        self.setPalette(palette)
        self.chart = QChart()
        self.chart.setMargins(QMargins(0, 0, 0, 0))  # 调整边距
        self.chart.setBackgroundBrush(QBrush(QColor(255, 255, 255, 0)))
        self.set_invariant()
        self.setChart(self.chart)

    def set_invariant(self):
        self.chart.setMargins(QMargins(0, 0, 0, 0))  # 调整边距
        linePen = QPen(Qt.white, 1.5)
        font = QFont()
        font.setPointSize(10)
        # 设置图例格式
        legend = self.chart.legend()  # 获取 QLegend 对象
        legend.setFont(QFont("Times New Roman", 8))  # 设置图例字体及大小
        legend.setContentsMargins(0, 0, 0, 0)  # 设置图例和边界之间的距离为0
        legend.setMarkerShape(QLegend.MarkerShapeCircle)  # 设置图例项的形状为圆形
        legend.setLabelColor(QColor('white'))
        # 设置坐标轴
        self.axisX_T, self.axisX_B, axisY_L, axisY_R = QLineSeries(), QDateTimeAxis(), QValueAxis(), QValueAxis()
        axisY_L.setTitleText("推进速度 & 刀盘转速"), axisY_R.setTitleText("刀盘推力 & 刀盘扭矩")
        self.axisX_B.setTitleFont(font), axisY_L.setTitleFont(font), axisY_R.setTitleFont(font)
        axisY_L.setRange(0, 100), axisY_R.setRange(0, 2500)
        self.axisX_B.setTickCount(6), axisY_L.setTickCount(11), axisY_R.setTickCount(11)
        self.axisX_B.setFormat("hh:mm:ss"), axisY_L.setLabelFormat("%d"), axisY_R.setLabelFormat("%d")
        self.axisX_B.setGridLineVisible(False), axisY_L.setGridLineVisible(False), axisY_R.setGridLineVisible(False)
        self.axisX_B.setLinePen(linePen), axisY_L.setLinePen(linePen), axisY_R.setLinePen(linePen)
        axisY_L.setLabelsColor(QColor("white")), axisY_R.setLabelsColor(QColor("white"))
        axisY_L.setTitleBrush(QBrush(QColor('white'))), axisY_R.setTitleBrush(QBrush(QColor('white')))
        self.axisX_B.setLabelsColor(QColor('white'))
        self.chart.addAxis(axisY_L, Qt.AlignLeft), self.chart.addAxis(axisY_R, Qt.AlignRight)
        self.chart.addAxis(self.axisX_B, Qt.AlignBottom), self.chart.addSeries(self.axisX_T)
        self.axisX_T.attachAxis(self.axisX_B), self.axisX_T.attachAxis(axisY_L)
        self.axisX_T.setPen(linePen)
        # 生成N、T、F、V数据点
        for name, axisY, color in zip(self.series3.keys(), [axisY_L, axisY_L, axisY_R, axisY_R],
                                      [Qt.white, Qt.green, Qt.red, QColor(255, 155, 0)]):
            self.chart.addSeries(self.series3[name])
            self.series3[name].setMarkerSize(4)
            self.series3[name].setColor(color)
            self.series3[name].attachAxis(self.axisX_B), self.series3[name].attachAxis(axisY)
            self.series3[name].setName(name)
            self.series3[name].setPen(QPen(Qt.transparent))
            brush = self.series3[name].brush()
            brush.setStyle(Qt.SolidPattern)
            self.series3[name].setBrush(brush)
        legend.markers()[0].setVisible(False)

    def set_changeable(self, values):
        if '--' not in [values['运行时间']]:
            Date = str(pd.to_datetime(values['运行时间'], format='%Y-%m-%d %H:%M:%S'))
        else:
            Date = str(pd.to_datetime('2008-01-01 12:00:00', format='%Y-%m-%d %H:%M:%S'))
        Max = QDateTime.fromString(Date, 'yyyy-MM-dd hh:mm:ss')
        Min = Max.addSecs(-600)
        self.axisX_T.clear()
        self.axisX_T.append(Min.toMSecsSinceEpoch(), 100)
        self.axisX_T.append(Max.toMSecsSinceEpoch(), 100)
        self.axisX_B.setRange(Min, Max)
        if '--' not in [values['刀盘转速-当前'], values['推进速度-当前'], values['刀盘扭矩-当前'], values['刀盘推力-当前']]:
            for name in self.series3.keys():
                if name == '转速(r/min)*10   ':
                    self.series3[name].append(Max.toMSecsSinceEpoch(), values['刀盘转速-当前'] * 100 / values['刀盘转速-容许'])
                if name == '速度(mm/min)   ':
                    self.series3[name].append(Max.toMSecsSinceEpoch(), values['推进速度-当前'] * 100 / values['推进速度-容许'])
                if name == '扭矩(kN.m)   ':
                    self.series3[name].append(Max.toMSecsSinceEpoch(), values['刀盘扭矩-当前'] * 2500 / values['刀盘扭矩-容许'])
                if name == '推力(kN)/10   ':
                    self.series3[name].append(Max.toMSecsSinceEpoch(), values['刀盘推力-当前'] * 2500 / values['刀盘推力-容许'])
                for point in self.series3[name].points():
                    if point.x() < Min.toMSecsSinceEpoch():
                        self.series3[name].remove(point)


class Module8(QChartView, QChart):
    series4 = {'TPI': QScatterSeries(), 'FPI': QScatterSeries(), '拟合FPI': QLineSeries(),
               '拟合TPI': QLineSeries()}
    axisX_T, axisX_B, axisY_L, axisY_R = None, None, None, None
    lower, upper, permit_F, permit_P = None, None, None, None

    def __init__(self, width, height):
        super(Module8, self).__init__()
        self.setFixedSize(int(width), int(height))
        palette = QPalette()
        palette.setColor(QPalette.Window, QColor(255, 255, 255, 20))
        self.setPalette(palette)

        self.chart4 = QChart()
        self.chart4.setBackgroundBrush(QBrush(QColor(255, 255, 255, 0)))
        self.set_invariant()
        self.setChart(self.chart4)

    def set_invariant(self):
        def set_pen(Color, line):
            pen_line = QPen(Color, 1, Qt.DotLine)
            pen_line.setDashPattern(line)
            return pen_line

        self.chart4.setMargins(QMargins(0, 0, 0, 0))  # 调整边距
        self.chart4.legend().setVisible(False)  # 不显示图例
        linePen4 = QPen(Qt.white, 1.5)
        font4 = QFont()
        font4.setPointSize(10)
        # 设置坐标轴
        self.axisX_T, self.axisX_B, self.axisY_L, self.axisY_R = QLineSeries(), QValueAxis(), QValueAxis(), QValueAxis()
        self.axisY_L.setTitleText("刀盘推力"), self.axisY_R.setTitleText("刀盘扭矩"), self.axisX_B.setTitleText('贯入度')
        self.axisX_B.setTitleFont(font4), self.axisY_L.setTitleFont(font4), self.axisY_R.setTitleFont(font4)
        self.axisX_B.setRange(0, 25), self.axisY_L.setRange(0, 25000), self.axisY_R.setRange(0, 5000)
        self.axisX_B.setTickCount(6), self.axisY_L.setTickCount(11), self.axisY_R.setTickCount(11)
        self.axisX_B.setLabelFormat("%d"), self.axisY_L.setLabelFormat("%d"), self.axisY_R.setLabelFormat("%d")
        self.axisX_B.setGridLineVisible(False), self.axisY_L.setGridLineVisible(False)
        self.axisY_R.setGridLineVisible(False)
        self.axisX_B.setLinePen(linePen4), self.axisY_L.setLinePen(linePen4), self.axisY_R.setLinePen(linePen4)
        self.axisY_L.setLinePenColor(QColor(255, 155, 0)), self.axisY_R.setLinePenColor(QColor(255, 0, 0))
        self.axisY_L.setLabelsColor(QColor(255, 155, 0)), self.axisY_R.setLabelsColor(QColor(255, 0, 0))
        self.axisY_L.setTitleBrush(QBrush(QColor(255, 155, 0))), self.axisY_R.setTitleBrush(QBrush(QColor(255, 0, 0)))
        self.axisX_B.setLabelsColor(QColor('white')), self.axisX_B.setTitleBrush(QBrush(QColor('white')))
        self.chart4.addAxis(self.axisY_L, Qt.AlignLeft), self.chart4.addAxis(self.axisY_R, Qt.AlignRight)
        self.chart4.addAxis(self.axisX_B, Qt.AlignBottom), self.chart4.addSeries(self.axisX_T)
        self.axisX_T.append(0, 25000), self.axisX_T.append(25, 25000)
        self.axisX_T.attachAxis(self.axisX_B), self.axisX_T.attachAxis(self.axisY_L)
        self.axisX_T.setPen(linePen4)
        # 设置边界线
        permit_T, self.permit_F, self.permit_P = QLineSeries(), QLineSeries(), QLineSeries()
        self.chart4.addSeries(permit_T), self.chart4.addSeries(self.permit_F), self.chart4.addSeries(self.permit_P)
        self.permit_F.attachAxis(self.axisX_B), self.permit_F.attachAxis(self.axisY_L)
        self.permit_F.setPen(set_pen(Color=QColor(255, 155, 0), line=[7, 3, 2, 3]))
        self.permit_P.attachAxis(self.axisX_B), self.permit_P.attachAxis(self.axisY_L)
        self.permit_P.setPen(set_pen(Color=Qt.green, line=[7, 3, 2, 3]))
        # 设置填充区域
        areas, self.lower, self.upper = QAreaSeries(), QLineSeries(), QLineSeries()
        areas.setUpperSeries(self.upper), areas.setLowerSeries(self.lower)
        self.chart4.addSeries(areas), self.chart4.addSeries(self.lower), self.chart4.addSeries(self.upper)
        areas.setBrush(QBrush(QColor(204, 255, 201, 40)))
        areas.setPen(QPen(Qt.NoPen)), self.lower.setPen(QPen(QColor(0, 0, 0, 0))), self.upper.setPen(QPen(QColor(0, 0, 0, 0)))
        areas.attachAxis(self.axisX_B), areas.attachAxis(self.axisY_L)
        # 拟合TPI、FPI
        for name, axisY, color in zip(['拟合FPI', '拟合TPI'], [self.axisY_L, self.axisY_R],
                                      [QColor(255, 155, 0), QColor(255, 0, 0)]):
            self.chart4.addSeries(self.series4[name])
            self.series4[name].attachAxis(self.axisX_B), self.series4[name].attachAxis(axisY)
            self.series4[name].setPen(set_pen(Color=color, line=[5, 5]))
            self.series4[name].setName(name)
        # 生成P-F, P-T数据点
        for name, axisY, color in zip(['FPI', 'TPI'], [self.axisY_L, self.axisY_R],
                                      [QColor(255, 155, 0), QColor(255, 0, 0)]):
            self.chart4.addSeries(self.series4[name])
            self.series4[name].setMarkerSize(4)
            self.series4[name].setColor(color)
            self.series4[name].attachAxis(self.axisX_B), self.series4[name].attachAxis(axisY)
            self.series4[name].setName(name)
            self.series4[name].setPen(QPen(Qt.transparent))
            brush = self.series4[name].brush()
            brush.setStyle(Qt.SolidPattern)
            self.series4[name].setBrush(brush)

    def set_changeable(self, real_values, last_values):
        keys = ['刀盘转速-容许', '推进速度-容许', '刀盘扭矩-容许', '刀盘推力-容许', '贯入度-容许',
                '刀盘转速-脱困', '推进速度-脱困', '刀盘扭矩-脱困', '刀盘推力-脱困', '贯入度-脱困']
        if {key: real_values[key] for key in keys} != {key: last_values[key] for key in keys}:
            self.axisX_T.clear()
            self.axisX_B.setRange(0, real_values['贯入度-脱困'])
            self.axisY_L.setRange(0, real_values['刀盘推力-脱困'])
            self.axisY_R.setRange(0, real_values['刀盘扭矩-脱困'])
            self.axisX_T.append(0, real_values['刀盘推力-脱困'])
            self.axisX_T.append(real_values['贯入度-脱困'], real_values['刀盘推力-脱困'])
            self.permit_F.append(0, real_values['刀盘推力-容许'])
            self.permit_F.append(real_values['贯入度-脱困'], real_values['刀盘推力-容许'])
            self.permit_P.append(real_values['贯入度-容许'], 0)
            self.permit_P.append(real_values['贯入度-容许'], real_values['刀盘推力-脱困'])
            self.upper.append(QPointF(0, 0)), self.upper.append(QPointF(real_values['贯入度-容许'], 0))
            self.lower.append(QPointF(0, real_values['刀盘推力-容许']))
            self.lower.append(QPointF(real_values['贯入度-容许'], real_values['刀盘推力-容许']))
        if real_values['施工状态'] == '正在掘进':
            for name in ['FPI', 'TPI']:
                if name == 'TPI':
                    self.series4[name].append(real_values['贯入度-当前'], real_values['刀盘扭矩-当前'])
                if name == 'FPI':
                    self.series4[name].append(real_values['贯入度-当前'], real_values['刀盘推力-当前'])
        else:
            self.series4['FPI'].clear(), self.series4['TPI'].clear()
            self.series4['拟合FPI'].clear(), self.series4['拟合TPI'].clear()
        if real_values['施工状态'] == '正在掘进':
            for name, var_k, var_b in zip(['拟合TPI', '拟合FPI'], [real_values['TPI-平均'], real_values['FPIa-平均']],
                                          [0, real_values['FPIb-平均']]):
                X, Y = np.array([0, real_values['贯入度-脱困']]), (var_k * np.array([0, real_values['贯入度-脱困']]) + var_b)
                new_line = [QPointF(X[i], Y[i]) for i in range(len(X))]
                self.series4[name].replace(new_line)


class Module9(QWidget):
    def __init__(self, width, height):
        super(Module9, self).__init__()
        self.setFixedSize(int(width), int(height))
        palette = QPalette()
        palette.setColor(QPalette.Window, QColor(255, 255, 255, 0))
        self.setPalette(palette)
        self.setAutoFillBackground(True)  # 需要将自动填充背景设置为True
        self.chart = QPolarChart()
        self.chart.setBackgroundBrush(QBrush(QColor(255, 255, 255, 0)))
        self.chart.setMargins(QMargins(0, 0, 0, 0))  # 调整边距
        self.chart.legend().setVisible(False)
        self.line_series, self.scatter_series, self.area_series = QLineSeries(), QScatterSeries(), QAreaSeries()
        self.title = QLabel('>>> 实时值/额定值')
        self.label_stage = {'CPU': QLabel('CPU:'), 'RAM': QLabel('RAM:'), 'PLC': QLabel('PLC:'),
                            'CPU使用': QLabel('--'), 'RAM使用': QLabel('--'), 'PLC状态': QLabel('--')}
        chart_view = QChartView(self.chart)
        chart_view.setRenderHint(QPainter.Antialiasing)
        self.set_invariant()
        self.layout = QGridLayout()
        self.layout.addWidget(self.title, 0, 0, 1, 10)
        self.layout.addWidget(self.label_stage['CPU'], 0, 17, 1, 4)
        self.layout.addWidget(self.label_stage['CPU使用'], 0, 21, 1, 3)
        self.layout.addWidget(self.label_stage['RAM'], 0, 24, 1, 4)
        self.layout.addWidget(self.label_stage['RAM使用'], 0, 28, 1, 3)
        self.layout.addWidget(self.label_stage['PLC'], 0, 31, 1, 4)
        self.layout.addWidget(self.label_stage['PLC状态'], 0, 35, 1, 5)
        self.layout.addWidget(chart_view, 1, 0, 40, 40)
        self.setLayout(self.layout)  # 设置 QWidget 的布局管理器

    def set_invariant(self):
        pen_No = QPen()  # 关闭画笔显示
        pen_No.setStyle(Qt.NoPen)  # 关闭画笔显示
        angular_axis, radial_axis = QCategoryAxis(), QCategoryAxis()
        angular_axis.setLabelsPosition(QCategoryAxis.AxisLabelsPositionOnValue)  # 坐标轴刻度调整
        radial_axis.setLabelsPosition(QCategoryAxis.AxisLabelsPositionOnValue)
        angular_axis.append("扭矩", 0), angular_axis.append("速度", 72), angular_axis.append("转速", 144)
        angular_axis.append("贯入度", 216), angular_axis.append("推力", 288)
        angular_axis.setLabelsColor(QColor(255, 255, 255, int(0.7 * 255)))
        angular_axis.setLinePen(pen_No), radial_axis.setLinePen(pen_No)
        self.chart.addAxis(angular_axis, QPolarChart.PolarOrientationAngular)
        self.chart.addAxis(radial_axis, QPolarChart.PolarOrientationRadial)
        angular_axis.setRange(0, 360), radial_axis.setRange(0, 141)  # 必须设置范围，否则图表无法显示
        angular_axis.setGridLineColor(QColor(255, 255, 255, int(0.7 * 255)))
        radial_axis.setLinePenColor(QColor(255, 0, 0, int(0.7 * 255)))
        angular_axis.setLabelsFont(QFont("黑体", 14))
        self.title.setFont(QFont("黑体", 15))
        self.title.setStyleSheet("color: rgba(255,255,255,1); background-color: rgba(0,0,0,0)")
        for index, text in enumerate(self.label_stage.values()):
            text.setFont(QFont("黑体", 9))
            text.setStyleSheet("color: rgba(255,255,255,1); background-color: rgba(0,0,0,0)")
            if index < 3:
                text.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
            else:
                text.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        series_line = [QLineSeries(), QLineSeries(), QLineSeries(), QLineSeries(), QLineSeries(), QLineSeries()]
        for index, line in zip([40, 60, 80, 100, 120, 140], series_line):
            [line.append(j, index) for j in range(361)]
            self.chart.addSeries(line)
            if index == 100:
                line.setColor(QColor(255, 155, 0, int(0.7 * 255)))
            elif index == 140:
                line.setColor(QColor(255, 0, 0, int(0.7 * 255)))
            else:
                pen_white_dot = QPen(QColor(255, 255, 255, int(0.7 * 255)), 1, Qt.DotLine)
                pen_white_dot.setDashPattern([7, 4])
                line.setPen(pen_white_dot)
            line.attachAxis(angular_axis), line.attachAxis(radial_axis)
        self.scatter_series.setMarkerSize(10)
        self.chart.addSeries(self.line_series), self.chart.addSeries(self.scatter_series)
        self.scatter_series.attachAxis(angular_axis), self.scatter_series.attachAxis(radial_axis)
        self.scatter_series.setPen(QPen(QColor(0, 235, 235, int(0.4 * 255)), 2))
        self.scatter_series.setColor(QColor(0, 235, 235)), self.line_series.setColor(QColor(0, 235, 235, 180))
        self.area_series.setPen(QPen(Qt.NoPen))
        self.area_series.setBrush(QBrush(QColor(0, 235, 235, 50)))
        self.area_series.setUpperSeries(self.line_series)
        self.chart.addSeries(self.area_series)
        self.area_series.attachAxis(angular_axis), self.area_series.attachAxis(radial_axis)

    def set_changeable(self, real_values, last_values):
        results = {"扭矩": 0, "推力": 0, "贯入度": 0, "转速": 0, "速度": 0}
        if '--' not in [real_values['刀盘转速-当前'], real_values['推进速度-当前'], real_values['刀盘扭矩-当前'], real_values['刀盘推力-当前'],
                        real_values['贯入度-当前']]:
            for Var, name in zip(results.keys(), ['刀盘扭矩', '刀盘推力', '贯入度', '刀盘转速', '推进速度']):
                if real_values['%s-当前' % name] <= real_values['%s-容许' % name]:
                    results[Var] = real_values['%s-当前' % name] / real_values['%s-容许' % name] * 100
                elif real_values['%s-容许' % name] <= real_values['%s-当前' % name] <= real_values['%s-脱困' % name]:
                    results[Var] = 100 + (real_values['%s-当前' % name] - real_values['%s-容许' % name]) / \
                                   (real_values['%s-脱困' % name] - real_values['%s-容许' % name]) * 40
        self.line_series.clear(), self.scatter_series.clear()
        self.line_series.append(0, results['扭矩']), self.line_series.append(72, results['速度'])
        self.line_series.append(144, results['转速']), self.line_series.append(216, results['贯入度'])
        self.line_series.append(288, results['推力']), self.line_series.append(360, results['扭矩'])
        self.scatter_series.append(0, results['扭矩']), self.scatter_series.append(72, results['速度'])
        self.scatter_series.append(144, results['转速']), self.scatter_series.append(216, results['贯入度'])
        self.scatter_series.append(288, results['推力'])
        self.label_stage['CPU使用'].setText('%2d%%' % int(psutil.cpu_percent()))
        self.label_stage['RAM使用'].setText('%2d%%' % int(psutil.virtual_memory().percent))
        if real_values['PLC状态'] != last_values['PLC状态']:
            text = 'Ready' if real_values['PLC状态'] else 'Failed'
            self.label_stage['PLC状态'].setText(text)
            if text == 'Failed':
                self.label_stage['PLC状态'].setStyleSheet("color: red; background-color: rgba(0,0,0,0)")
            elif text == 'Ready':
                self.label_stage['PLC状态'].setStyleSheet("color: rgba(0,255,0); background-color: rgba(0,0,0,0)")


class Module10(QWidget):
    def __init__(self, width, height):
        super(Module10, self).__init__()
        self.setFixedSize(int(width), int(height))
        palette = QPalette()
        palette.setColor(QPalette.Window, QColor(255, 255, 255, 20))
        self.setPalette(palette)
        self.setAutoFillBackground(True)  # 需要将自动填充背景设置为True
        self.label_title = {'掘进编号': QLabel('掘进编号:'), '当前里程': QLabel('当前里程:'), '开始时间': QLabel('开始时间:'),
                            '结束时间': QLabel('结束时间:'), '掘进时间': QLabel('掘进时间:'), '掘进长度': QLabel('掘进长度:'),
                            '刀盘转速': QLabel('刀盘转速:'), '掘进速度': QLabel('掘进速度:'),
                            '刀盘推力': QLabel('刀盘推力:'), '刀盘扭矩': QLabel('刀盘扭矩:')}
        self.label_var = {'掘进编号': QLabel('--'), '当前里程': QLabel('--'), '开始时间': QLabel('--'),
                          '结束时间': QLabel('--'), '掘进时间': QLabel('--'), '掘进长度': QLabel('--'),
                          '刀盘转速': QLabel('--'), '掘进速度': QLabel('--'),
                          '刀盘推力': QLabel('--'), '刀盘扭矩': QLabel('--')}
        self.layout = QGridLayout()
        self.set_invariant()
        self.setLayout(self.layout)  # 设置 QWidget 的布局管理器

    def set_invariant(self):
        for index, col in enumerate([0, 20, 40, 60, 80]):
            for name, row in zip(list(self.label_title.values())[2 * index: 2 * (index + 1)], [0, 50]):
                self.layout.addWidget(name, col, row, 20, 10)
                name.setStyleSheet("color: white; font-size: 17px; background-color: rgba(0,0,0,0)")
                name.setAlignment(Qt.AlignCenter)
                name.setFont(QFont('黑体', 13))
            for name, row in zip(list(self.label_var.values())[2 * index: 2 * (index + 1)], [10, 60]):
                self.layout.addWidget(name, col, row, 20, 40)
                name.setStyleSheet("color: white; font-size: 17px; background-color: rgba(0,0,0,0)")
                name.setAlignment(Qt.AlignCenter)
                name.setFont(QFont('黑体', 13))

    def set_changeable(self, cycles):
        total = cycles['data'].shape[0]
        Time_start = cycles['data'].loc[0, '运行时间']  # 获取每个掘进段的时间记录
        Time_start = pd.to_datetime(Time_start, format='%Y-%m-%d %H:%M:%S')  # 对时间类型记录进行转换
        Time_end = cycles['data'].loc[total - 1, '运行时间']  # 获取每个掘进段的时间记录
        Time_end = pd.to_datetime(Time_end, format='%Y-%m-%d %H:%M:%S')  # 对时间类型记录进行转换
        Length = max(cycles['data'].loc[:, '推进位移']) - min(cycles['data'].loc[:, '推进位移'])
        self.label_var['掘进编号'].setText('%00005d' % cycles['num'])
        self.label_var['当前里程'].setText('%.2f m' % cycles['data'].loc[0, '里程'])
        self.label_var['开始时间'].setText('%s' % Time_start)
        self.label_var['结束时间'].setText('%s' % Time_end)
        self.label_var['掘进时间'].setText('%d s' % (Time_end - Time_start).seconds)
        self.label_var['掘进长度'].setText('%d mm' % int(Length))
        self.label_var['刀盘转速'].setText('%.2f r/min' % cycles['data'].loc[:, '刀盘转速'].mean())
        self.label_var['掘进速度'].setText('%.2f mm/min' % cycles['data'].loc[:, '推进速度'].mean())
        self.label_var['刀盘推力'].setText('%.2f kN' % cycles['data'].loc[:, '刀盘推力'].mean())
        self.label_var['刀盘扭矩'].setText('%.2f kN.m' % cycles['data'].loc[:, '刀盘扭矩'].mean())


class History_info(QWidget):
    def __init__(self):
        plt.rcParams["font.sans-serif"] = ["Simhei"]  # 设置默认字体
        plt.rcParams["axes.unicode_minus"] = False  # 坐标轴正确显示正负号
        plt.style.use('ggplot')  # 设置ggplot样式
        plt.rcParams["axes.grid"] = False
        super(History_info, self).__init__()
        self.setFixedSize(1750, 800)  # 设置窗口大小为 400x300
        self.move(100, 100)
        self.history = []
        self.values_last = {'当前围岩类型': '--', 'Ⅱ类Ⅲ类围岩概率': '--', 'Ⅳ类Ⅴ类围岩概率': '--',
                            '建议支护方式': '--', '风险状态': '--', '推荐刀盘转速': '--', '推荐推进速度': '--',
                            'TPI-平均': 0, 'FPIa-平均': 0, 'FPIb-平均': 0}
        base_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        self.save_csv = os.path.join(base_path, 'SaveData')
        if not os.path.exists(self.save_csv):
            os.mkdir(self.save_csv)  # 创建相关文件夹
        # self.history_window.setWindowFlags(Qt.CustomizeWindowHint)  # 去掉窗口标题栏
        self.setWindowTitle("历史信息")
        self.palette = QPalette()
        brush = QBrush(QPixmap(os.path.join(base_path, 'Resources\\BGImages.png')))
        self.palette.setBrush(QPalette.Background, brush)
        self.setPalette(self.palette)
        self.setAutoFillBackground(True)  # 需要将自动填充背景设置为True
        self.page = 0
        Width, Height = (self.size().width() - 38) / 6, (self.size().height() - 35) / 16
        self.Module2 = Module2(width=int(Width*2), height=int(Height*6))
        self.Module3 = Module3(width=int(Width*2), height=int(Height*6))
        self.Module10 = Module10(width=int(Width*2), height=int(Height*6))
        # 添加画布四
        self.scatter4 = []
        self.fig4 = Figure(figsize=(9, 4), dpi=100, facecolor=(1.0, 1.0, 1.0, 0.1))
        self.ax4 = self.fig4.add_subplot(111)
        self.X_R4 = self.ax4.twinx()
        self.SubPlot_4(Axes=self.ax4, Type='Invariant')
        self.canvas4 = FigureCanvas(self.fig4)
        self.canvas4.setStyleSheet("background-color: transparent;")
        self.canvas4.setFixedSize(int(Width*3), int(Height*9))
        # 添加画布五
        self.scatter5 = []
        self.fig5 = Figure(figsize=(9, 4), dpi=100, facecolor=(1.0, 1.0, 1.0, 0.1))
        self.ax5 = self.fig5.add_subplot(111)
        self.X_R5 = self.ax5.twinx()
        self.SubPlot_5(Axes=self.ax5, Type='Invariant')
        self.canvas5 = FigureCanvas(self.fig5)
        self.canvas5.setStyleSheet("background-color: transparent;")
        self.canvas5.setFixedSize(int(Width*3), int(Height*9))
        # 添加画布六
        self.Widget6 = QWidget()
        palette = QPalette()
        palette.setColor(QPalette.Window, QColor(255, 255, 255, 0))
        self.Widget6.setPalette(palette)
        self.Widget6.setAutoFillBackground(True)  # 需要将自动填充背景设置为True
        self.layout6 = QGridLayout()
        self.Button = {'上一页': QPushButton("<<上一页"), '页面导航': QLabel('第-页/共-页'), '下一页': QPushButton("下一页>>")}
        self.layout6.addWidget(self.Button['上一页'], 0, 0, 1, 1)
        self.Button['上一页'].setFixedSize(80, 30)
        self.Button['上一页'].clicked.connect(lambda: self.update_figure(1))
        self.layout6.addWidget(self.Button['页面导航'], 0, 1, 1, 1)
        self.Button['页面导航'].setFixedSize(160, 30)
        self.Button['页面导航'].setFont(QFont('黑体', 13))
        self.Button['页面导航'].setStyleSheet("color: white")
        self.Button['页面导航'].setAlignment(Qt.AlignCenter)
        self.layout6.addWidget(self.Button['下一页'], 0, 2, 1, 1)
        self.Button['下一页'].setFixedSize(80, 30)
        self.Button['下一页'].clicked.connect(lambda: self.update_figure(-1))
        self.Widget6.setLayout(self.layout6)
        self.Widget6.setFixedSize(int(Width*2), int(Height*1))
        # 添加画布七
        self.Widget7 = QWidget()
        palette7 = QPalette()
        palette7.setColor(QPalette.Window, QColor(255, 255, 255, 0))
        self.Widget7.setPalette(palette7)
        self.Widget7.setAutoFillBackground(True)  # 需要将自动填充背景设置为True
        self.layout7 = QGridLayout()
        Button7 = QPushButton("循环段数据")
        self.layout7.addWidget(Button7, 0, 0, 1, 1)
        Button7.setFixedSize(90, 30)
        Button7.clicked.connect(lambda: os.startfile(self.save_csv))
        self.Widget7.setLayout(self.layout7)
        self.Widget7.setFixedSize(int(Width*0.5), int(Height*1))
        self.layout = QGridLayout()
        self.layout.addWidget(self.Module2, 0, 0, 6, 12)
        self.layout.addWidget(self.Module3, 0, 12, 6, 12)
        self.layout.addWidget(self.Module10, 0, 24, 6, 12)
        self.layout.addWidget(self.canvas4, 6, 0, 8, 18)
        self.layout.addWidget(self.canvas5, 6, 18, 8, 18)
        self.layout.addWidget(self.Widget6, 14, 12, 1, 12)
        self.layout.addWidget(self.Widget7, 14, 0, 1, 12)
        self.setLayout(self.layout)
        self.update_figure(0)

    def update_figure(self, num):
        if 1 < self.page < len(self.history):
            self.page = self.page + num
        elif self.page == 1 and num > 0 and len(self.history) > 1:
            self.page = self.page + num
        elif self.page == len(self.history) and num < 0 and len(self.history) > 1:
            self.page = self.page + num
        if self.page == 0 and len(self.history) > 0:
            self.page += 1
        self.Button['页面导航'].setText('第%d页/共%d页' % (self.page, len(self.history)))
        if 0 < self.page <= len(self.history):
            # noinspection PyBroadException
            try:
                self.Module2.set_changeable(real_values=self.history[self.page - 1], last_values=self.values_last)
                self.Module3.set_changeable(real_values=self.history[self.page - 1], last_values=self.values_last)
                self.Module10.set_changeable(cycles=self.history[self.page - 1])
                self.SubPlot_4(Axes=self.ax4, Type='Changeable', Num=-self.page)
                self.SubPlot_5(Axes=self.ax5, Type='Changeable', Num=-self.page)
            except Exception:
                QMessageBox.critical(self, 'Error', traceback.format_exc())

    def SubPlot_4(self, Axes, Type, Num=0):
        if Type == 'Invariant':
            Axes.patch.set_alpha(0.0)
            x_p = np.array([i for i in range(25)])  # '刀盘转速设定'
            y_T = np.array([0 for _ in range(25)])  # '推进速度'
            y_F = np.array([0 for _ in range(25)])  # '推进速度设定'
            Axes.xaxis.set_tick_params(colors='#33CCFF')
            Axes.set_xlabel('贯入度p(mm/r)', color='#33CCFF', fontsize=12)
            Axes.set_xlim(xmin=0, xmax=25)
            self.scatter4.append(Axes.scatter(x_p, y_T, label="刀盘扭矩T(kN.m)", color='#FF9B00', marker='.', s=35))
            Axes.set_ylim(ymin=0, ymax=5000)
            Axes.legend(bbox_to_anchor=(0.22, 1.15), loc=9, ncol=2, frameon=False, fontsize=10, labelcolor='white')
            Axes.yaxis.set_tick_params(colors='#FF9B00')
            Axes.set_ylabel('刀盘扭矩', color='#FF9B00', fontsize=14)
            self.scatter4.append(self.X_R4.scatter(x_p, y_F, label="刀盘推力(kN)", color='#FF0000', marker='.', s=35))
            self.X_R4.set_ylim(ymin=0, ymax=30000)
            self.X_R4.legend(bbox_to_anchor=(0.78, 1.15), loc=9, ncol=2, frameon=False, fontsize=10, labelcolor='white')
            self.X_R4.yaxis.set_tick_params(colors='#FF0000')
            self.X_R4.set_ylabel('刀盘推力', color='#FF0000', fontsize=14)
            Axes.axhline(y=4000, c="#FF9B00", ls="-.", alpha=0.7)
            Axes.axvline(x=20, c="#33CCFF", ls="-.", alpha=0.7)
            Axes.fill([0, 0, 20, 20], [0, 4000, 4000, 0], c="#CCFFC9", alpha=0.1)
            self.scatter4.append(Axes.plot(np.array([0, 25]), np.array([0, 0]), c="#FF9B00", ls="--"))
            self.scatter4.append(self.X_R4.plot(np.array([0, 25]), np.array([0, 0]), c="#FF0000", ls="--"))
        if Type == 'Changeable':
            if self.scatter4 is not None:
                for num, k in enumerate(self.scatter4):
                    k.remove() if num < len(self.scatter4) - 2 else k[0].remove()
            x_p = self.history[Num]['data'].loc[:, '刀盘贯入度']  # '刀盘转速设定'
            y_T = self.history[Num]['data'].loc[:, '刀盘扭矩']  # '推进速度'
            y_F = self.history[Num]['data'].loc[:, '刀盘推力']  # '推进速度设定')
            T_K_B = y_T.mean() / x_p.mean()
            T_x, T_y = np.array([0, 25]), (T_K_B * np.array([0, 25]))
            F_K_B = np.polyfit(x_p.astype(float), y_F.astype(float), 1)
            F_x, F_y = np.array([0, 25]), (F_K_B[0] * np.array([0, 25]) + F_K_B[1])
            self.scatter4 = [Axes.scatter(x_p, y_T, label="刀盘扭矩T(kN.m)", color='#FF9B00', marker='.', s=35),
                             self.X_R4.scatter(x_p, y_F, label="刀盘推力(kN)", color='#FF0000', marker='.', s=35),
                             Axes.plot(T_x, T_y, c="#FF9B00", ls="--"),
                             self.X_R4.plot(F_x, F_y, c="#FF0000", ls="--")]
            self.canvas4.draw()

    def SubPlot_5(self, Axes, Type, Num=0):
        if Type == 'Invariant':
            Axes.patch.set_alpha(0.0)
            x = [i for i in range(100)]  # 'Time'
            y_n = np.array([0 for _ in range(100)])  # '刀盘转速'
            y_v = np.array([0 for _ in range(100)])  # '刀盘转速设定'
            y_T = np.array([0 for _ in range(100)])  # '推进速度'
            y_F = np.array([0 for _ in range(100)])  # '推进速度设定'
            self.scatter5.append(Axes.scatter(x, y_n * 15, label="刀盘转速n*10(r/min)", color='white', marker='.', s=35))
            self.scatter5.append(Axes.scatter(x, y_v, label="推进速度v(mm/min)", color='#00FF00', marker='.', s=35))
            Axes.set_ylim(ymin=-5, ymax=120)
            Axes.legend(bbox_to_anchor=(0.22, 1.15), loc=9, ncol=2, frameon=False, fontsize=10, labelcolor='white',
                        markerscale=1.5)
            Axes.yaxis.set_tick_params(colors='white')
            Axes.xaxis.set_tick_params(colors='white')
            Axes.set_ylabel('刀盘转速，推进速度', color='white', fontsize=14)
            Axes.set_xlabel('时  间 (s)', color='white', fontsize=12)
            self.scatter5.append(
                self.X_R5.scatter(x, y_T / 3, label="刀盘扭矩T/3(kN.m)", color='#FF9B00', marker='.', s=35))
            self.scatter5.append(self.X_R5.scatter(x, y_F / 25, label="刀盘推力F/25(kN)", color='red', marker='.', s=35))
            self.X_R5.set_ylim(ymin=-100, ymax=2500)
            self.X_R5.legend(bbox_to_anchor=(0.78, 1.15), loc=9, ncol=2, frameon=False, fontsize=10, labelcolor='white',
                             markerscale=1.5)
            self.X_R5.yaxis.set_tick_params(colors='white')
            self.X_R5.set_ylabel('刀盘扭矩，刀盘推力', color='white', fontsize=14)
        if Type == 'Changeable':
            if self.scatter5 is not None:
                [k.remove() for k in self.scatter5]
            x = [i for i in range(self.history[Num]['data'].shape[0])]  # 'Time'
            y_n = self.history[Num]['data'].loc[:, '刀盘转速']  # '刀盘转速'
            y_v = self.history[Num]['data'].loc[:, '推进速度']  # '刀盘转速设定'
            y_T = self.history[Num]['data'].loc[:, '刀盘扭矩']  # '推进速度'
            y_F = self.history[Num]['data'].loc[:, '刀盘推力']  # '推进速度设定'
            Axes.set_xlim(xmin=-50, xmax=self.history[Num]['data'].shape[0] + 50)
            self.scatter5 = [Axes.scatter(x, y_n * 15, label="刀盘转速n*10(r/min)", color='white', marker='.', s=35),
                             Axes.scatter(x, y_v, label="推进速度v(mm/min)", color='#00FF00', marker='.', s=35),
                             self.X_R5.scatter(x, y_T / 3, label="刀盘扭矩T/3(kN.m)", color='#FF9B00', marker='.', s=35),
                             self.X_R5.scatter(x, y_F / 25, label="刀盘推力F/25(kN)", color='red', marker='.', s=35)]
            self.canvas5.draw()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    demo = Window()
    desktop = QDesktopWidget()
    screen_rect = desktop.screenGeometry()
    demo.show()
    sys.exit(app.exec_())
