# -*- coding: utf-8 -*-
"""
@File    : main_1224.py
@Author  : hm325800
@Time    : 2020/12/24 20:54
"""
from PyQt5 import QtCore, QtGui
from PyQt5.QtWidgets import (QMainWindow, QApplication, QMessageBox, QWidget, QGridLayout, QPushButton, QDialog,
                             QFrame, QLabel, QToolButton, QFileDialog,
                             QDesktopWidget, QDateTimeEdit)
from PyQt5.QtGui import QCursor, QIcon, QMouseEvent
from PyQt5.QtCore import Qt, QDateTime, QVersionNumber, QT_VERSION_STR
import sys
import numpy as np
import pandas as pd
import pyqtgraph as pg
from pyqtgraph import PlotWidget
import OpenOPC
import pywintypes

from JJSH_MainWindow import Ui_JJSH_MainWindow
from call_DC_optimize import JJSH_Form_DC_Optimize
from call_FCCU_Monitor import JJSH_Form_FCCU_Monitor
import functools
import ctypes


def get_screen_dpi():
    user32 = ctypes.windll.user32
    gdi32 = ctypes.windll.gdi32
    LOGPIXELSX = 88
    LOGPIXELSY = 90
    user32.SetProcessDPIAware()
    hDC = user32.GetDC(0)
    hdpi = gdi32.GetDeviceCaps(hDC, LOGPIXELSX)
    ydpi = gdi32.GetDeviceCaps(hDC, LOGPIXELSY)
    return hdpi, ydpi


class JJSH_MainWindow(QMainWindow, Ui_JJSH_MainWindow):
    def __init__(self, parent=None):
        super(JJSH_MainWindow, self).__init__(parent)
        self.setupUi(self)

        # 初始化右上角的时间
        self.main_timer = QtCore.QTimer()
        self.main_timer.start(1000)
        self.main_timer.timeout.connect(self.showtime)

        # 初始化主窗口为设计时的样式
        self.init_qss('JJSH_style.qss')
        self.init_main_window_para = self.geometry()
        # self.init_dpi = 96  # 设计时屏幕的dpi

        # 加入子窗口qWidget_DC_Optimize，并并初始化设计时的窗口大小
        self.qWidget_DC_Optimize = JJSH_Form_DC_Optimize()
        self.qWidget_DC_Optimize.setObjectName('JJSH_Form_DC_Optimize')
        self.gridLayout.addWidget(self.qWidget_DC_Optimize, 3, 1, 1, 1)
        self.qWidget_DC_Optimize.show()
        self.qWidget_DC_Optimize.get_frame_DC_picture_size()
        self.qWidget_DC_Optimize.hide()

        # 加入子窗口qWidget_FCCU_Monitor，并并初始化设计时的窗口大小
        self.qWidget_FCCU_Monitor = JJSH_Form_FCCU_Monitor()
        self.qWidget_FCCU_Monitor.setObjectName('JJSH_Form_FCCU_Monitor')
        self.gridLayout.addWidget(self.qWidget_FCCU_Monitor, 3, 1, 1, 1)
        self.qWidget_FCCU_Monitor.show()
        self.qWidget_FCCU_Monitor.get_frame_FCCU_picture_size()
        self.qWidget_FCCU_Monitor.hide()

        # 使主窗口根据界面大小调整界面尺寸
        self.self_adjust_window_size()

        # 初始化主窗口的按钮和界面文字
        self.init_main_window_text()
        self.init_btn_connect()

        # 隐藏不必要的窗口
        self.qWidget_DC_Optimize.hide()
        self.qWidget_FCCU_Monitor.hide()

    # ******定义界面外观相关函数******
    def showtime(self):
        time = QDateTime.currentDateTime()  # 获取当前时间
        time_display = time.toString("yyyy-MM-dd hh:mm:ss dddd")  # 格式化一下时间
        self.label_system_time.setText(time_display)

    def init_qss(self, file_name):
        with open(file_name, encoding='utf-8') as f:
            qss = f.read()
        self.setStyleSheet(qss)

    def init_main_window_text(self):
        self.label_title.setText('面向炼油生产过程的工程优化运行软件')
        temp_width = self.pushButton_main_home.width()
        self.widget_title.layout().setContentsMargins(int(temp_width / 4), 0, 15, 0)
        self.widget_main_nav.layout().setContentsMargins(0, 0, 15, 0)

        self.pushButton_main_home.setText('首页')
        self.pushButton_main_model.setText('系统建模')
        self.pushButton_main_monitor.setText('运行监测')
        self.pushButton_main_optimize.setText('运行优化')
        self.pushButton_main_tool.setText('工具')
        self.pushButton_main_help.setText('帮助')
        self.pushButton_main_help.objectName()
        for name, _ in vars(self).items():
            if 'pushButton_sub_nav' in name:
                eval('self.' + name).setText('')
                eval('self.' + name).hide()
        self.pushButton_sub_nav_1.setText('催化裂化装置')
        self.pushButton_sub_nav_2.setText('柴油加氢装置')
        self.pushButton_sub_nav_1.show()
        self.pushButton_sub_nav_2.show()

    # ******定义窗口自适应函数******
    def self_adjust_window_size(self):
        normal_scale = 0.8  # 定义初始化界面占屏幕大小的80%
        desktop = QApplication.desktop()
        scale_rate = desktop.width() / self.init_main_window_para.width()
        if scale_rate > desktop.height() / self.init_main_window_para.height():
            scale_rate = desktop.height() / self.init_main_window_para.height()
        # hdpi, _ = get_screen_dpi()  # 获取当前屏幕的dpi
        # print(hdpi)
        # scale_rate = scale_rate*(self.init_dpi/hdpi)
        scale_rate = scale_rate * normal_scale

        with open('JJSH_style.qss', encoding='utf-8') as f:
            qss = f.readlines()

        for idx_item in range(len(qss)):
            item = qss[idx_item]
            if ('min-' in item) or ('max-' in item) or ('font-size' in item):
                num = int(item.split(':')[1].split('p')[0])
                num = int(num * scale_rate)
                if num == 0:
                    num = 1
                qss[idx_item] = item.split(':')[0] + ': ' + str(num) + 'p' + item.split(':')[1].split('p')[1]
            elif 'qproperty-iconSize' in item:
                num0 = int(item.split(':')[1].split('px')[0])
                num1 = int(item.split(':')[1].split('px')[1])
                num0 = int(num0*scale_rate)
                num1 = int(num1*scale_rate)
                qss[idx_item] = item.split(':')[0] + ': ' + str(num0) + 'px ' + str(num1) + 'px' + item.split(':')[1].split('px')[2]

        with open('JJSH_style_adjust.qss', 'w', encoding='utf-8') as f:
            f.writelines(qss)
        self.init_qss('JJSH_style_adjust.qss')
        self.resize(desktop.width()*normal_scale, desktop.height()*normal_scale)
        self.setWindowFlags(Qt.FramelessWindowHint)

    # ******定义按钮相关函数******
    def init_btn_connect(self):
        for name, _ in vars(self).items():
            if 'Button' in name:
                eval('self.' + name).clicked.connect(functools.partial(self.btn_clicked_func, eval('self.' + name)))

    def btn_clicked_func(self, btn):
        if 'pushButton_main' in btn.objectName():
            self.disable_myself(btn.objectName(), 'pushButton_main')
            if btn.objectName() == 'pushButton_main_home':
                print(btn.objectName())
            elif btn.objectName() == 'pushButton_main_model':
                print(btn.objectName())
            elif btn.objectName() == 'pushButton_main_monitor':#添加FCCU界面
                print(btn.objectName())
                self.widget_mainWindow.hide()
                self.qWidget_DC_Optimize.hide()
                self.qWidget_FCCU_Monitor.show()
                print(self.qWidget_FCCU_Monitor.frame_FCCU_picture.geometry())
            elif btn.objectName() == 'pushButton_main_optimize':
                print(btn.objectName())
                self.widget_mainWindow.hide()
                self.qWidget_FCCU_Monitor.hide()
                self.qWidget_DC_Optimize.show()
                #self.connect.lastWindowClosed()
                print(self.qWidget_DC_Optimize.frame_DC_picture.geometry())
        elif btn.objectName() == 'pushButton_close':
            self.close()
        elif btn.objectName() == 'pushButton_minimize':
            self.showMinimized()
        elif btn.objectName() == 'pushButton_maximize':
            if self.isFullScreen():
                self.pushButton_maximize.setStyleSheet('border-image: url(":/img/images/maximize.png") on')
                self.showNormal()
            else:
                self.pushButton_maximize.setStyleSheet('border-image: url(":/img/images/normal.png") on')
                self.showFullScreen()

    def disable_myself(self, my_btn, level_name):
        for name, _ in vars(self).items():
            if level_name in name:
                if name == my_btn:
                    eval('self.' + name).setEnabled(False)
                else:
                    eval('self.' + name).setEnabled(True)

    # ******事件函数******
    def closeEvent(self, event):
        reply = QMessageBox.question(self, '是否要退出程序', '确认退出？',
                                     QMessageBox.Yes, QMessageBox.No)
        if reply == QMessageBox.Yes:
            event.accept()
        else:
            event.ignore()

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.m_flag = True
            self.m_Position = event.globalPos() - self.pos()  # 获取鼠标相对窗口的位置
            event.accept()
            self.setCursor(QCursor(Qt.OpenHandCursor))  # 更改鼠标图标

    def mouseMoveEvent(self, QMouseEvent):
        if Qt.LeftButton and self.m_flag:
            self.move(QMouseEvent.globalPos() - self.m_Position)  # 更改窗口位置
            QMouseEvent.accept()

    def mouseReleaseEvent(self, QMouseEvent):
        self.m_flag = False
        self.setCursor(QCursor(Qt.ArrowCursor))


if __name__ == '__main__':
    pywintypes.datetime = pywintypes.TimeType
    QApplication.setAttribute(Qt.AA_EnableHighDpiScaling)  # Qt从5.6.0开始，支持High-DPI
    app = QApplication(sys.argv)
    ui = JJSH_MainWindow()
    # app.setStyleSheet(qss)
    ui.show()
    sys.exit(app.exec_())
