# -*- coding: utf-8 -*-
"""
@File    : call_FCCU_Monitor.py
@Author  : MingyuLiang
@Time    : 2021/01/18 15:21

本文件用于实现JJSH_Form_FCCU_Monitor界面的功能，使用方法参见__main__中的调用方式
"""
from PyQt5 import QtGui, QtWidgets, QtCore
from PyQt5.QtWidgets import (QMainWindow, QApplication, QWidget, QGridLayout, QPushButton, QDialog,
                             QFrame, QLabel, QToolButton, QFileDialog,
                             QDesktopWidget, QDateTimeEdit)
from PyQt5.QtGui import QCursor, QIcon
from PyQt5.QtCore import Qt, QDateTime
import sys
import numpy as np
import pandas as pd
import pyqtgraph as pg
from pyqtgraph import PlotWidget
import OpenOPC
import pywintypes

from JJSH_Form_FCCU_Monitor import Ui_JJSH_Form_FCCU_Monitor
import functools


class JJSH_Form_FCCU_Monitor(QWidget, Ui_JJSH_Form_FCCU_Monitor):
    def __init__(self):
        super(JJSH_Form_FCCU_Monitor, self).__init__()
        self.setupUi(self)

        # 启动子主界面自己的定时器，并记录设计时的界面尺寸
        self.FCCU_timer = QtCore.QTimer()
        self.Dic_init_tagPosition = {}
        self.init_frame_FCCU_picture_width = self.frame_FCCU_picture.width()
        self.init_frame_FCCU_picture_height = self.frame_FCCU_picture.height()

        # 初始化子界面的按钮
        self.init_btn_connect()

        # 初始化子界面中tag标签的数据
        self.init_tag()

    def init_btn_connect(self):
        for name, _ in vars(self).items():
            if 'Button' in name:
                eval('self.' + name).clicked.connect(functools.partial(self.btn_clicked_func, eval('self.' + name)))

    def btn_clicked_func(self, btn):
        if btn.objectName() == 'pushButton_FCCU_ctrl_on':
            self.pushButton_FCCU_ctrl_on.setEnabled(False)
            self.pushButton_FCCU_ctrl_off.setEnabled(True)
            self.FCCU_timer.start(1000)
            self.FCCU_timer.timeout.connect(self.FCCU_update_data)

        elif btn.objectName() == 'pushButton_FCCU_ctrl_off':
            self.pushButton_FCCU_ctrl_on.setEnabled(True)
            self.pushButton_FCCU_ctrl_off.setEnabled(False)
            self.FCCU_timer.stop()
            self.label_N100_time.setText('')
            self.label_N100_time_2.setText('')
            self.label_N100_time_3.setText('')
            self.label_N100_value.setText('')
            self.label_N100_value_2.setText('')
            self.label_N100_value_3.setText('')
            #self.textBrowser_Suggest.setText('')
            #self.textBrowser_warning.setText('')

    def FCCU_update_data(self):
        for name, _ in vars(self).items():
            if 'ton_tag_' in name:
                # temp_data = self.opc.read('Distillation.'+item_tag_name)[0] #启动OPC时运行这个
                temp_data = round(np.random.normal(), 2)
                eval('self.' + name).setText(str(temp_data))

        lims_data = pd.read_csv('./data/data_FCCU.csv', header=None)
        condition_flag = pd.read_csv('./data/data_condition.csv', header=None)
        self.label_N100_time.setText(lims_data[0].values[0])
        self.label_N100_time_2.setText(lims_data[0].values[0])
        self.label_N100_time_3.setText(lims_data[0].values[0])
        self.label_N100_value.setText(str(lims_data[1].values[0]))
        self.label_N100_value_2.setText(str(lims_data[1].values[0]))
        self.label_N100_value_3.setText(str(lims_data[1].values[0]))

        #words_suggestion = '当前塔顶温度为%d，建议调整为%d\n当前重沸炉温度为%d，建议调整为%d' % (178, 180, 230, 229)
        #words_warning = '运行正常'
        #self.textBrowser_Suggest.setText(words_suggestion)
        #self.textBrowser_warning.setText(words_warning)

    def init_tag(self):
        for name, _ in vars(self).items():
            if '_tag_' in name:
                eval('self.' + name).setProperty('level', 'tag')
                if 'frame' in name:
                    self.Dic_init_tagPosition[name] = eval('self.' + name).geometry()
                    # print(self.Dic_init_tagPosition[name.split('tag_')[1]].x())
                if 'label' in name:
                    eval('self.' + name).setText(name.split('tag_')[1])
                if 'ton' in name:
                    eval('self.' + name).setText('0')

    def get_frame_FCCU_picture_size(self):
        self.init_frame_FCCU_picture_width = self.frame_FCCU_picture.width()
        self.init_frame_FCCU_picture_height = self.frame_FCCU_picture.height()

        # 窗口tag自适应调整函数
    def adjust_tag_position(self):
        now_frame_FCCU_picture_width = self.frame_FCCU_picture.width()
        now_frame_FCCU_picture_height = self.frame_FCCU_picture.height()
        for key_name in self.Dic_init_tagPosition.keys():
            x_now = (now_frame_FCCU_picture_width / self.init_frame_FCCU_picture_width) \
                    * self.Dic_init_tagPosition[key_name].x()
            y_now = (now_frame_FCCU_picture_height / self.init_frame_FCCU_picture_height) \
                    * self.Dic_init_tagPosition[key_name].y()
            self.Dic_init_tagPosition[key_name] = QtCore.QRect(x_now,
                                                               y_now,
                                                               now_frame_FCCU_picture_width,
                                                               now_frame_FCCU_picture_height)
    # 事件函数
    def resizeEvent(self, event):

        now_width = self.frame_FCCU_picture.width()
        now_height = self.frame_FCCU_picture.height()

        move_width = now_width / self.init_frame_FCCU_picture_width
        move_height = now_height / self.init_frame_FCCU_picture_height

        for name in self.Dic_init_tagPosition.keys():
            new_position_x = round(move_width * self.Dic_init_tagPosition[name].x())
            new_position_y = round(move_height * self.Dic_init_tagPosition[name].y())
            eval('self.' + name).move(new_position_x, new_position_y)

        self.update()


if __name__ == '__main__':
    with open('JJSH_style.qss', encoding='utf-8') as f:
        qss = f.read()

    pywintypes.datetime = pywintypes.TimeType
    app = QApplication(sys.argv)
    ui = JJSH_Form_FCCU_Monitor()
    ui.setStyleSheet(qss)
    ui.show()
    sys.exit(app.exec_())
