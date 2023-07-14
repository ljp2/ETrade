import sys
from threading import Thread
from time import sleep
from multiprocessing import Process, Value, Queue
from collections.abc import Iterable    

from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,  QGridLayout, QScrollArea,
    QRadioButton, QGroupBox, QPushButton, QCheckBox, QMessageBox, QInputDialog,
    QComboBox, QLabel
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont
from PyQt6.QtGui import QPalette, QColor

import alpacaAPI as api
from utils import getAccountValue, setAccountValue
import pandas as pd

import mqmain

class MyComboBox(QComboBox):
    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
    def addItems(self, texts: Iterable[str]) -> None:
        self.allTexts = texts
        return super().addItems(texts)
    def setText(self, text:str):
        index = self.allTexts.index(text)
        self.setCurrentIndex(index)

def getTickers():
    df = pd.read_csv('tickers.txt', header=None)
    tickers = df[0].values
    tickers.sort()
    return tickers

def plotter(ticker, charttype, timeframe, timeperiod, av):
    app = QApplication(sys.argv)
    window = mqmain.TickerMainWindow(ticker, charttype, timeframe, timeperiod, av)
    if window.failed:
        QMessageBox.critical(None, 'Critical', 'No Data Available')
        app.exit()
    else:
        window.show()
        app.exec()

def plotProcess(ticker, charttype, timeframe, timeperiod):
    av = getAccountValue()
    args = (ticker, charttype, timeperiod, timeframe, av)
    process = Process(target=plotter, args=args, daemon=True)
    process.start()
    return process


def killProcess(p: Process):
    p.kill()

class MainWindow(QWidget):
    ALL_INTERVALS = list(api.interval_dict.keys())
    ALL_DURATIONS = list(api.duration_dict.keys())
    def __init__(self):
        super(MainWindow, self).__init__()
        self.setWindowTitle("Lou loves Eileen Trade")
        
        self.timeinterval = "NONE"
        self.timeduration  = "NONE"

        top_layout = QVBoxLayout()
        main_layout = QHBoxLayout()
        main_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        
        col2_layout = QVBoxLayout()
        col2_1_layout = QHBoxLayout()
        col2_layout.addWidget(self.chartTypeGroup())
        
        pi_group = QGroupBox('Period - Interval')
        pi_group.setStyleSheet("font-weight: bold;");
        
        pi_group_layout = QHBoxLayout()
        pi_btn_group = self.periodIntervalBtnGroup()
        pi_group_layout.addWidget(pi_btn_group)
        
        for child in pi_btn_group.findChildren(QPushButton):
            child.setStyleSheet("font-weight: normal;");
        
        pi_group_layout.addWidget(self.periodIntervalDropDownGroup())
        pi_group.setLayout(pi_group_layout)
        
        col2_layout.addWidget(QLabel(" "))
        col2_layout.addWidget(pi_group)
        col2_layout.addStretch()

        # Adding the ticker buttons
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True) 
        content_widget = QWidget()
        scroll_area.setWidget(content_widget)
        
        
        main_tb_layout = QVBoxLayout() 
        content_widget.setLayout(main_tb_layout)
        
        ticker_button_group = QGroupBox('Tickers')
        ticker_button_group_layout = QVBoxLayout()
        ticker_button_group.setLayout(ticker_button_group_layout)
        
        for ticker in  getTickers():
            button = QPushButton(ticker)
            button.clicked.connect(self.ticker_button_action)
            ticker_button_group_layout.addWidget(button)
        ticker_button_group_layout.addStretch()
        
        main_tb_layout.addWidget(ticker_button_group)
        
        
        main_layout.addWidget(scroll_area)
        
        
        main_layout.addLayout(col2_layout)
        top_layout.addWidget(self.accountValueWidget())
        top_layout.addLayout(main_layout)
        self.setLayout(top_layout)
        
    def accountValueWidget(self) -> QWidget:
        av_layout = QHBoxLayout()
        av = getAccountValue()
        self.acct_value_label = QLabel('Account Value : ${}'.format(av))
        self.acct_value_label.setFont(QFont('Arial', 10))
        btnChangeAcctValue = QPushButton('Change Acct Value')
        btnChangeAcctValue.clicked.connect(self.changeAcctAction)
        av_layout.addWidget(self.acct_value_label)
        av_layout.addWidget(btnChangeAcctValue)
        av_layout.addStretch()
        w = QWidget()
        w.setLayout(av_layout)
        return w
    
    def changeAcctAction(self, event):
        av = getAccountValue()
        value,ok = QInputDialog.getInt(self,"i Account Value","Enter Account Value ($)",av)
        if ok:
            setAccountValue(value)
            av = getAccountValue()
            self.acct_value_label.setText('Account Value : ${}'.format(av))
                
    
    def tickerButtonGroup(self) -> QGroupBox:
        tb_layout = QVBoxLayout() 
        for ticker in  getTickers():
            button = QPushButton(ticker)
            button.clicked.connect(self.ticker_button_action)
            tb_layout.addWidget(button)
        tb_layout.addStretch()
        ticker_button_group = QGroupBox('Tickers')
        ticker_button_group.setLayout(tb_layout)
        return ticker_button_group
    
    def ticker_button_action(self):
        charttype = self.charttype
        if charttype is None:
            QMessageBox.critical(self, 'Critical', 'Select Chart Type')
            return
        timeinterval = self.ddInterval.currentText()
        timeduration = self.ddDuration.currentText()
        if timeinterval == 'NONE' or timeduration == 'NONE':
            QMessageBox.critical(self, 'Critical', 'Choose Period = Interval')
            return
        pb: QPushButton = self.sender()
        ticker = pb.text()
        timeduration = self.ddDuration.currentText()
        timeinterval = self.ddInterval.currentText()
        plotProcess(ticker, charttype, timeduration, timeinterval)
            
    def chartTypeGroup(self) -> QGroupBox:
        self.charttype: str = None
        charttypes = ['Line', 'Candle', 'HA']
        preselect_type = 'HA'
        charttype_group = QGroupBox('Chart Type')
        charttype_layout = QHBoxLayout()
        for charttype in charttypes:
            radiocharttype = QRadioButton(charttype)
            radiocharttype.toggled.connect(self.on_charttype_changed)
            charttype_layout.addWidget(radiocharttype)
            if charttype == preselect_type:
                radiocharttype.setChecked(charttype == preselect_type)
        charttype_layout.setSpacing(10)
        charttype_group.setLayout(charttype_layout)
        return charttype_group
     
    def on_charttype_changed(self):
        cb: QRadioButton = self.sender()
        if cb.isChecked() == True:
            self.charttype = cb.text().lower()   

    def periodIntervalBtnGroup(self) -> QGroupBox:
        period_intervals = ['1Day - 5Min', '1Week - 1Hr',
                            '1Month - 4Hr', '3Months - 4Hr', '1Year - 1Day', '1Year - 1Week']
        period_inteval_layout = QVBoxLayout()
        for s in period_intervals:
            btn = QPushButton(s)
            btn.clicked.connect(self.changePIaction)
            period_inteval_layout.addWidget(btn)
        period_interval_group = QGroupBox('Favorites')
        period_interval_group.setLayout(period_inteval_layout)
        return period_interval_group
        
    def changePIaction(self):
        btn = self.sender()
        ditxt = btn.text()
        self.timeduration, self.timeinterval = ditxt.split(' - ')
        self.ddDuration.setText(self.timeduration)
        self.ddInterval.setText(self.timeinterval)
         
        
    def periodIntervalDropDownGroup(self):
        pi_layout = QGridLayout()
        font = QFont('Arial', 24)
        
        self.ddInterval = MyComboBox()
        self.ddInterval.setFont(font)
        self.ddInterval.addItems(MainWindow.ALL_INTERVALS)
        
        self.ddDuration = MyComboBox()
        self.ddDuration.setFont(font)
        self.ddDuration.addItems(MainWindow.ALL_DURATIONS)

        pi_layout.addWidget(self.ddDuration, 0, 0)
        pi_layout.addWidget(QLabel(" "), 0, 1)
        pi_layout.addWidget(self.ddInterval, 0, 2 )
        
        period_interval_group = QGroupBox('Current')
        period_interval_group.setLayout(pi_layout)
        
        self.ddDuration.setText('3Months')
        self.ddInterval.setText('4Hr')
        
        return period_interval_group
           
if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    app.exec()
