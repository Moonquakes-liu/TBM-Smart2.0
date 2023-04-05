#!/usr/bin/env python
# -*- coding: utf-8 -*-
# ************************************************************************
# * Software:  MyMainWindow  for  Python                                 *
# * Version:  1.0.0                                                      *
# * Date:  2023-03-30 00:00:00                                           *
# * Last  update: 2023-03-30 00:00:00                                    *
# * License:  LGPL v1.0                                                  *
# * Maintain  address:  https://pan.baidu.com/s/1SKx3np-9jii3Zgf1joAO4A  *
# * Maintain  code:  STBM                                                *
# ************************************************************************

import random
import pandas as pd
from PyQt5 import QtCore
from PyQt5.QtChart import QChartView, QChart, QScatterSeries, QDateTimeAxis
from PyQt5.QtChart import QValueAxis, QLineSeries, QLegend, QAreaSeries
from PyQt5.QtGui import QBrush, QColor, QPainter, QFont, QPen
from PyQt5.QtWidgets import QMainWindow, QWidget, QGridLayout, QLabel, QScrollArea
from PyQt5.QtCore import QTimer, Qt, QDateTime, QPointF, QPoint
from matplotlib import pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import numpy as np

plt.rcParams["font.sans-serif"] = ["Simhei"]  # 设置默认字体
plt.rcParams["axes.unicode_minus"] = False  # 坐标轴正确显示正负号
plt.style.use('ggplot')  # 设置ggplot样式


class MyMainWindow(QMainWindow):
    def __init__(self, time_interval=1):
        super().__init__()
        self.values = {'里程': 0, '运行时间': '2008-01-01 12:00:00', '刀盘转速-当前': 0, '刀盘转速设定值-当前': 0,
                       '推进速度-当前': 0, '推进速度设定值-当前': 0, '刀盘扭矩-当前': 0, '刀盘推力-当前': 0, '贯入度-当前': 0,
                       '刀盘转速-之前': 0, '推进速度-之前': 0, '刀盘扭矩-之前': 0, '刀盘推力-之前': 0, '施工状态': '停机中',
                       '当前围岩类型': '待生成', 'Ⅱ类Ⅲ类围岩概率': 0, 'Ⅳ类Ⅴ类围岩概率': 0, '建议支护方式': '无',
                       '风险状态': '安全掘进', '推荐刀盘转速': 0, '推荐推进速度': 0, '刀盘扭矩预测值': 0, '刀盘推力预测值': 0,
                       '滚刀磨损速率': '低'}
        # 添加画布一
        self.fig1 = Figure(figsize=(9, 3), dpi=100, facecolor='ghostwhite')
        self.fig1.subplots_adjust(top=1, bottom=0, right=1, left=0, hspace=0, wspace=0)
        self.ax1 = self.fig1.add_axes([0, 0, 1, 1])
        self.SubPlot_1(Axes=self.ax1, Type='Invariant')
        self.canvas1 = FigureCanvas(self.fig1)
        self.axes1 = []
        # 添加画布二
        self.fig2 = Figure(figsize=(9, 3), dpi=100, facecolor='ghostwhite')
        self.fig2.subplots_adjust(top=1, bottom=0, right=1, left=0, hspace=0, wspace=0)
        self.ax2 = self.fig2.add_axes([0, 0, 1, 1])
        self.SubPlot_2(Axes=self.ax2, Type='Invariant')
        self.canvas2 = FigureCanvas(self.fig2)
        self.axes2 = []
        # 添加画布三
        self.chart3 = QChart()
        self.chart3.setBackgroundBrush(QBrush(QColor('ghostwhite')))
        self.series3 = {'转速(r/min)*10   ': QScatterSeries(), '速度(mm/min)   ': QScatterSeries(),
                        '扭矩(kN.m)   ': QScatterSeries(), '推力(kN)/10   ': QScatterSeries()}
        self.axisX_B = None
        self.SubPlot_3(Chart=self.chart3, Type='Invariant')
        self.chartView3 = QChartView(self.chart3)
        self.chartView3.setStyleSheet('background-color: ghostwhite;')
        self.chartView3.resize(700, 400)
        self.chartView3.setRenderHint(QPainter.Antialiasing)
        self.setCentralWidget(self.chartView3)
        # 添加画布四
        self.chart4 = QChart()
        self.chart4.setBackgroundBrush(QBrush(QColor('ghostwhite')))
        self.series4 = {'TPI': QScatterSeries(), 'FPI': QScatterSeries(), '拟合FPI': QLineSeries(),
                        '拟合TPI': QLineSeries()}
        self.SubPlot_4(Chart=self.chart4, Type='Invariant')
        self.chartView4 = QChartView(self.chart4)
        self.chartView4.setStyleSheet('background-color: ghostwhite;')
        self.chartView4.resize(700, 400)
        self.chartView4.setRenderHint(QPainter.Antialiasing)
        self.Fit4 = [[[], []], [[], []]]
        # 添加画布五
        self.fig5 = Figure(figsize=(12, 3), dpi=100, facecolor='ghostwhite')
        self.fig5.subplots_adjust(top=1, bottom=0, right=1, left=0, hspace=0, wspace=0)
        self.ax5 = self.fig5.add_axes([0, 0, 1, 1])
        self.SubPlot_5(Axes=self.ax5, Type='Invariant')
        self.canvas5 = FigureCanvas(self.fig5)
        self.axes5 = []
        # 添加画布六
        self.fig6 = Figure(figsize=(6, 6), dpi=100, facecolor='ghostwhite')
        self.fig6.subplots_adjust(top=0.80)
        self.fig6.text(0.030, 0.910, '实时值/额定值', size=22)
        self.fig6.subplots_adjust(top=0.85)
        self.ax6 = self.fig6.add_subplot(111, polar=True, facecolor='ghostwhite', projection='polar')
        self.SubPlot_6(Axes=self.ax6, Type='Invariant')
        self.canvas6 = FigureCanvas(self.fig6)
        self.axes6 = []
        # 添加滚动字幕
        self.label = QLabel(self)
        self.label.setStyleSheet('color: blue')
        self.label.setAlignment(Qt.AlignCenter)
        self.text = "预测围岩类别：待生成     概率：待生成"
        self.label.setText(self.text)
        font = QFont('Simhei', 14)
        self.label.setFont(font)
        self.scroll_area = QScrollArea()
        self.scroll_area.setStyleSheet("background-color: ghostwhite; border: none")
        self.scroll_area.setAlignment(Qt.AlignCenter)
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setMaximumHeight(35)
        self.scroll_area.setWidget(self.label)
        # 将图形添加到主窗口
        widget = QWidget()
        layout = QGridLayout()
        layout.addWidget(self.scroll_area, 0, 0, 1, 42)
        layout.addWidget(self.canvas1, 1, 0, 7, 21)
        layout.addWidget(self.canvas2, 1, 21, 7, 21)
        layout.addWidget(self.chartView3, 8, 0, 8, 14)
        layout.addWidget(self.chartView4, 8, 14, 8, 14)
        layout.addWidget(self.canvas5, 16, 0, 6, 28)
        layout.addWidget(self.canvas6, 8, 28, 14, 14)
        widget.setLayout(layout)
        self.setCentralWidget(widget)
        # 创建一个计时器，用于实时更新图形
        self.timer = QTimer(self)
        self.timer1 = QTimer(self)
        self.timer.timeout.connect(self.update_figure)
        self.timer1.timeout.connect(self.scroll_text)
        self.timer.start(int(time_interval * 1000))
        self.timer1.start(30)  # 50ms滚动一次
        self.num = 0

    def update_figure(self):
        self.SubPlot_1(Axes=self.ax1, Type='Changeable')  # 更新第一个图形
        self.SubPlot_2(Axes=self.ax2, Type='Changeable')  # 更新第二个图形
        self.SubPlot_3(Chart=self.chart3, Type='Changeable')  # 更新第三个图形
        self.SubPlot_4(Chart=self.chart4, Type='Changeable')  # 更新第四个图形
        self.SubPlot_5(Axes=self.ax5, Type='Changeable')  # 更新第五个图形
        self.SubPlot_6(Axes=self.ax6, Type='Changeable')  # 更新第六个图形
        self.num += 1

    def scroll_text(self):
        # 每次向左移动1个像素
        current_pos = self.label.pos()
        new_pos = current_pos - QPoint(5, 0)
        self.label.move(new_pos)
        # 如果已经滚出屏幕，则重新开始滚动
        if self.label.pos().x() + self.label.width() < 0:
            self.label.setText('%d%%' % ((random.random()) * 100))
            self.label.move(QPoint(self.width(), self.label.pos().y()))
            # self.label.move(self.width(), self.label.pos().y())

    def SubPlot_1(self, Axes, Type):
        if Type == 'Invariant':
            Axes.set_xlim(xmin=0, xmax=1), Axes.set_ylim(ymin=0, ymax=1)
            Axes.grid(c='ghostwhite')
            Axes.patch.set_alpha(0.0)
            Axes.text(0.29, 0.78, '掘进过程预警', size=22, va='center', ha='center')
            Axes.text(0.175, 0.62, '围岩分类', size=15, va='center', ha='center')
            Axes.text(0.23, 0.48, 'Ⅱ类或Ⅲ类围岩概率', size=15, va='center', ha='center')
            Axes.text(0.23, 0.34, 'Ⅳ类或Ⅴ类围岩概率', size=15, va='center', ha='center')
            Axes.plot([0.10, 0.18], [0.78, 0.78], color='lightgray', lw=1)
            Axes.plot([0.40, 0.49], [0.78, 0.78], color='lightgray', lw=1)
            Axes.plot([0.10, 0.10], [0.25, 0.78], color='lightgray', lw=1)
            Axes.plot([0.49, 0.49], [0.25, 0.78], color='lightgray', lw=1)
            Axes.plot([0.10, 0.49], [0.25, 0.25], color='lightgray', lw=1)
            Axes.text(0.47, 0.13, '建议支护方式：', size=26, color='royalblue', va='center', ha='center')
            Axes.text(0.72, 0.78, '风险掘进提示', size=22, va='center', ha='center')
            Axes.text(0.75, 0.62, '安全掘进', size=15, va='center', ha='center')
            Axes.text(0.75, 0.486, '预警观察', size=15, va='center', ha='center')
            Axes.text(0.75, 0.34, '风险控制', size=15, va='center', ha='center')
            Axes.plot([0.53, 0.61], [0.78, 0.78], color='lightgray', lw=1)
            Axes.plot([0.83, 0.92], [0.78, 0.78], color='lightgray', lw=1)
            Axes.plot([0.53, 0.53], [0.25, 0.78], color='lightgray', lw=1)
            Axes.plot([0.92, 0.92], [0.25, 0.78], color='lightgray', lw=1)
            Axes.plot([0.53, 0.92], [0.25, 0.25], color='lightgray', lw=1)
        if Type == 'Changeable':
            if self.axes1 is not None:
                [k.remove() for k in self.axes1]
            Status = self.values['风险状态']
            self.axes1 = [
                Axes.text(0.41, 0.62, '%s' % self.values['当前围岩类型'], size=15, va='center', ha='center'),
                Axes.text(0.41, 0.48, '%2d%%' % self.values['Ⅱ类Ⅲ类围岩概率'], size=15, va='center', ha='center'),
                Axes.text(0.41, 0.34, '%2d%%' % self.values['Ⅳ类Ⅴ类围岩概率'], size=15, va='center', ha='center'),
                Axes.text(0.65, 0.13, '%s' % self.values['建议支护方式'], size=26, color='blue', va='center', ha='center'),
                Axes.scatter(0.65, 0.62, s=160, c='%s' % ('lime' if Status == '安全掘进' else 'g')),
                Axes.scatter(0.65, 0.48, s=160, c='%s' % ('gold' if Status == '预警观察' else 'darkorange')),
                Axes.scatter(0.65, 0.34, s=160, c='%s' % ('red' if Status == '风险控制' else 'darkred'))]
            self.canvas1.draw()

    def SubPlot_2(self, Axes, Type):
        if Type == 'Invariant':
            Axes.set_xlim(xmin=0, xmax=1), Axes.set_ylim(ymin=0, ymax=1)
            Axes.grid(c='ghostwhite')
            Axes.patch.set_alpha(0.0)
            Axes.text(0.31, 0.45, '推荐刀盘转速', size=15, va='center', ha='center')
            Axes.text(0.68, 0.45, '推荐推进速度', size=15, va='center', ha='center')
            Axes.text(0.14, 0.26, '参  数', size=12, va='center', ha='center')
            Axes.text(0.35, 0.26, '扭矩最大值(kN.m)', size=12, va='center', ha='center')
            Axes.text(0.61, 0.26, '推力最大值(kN)', size=12, va='center', ha='center')
            Axes.text(0.83, 0.26, '滚刀磨损速率', size=12, va='center', ha='center')
            Axes.text(0.14, 0.12, '预测值', size=12, va='center', ha='center')
            Axes.fill([0.07, 0.07, 0.93, 0.93], [0.20, 0.32, 0.32, 0.20], color='lavender', alpha=0.4)
        if Type == 'Changeable':
            if self.axes2 is not None:
                [k.remove() for k in self.axes2]
            color = ('g' if self.values['滚刀磨损速率'] == '低' else ('y' if self.values['滚刀磨损速率'] == '中' else 'r'))
            self.axes2 = [
                self.ax2.text(0.31, 0.64, '%2d%%' % self.values['推荐刀盘转速'], size=35, va='center', ha='center'),
                self.ax2.text(0.68, 0.64, '%2d%%' % self.values['推荐推进速度'], size=35, va='center', ha='center'),
                self.ax2.text(0.35, 0.12, '%5.2f' % self.values['刀盘扭矩预测值'], size=12, va='center', ha='center'),
                self.ax2.text(0.61, 0.12, '%5.2f' % self.values['刀盘推力预测值'], size=12, va='center', ha='center'),
                self.ax2.text(0.83, 0.12, '%s' % self.values['滚刀磨损速率'], color=color, size=12, va='center', ha='center')]
            self.canvas2.draw()

    def SubPlot_3(self, Chart, Type):
        if Type == 'Invariant':
            Chart.setMargins(QtCore.QMargins(0, 0, 0, 0))  # 调整边距
            linePen = QPen(Qt.black, 1.5)
            font = QFont()
            font.setPointSize(10)
            # 设置图例格式
            legend = Chart.legend()  # 获取 QLegend 对象
            legend.setFont(QFont("Arial", 8))  # 设置图例字体及大小
            legend.setContentsMargins(0, 0, 0, 0)  # 设置图例和边界之间的距离为0
            legend.setMarkerShape(QLegend.MarkerShapeCircle)  # 设置图例项的形状为圆形
            # 设置坐标轴
            axisX_T, self.axisX_B, axisY_L, axisY_R = QLineSeries(), QDateTimeAxis(), QValueAxis(), QValueAxis()
            self.axisX_B.setTitleText("时  间"), axisY_L.setTitleText("速度 & 转速"), axisY_R.setTitleText("推力 & 扭矩")
            self.axisX_B.setTitleFont(font), axisY_L.setTitleFont(font), axisY_R.setTitleFont(font)
            axisY_L.setRange(0, 100), axisY_R.setRange(0, 2500)
            self.axisX_B.setTickCount(6), axisY_L.setTickCount(11), axisY_R.setTickCount(11)
            self.axisX_B.setFormat("hh:mm:ss"), axisY_L.setLabelFormat("%d"), axisY_R.setLabelFormat("%d")
            self.axisX_B.setGridLineVisible(False), axisY_L.setGridLineVisible(False), axisY_R.setGridLineVisible(False)
            self.axisX_B.setLinePen(linePen), axisY_L.setLinePen(linePen), axisY_R.setLinePen(linePen)
            Chart.addAxis(axisY_L, Qt.AlignLeft), Chart.addAxis(axisY_R, Qt.AlignRight)
            Chart.addAxis(self.axisX_B, Qt.AlignBottom), Chart.addSeries(axisX_T)
            axisX_T.append(0, 100), axisX_T.append(25, 100)
            axisX_T.attachAxis(self.axisX_B), axisX_T.attachAxis(axisY_L)
            axisX_T.setPen(linePen)
            # 生成N、T、F、V数据点
            for name, axisY, color in zip(self.series3.keys(), [axisY_L, axisY_L, axisY_R, axisY_R],
                                          [Qt.black, Qt.red, Qt.blue, Qt.green]):
                Chart.addSeries(self.series3[name])
                self.series3[name].setMarkerSize(4)
                self.series3[name].setColor(color)
                self.series3[name].attachAxis(self.axisX_B), self.series3[name].attachAxis(axisY)
                self.series3[name].setName(name)
        if Type == 'Changeable':
            aaaa = str(pd.to_datetime(self.values['运行时间'], format='%Y-%m-%d %H:%M:%S'))
            max_timestamp = QDateTime.fromString(aaaa, 'yyyy-MM-dd hh:mm:ss')
            min_timestamp = max_timestamp.addSecs(-600)
            self.axisX_B.setRange(min_timestamp, max_timestamp)
            for name in self.series3.keys():
                if name == '转速(r/min)*10   ':
                    self.series3[name].append(max_timestamp.toMSecsSinceEpoch(), self.values['刀盘转速-当前'] * 12)
                if name == '速度(mm/min)   ':
                    self.series3[name].append(max_timestamp.toMSecsSinceEpoch(), self.values['推进速度-当前'])
                if name == '扭矩(kN.m)   ':
                    self.series3[name].append(max_timestamp.toMSecsSinceEpoch(), self.values['刀盘扭矩-当前'] / 2.5)
                if name == '推力(kN)/10   ':
                    self.series3[name].append(max_timestamp.toMSecsSinceEpoch(), self.values['刀盘推力-当前'] / 25)
                brush = self.series3[name].brush()
                brush.setStyle(Qt.SolidPattern)
                self.series3[name].setPen(QPen(Qt.transparent))
                self.series3[name].setBrush(brush)
                for point in self.series3[name].points():
                    if point.x() < min_timestamp.toMSecsSinceEpoch():
                        self.series3[name].remove(point)

    def SubPlot_4(self, Chart, Type):
        def set_pen(Color, line):
            pen_line = QPen(Color, 1, Qt.DotLine)
            pen_line.setDashPattern(line)
            return pen_line

        if Type == 'Invariant':
            Chart.setMargins(QtCore.QMargins(0, 0, 0, 0))  # 调整边距
            Chart.legend().setVisible(False)  # 不显示图例
            linePen4 = QPen(Qt.black, 1.5)
            font4 = QFont()
            font4.setPointSize(10)
            # 设置坐标轴
            axisX_T, axisX_B, axisY_L, axisY_R = QLineSeries(), QValueAxis(), QValueAxis(), QValueAxis()
            axisX_B.setTitleText("贯入度"), axisY_L.setTitleText("推  力"), axisY_R.setTitleText("扭  矩")
            axisX_B.setTitleFont(font4), axisY_L.setTitleFont(font4), axisY_R.setTitleFont(font4)
            axisX_B.setRange(0, 25), axisY_L.setRange(0, 25000), axisY_R.setRange(0, 5000)
            axisX_B.setTickCount(6), axisY_L.setTickCount(11), axisY_R.setTickCount(11)
            axisX_B.setLabelFormat("%d"), axisY_L.setLabelFormat("%d"), axisY_R.setLabelFormat("%d")
            axisX_B.setGridLineVisible(False), axisY_L.setGridLineVisible(False), axisY_R.setGridLineVisible(False)
            axisX_B.setLinePen(linePen4), axisY_L.setLinePen(linePen4), axisY_R.setLinePen(linePen4)
            axisY_L.setLinePenColor(QColor("blue")), axisY_R.setLinePenColor(QColor("red"))
            axisY_L.setLabelsColor(QColor("blue")), axisY_R.setLabelsColor(QColor("red"))
            axisY_L.setTitleBrush(QBrush(QColor('blue'))), axisY_R.setTitleBrush(QBrush(QColor('red')))
            Chart.addAxis(axisY_L, Qt.AlignLeft), Chart.addAxis(axisY_R, Qt.AlignRight)
            Chart.addAxis(axisX_B, Qt.AlignBottom), Chart.addSeries(axisX_T)
            axisX_T.append(0, 25000), axisX_T.append(25, 25000)
            axisX_T.attachAxis(axisX_B), axisX_T.attachAxis(axisY_L)
            axisX_T.setPen(linePen4)
            # 设置边界线
            permit_T, permit_F, permit_P = QLineSeries(), QLineSeries(), QLineSeries()
            Chart.addSeries(permit_T), Chart.addSeries(permit_F), Chart.addSeries(permit_P)
            permit_T.attachAxis(axisX_B), permit_T.attachAxis(axisY_R)
            permit_T.append(0, 4000), permit_T.append(25, 4000)
            permit_T.setPen(set_pen(Color=Qt.red, line=[7, 3, 2, 3]))
            permit_F.attachAxis(axisX_B), permit_F.attachAxis(axisY_L)
            permit_F.append(0, 23000), permit_F.append(25, 23000)
            permit_F.setPen(set_pen(Color=Qt.blue, line=[7, 3, 2, 3]))
            permit_P.attachAxis(axisX_B), permit_P.attachAxis(axisY_L)
            permit_P.append(20, 0), permit_P.append(20, 25000)
            permit_P.setPen(set_pen(Color=Qt.green, line=[7, 3, 2, 3]))
            # 设置填充区域
            areas, lower, upper = QAreaSeries(), QLineSeries(), QLineSeries()
            upper.append(QPointF(0, 0)), upper.append(QPointF(20, 0))
            lower.append(QPointF(0, 20000)), lower.append(QPointF(20, 20000))
            areas.setUpperSeries(upper), areas.setLowerSeries(lower)
            Chart.addSeries(areas), Chart.addSeries(lower), Chart.addSeries(upper)
            areas.setBrush(QBrush(QColor(204, 255, 201, 80)))
            areas.setPen(QPen(Qt.NoPen)), lower.setPen(QPen(QColor(0, 0, 0, 0))), upper.setPen(QPen(QColor(0, 0, 0, 0)))
            areas.attachAxis(axisX_B), areas.attachAxis(axisY_L)
            # 拟合TPI、FPI
            for name, axisY, color in zip(['拟合FPI', '拟合TPI'], [axisY_L, axisY_R], [Qt.blue, Qt.red]):
                Chart.addSeries(self.series4[name])
                self.series4[name].attachAxis(axisX_B), self.series4[name].attachAxis(axisY)
                self.series4[name].setPen(set_pen(Color=color, line=[5, 5]))
                self.series4[name].setName(name)
            # 生成P-F, P-T数据点
            for name, axisY, color in zip(['FPI', 'TPI'], [axisY_L, axisY_R], [Qt.blue, Qt.red]):
                Chart.addSeries(self.series4[name])
                self.series4[name].setMarkerSize(4)
                self.series4[name].setColor(color)
                self.series4[name].attachAxis(axisX_B), self.series4[name].attachAxis(axisY)
                self.series4[name].setName(name)
        if Type == 'Changeable':
            if self.values['施工状态'] == '正在掘进':
                for name in ['FPI', 'TPI']:
                    if name == 'TPI':
                        self.series4[name].append(self.values['贯入度-当前'], self.values['刀盘扭矩-当前'])
                    if name == 'FPI':
                        self.series4[name].append(self.values['贯入度-当前'], self.values['刀盘推力-当前'])
                    brush = self.series4[name].brush()
                    brush.setStyle(Qt.SolidPattern)
                    self.series4[name].setPen(QPen(Qt.transparent))
                    self.series4[name].setBrush(brush)
            else:
                self.series4['FPI'].clear(), self.series4['TPI'].clear()
                self.series4['拟合FPI'].clear(), self.series4['拟合TPI'].clear()
            self.Fit4[0][0].append(self.values['贯入度-当前']), self.Fit4[0][1].append(self.values['刀盘扭矩-当前'])
            self.Fit4[1][0].append(self.values['贯入度-当前']), self.Fit4[1][1].append(self.values['刀盘推力-当前'])
            if len(self.Fit4[1][0]) % 30 == 0:
                if self.values['施工状态'] == '正在掘进':
                    for col, name in enumerate(['拟合TPI', '拟合FPI']):
                        if max(self.Fit4[col][0]) != 0 and max(self.Fit4[col][1]) != 0:
                            K_B = np.polyfit(self.Fit4[1][0], self.Fit4[1][1], 1)
                            X, Y = np.array([0, 25]), (K_B[0] * np.array([0, 25]) + K_B[1])
                            if name == '拟合TPI':
                                if max(self.Fit4[0][0]) != 0 and max(self.Fit4[0][1]) != 0:
                                    tar_X, tar_Y = np.array(self.Fit4[0][0]), np.array(self.Fit4[0][1])
                                    K = np.linalg.lstsq(tar_X.reshape(-1, 1), tar_Y, rcond=None)[0][0]
                                    X, Y = np.array([0, 25]), (K * np.array([0, 25]))
                            new_line = [QPointF(X[i], Y[i]) for i in range(len(X))]
                            self.series4[name].replace(new_line)
                else:
                    self.Fit4[0][0].clear(), self.Fit4[0][1].clear(), self.Fit4[1][0].clear(), self.Fit4[1][1].clear()

    def SubPlot_5(self, Axes, Type):
        if Type == 'Invariant':
            Axes.set_xlim(xmin=0, xmax=1), Axes.set_ylim(ymin=0, ymax=1)
            Axes.grid(c='ghostwhite')
            Axes.patch.set_alpha(0.0)
            Axes.text(0.05, 0.62, '刀盘转速n(Rev/min)', size=12, va='center', ha='left')
            Axes.text(0.05, 0.46, '推进速度(mm/min)', size=12, va='center', ha='left')
            Axes.text(0.05, 0.30, '刀盘扭矩T(kN.m)', size=12, va='center', ha='left')
            Axes.text(0.05, 0.14, '刀盘推力F(kN)', size=12, va='center', ha='left')
            Axes.text(0.25, 0.78, '当前值', size=12, va='center', ha='center')
            Axes.text(0.40, 0.78, '前一段平均值', size=12, va='center', ha='center')
            Axes.text(0.75, 0.78, '建议', size=12, va='center', ha='center')
            Axes.text(0.05, 0.925, '桩号：', size=12, va='center', ha='center')
            Axes.text(0.25, 0.925, '日期：', size=12, va='center', ha='center')
            Axes.text(0.50, 0.925, '时间：', size=12, va='center', ha='center')
            Axes.text(0.75, 0.925, '工作状态：', size=12, va='center', ha='center')
            Axes.fill([0, 0, 10, 10], [0.06, 0.22, 0.22, 0.06], color='lavender', alpha=0.4)
            Axes.fill([0, 0, 10, 10], [0.38, 0.54, 0.54, 0.38], color='lavender', alpha=0.4)
            Axes.fill([0, 0, 10, 10], [0.70, 0.86, 0.86, 0.70], color='lavender', alpha=0.4)
        if Type == 'Changeable':
            if self.axes5 is not None:
                [k.remove() for k in self.axes5]
            color = ('g' if self.values['施工状态'] == '正在掘进' else ('r' if self.values['施工状态'] == '停机中' else 'y'))
            Time = pd.to_datetime(self.values['运行时间'], format='%Y-%m-%d %H:%M:%S')  # 对时间类型记录进行转换
            year, mon, d, h, m, s = Time.year, Time.month, Time.day, Time.hour, Time.minute, Time.second
            self.axes5 = [
                Axes.text(0.11, 0.925, '%.2f m' % self.values['里程'], size=12, va='center', ha='center'),
                Axes.text(0.31, 0.925, '%4d-%02d-%02d' % (year, mon, d), size=12, va='center', ha='center'),
                Axes.text(0.55, 0.925, '%02d:%02d:%02d' % (h, m, s), size=12, va='center', ha='center'),
                Axes.text(0.79, 0.925, '%s' % self.values['施工状态'], color='%s' % color, size=12, va='center', ha='left'),
                Axes.text(0.25, 0.62, '%.2f' % self.values['刀盘转速-当前'], size=12, va='center', ha='center'),
                Axes.text(0.25, 0.46, '%.2f' % self.values['推进速度-当前'], size=12, va='center', ha='center'),
                Axes.text(0.25, 0.30, '%.2f' % self.values['刀盘扭矩-当前'], size=12, va='center', ha='center'),
                Axes.text(0.25, 0.14, '%.2f' % self.values['刀盘推力-当前'], size=12, va='center', ha='center'),
                Axes.text(0.40, 0.62, '%.2f' % self.values['刀盘转速-之前'], size=12, va='center', ha='center'),
                Axes.text(0.40, 0.46, '%.2f' % self.values['推进速度-之前'], size=12, va='center', ha='center'),
                Axes.text(0.40, 0.30, '%.2f' % self.values['刀盘扭矩-之前'], size=12, va='center', ha='center'),
                Axes.text(0.40, 0.14, '%.2f' % self.values['刀盘推力-之前'], size=12, va='center', ha='center'),
                Axes.text(0.53, 0.62, '建议1......', size=12, va='center', ha='left'),
                Axes.text(0.53, 0.46, '建议2......', size=12, va='center', ha='left'),
                Axes.text(0.53, 0.30, '建议3......', size=12, va='center', ha='left'),
                Axes.text(0.53, 0.14, '建议4......', size=12, va='center', ha='left')]
            self.canvas5.draw()

    def SubPlot_6(self, Axes, Type):
        angles = np.linspace(0, 2 * np.pi, 5, endpoint=False)  # 将极坐标根据数据长度进行等分
        angles = np.concatenate((angles, [angles[0]]))
        if Type == 'Invariant':
            Axes.text(x=0.12, y=150, s='扭矩', size=20)
            Axes.text(x=1.32, y=175, s='推力', size=20)
            Axes.text(x=5.02, y=145, s='速度', size=20)
            Axes.text(x=2.32, y=190, s='贯入度', size=20)
            Axes.text(x=3.71, y=157, s='转速', size=20)
            R = np.arange(0, 1.01, 0.01)
            theta = 2 * np.pi * R
            Value = [{'lw': 1, 'mark': (0, (6, 2)), 'color': 'k'},
                     {'lw': 1, 'mark': (0, (6, 2)), 'color': 'k'},
                     {'lw': 1, 'mark': (0, (6, 2)), 'color': 'k'},
                     {'lw': 2, 'mark': '-', 'color': 'r'},
                     {'lw': 1, 'mark': (0, (6, 2)), 'color': 'k'},
                     {'lw': 2, 'mark': '-', 'color': 'k'}]
            for i, r in zip(range(8), range(40, 160, 20)):
                rou = [r for _ in range(0, len(R))]
                Axes.plot(theta, rou, lw=Value[i]['lw'], color=Value[i]['color'], linestyle=Value[i]['mark'])
            for j in range(5):
                Axes.plot([angles[j], angles[j]], [0, 140], lw=1.3, color='black')  # 绘制角度轴
            Axes.set_theta_zero_location('N')
            Axes.set_rlim(0, 141)
            Axes.set_rlabel_position(False)
            Axes.set_thetagrids(angles, visible=False)  # 关闭默认角度值显示
            Axes.set_rgrids([0, 20, 40, 60, 80, 100, 120, 140], visible=False)  # 关闭默认圈内数值显示
        if Type == 'Changeable':
            if self.axes6 is not None:
                [k[0].remove() for k in self.axes6]
            results = {"扭矩": self.values['刀盘扭矩-当前'] / 20, "推力": self.values['刀盘推力-当前'] / 120,
                       "贯入度": self.values['贯入度-当前'] * 5, "转速": self.values['刀盘转速-当前'] * 20,
                       "速度": self.values['推进速度-当前']}
            score = [v for v in results.values()]
            score_Harry = np.concatenate((score, [score[0]]))
            self.axes6 = [Axes.plot(angles, score_Harry, color='b'),
                          Axes.fill(angles, score_Harry, color='b', alpha=0.4)]
            self.canvas6.draw()
