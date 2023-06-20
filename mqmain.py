import sys
import pandas as pd
from multiprocessing import Value

from PyQt6 import QtCore, QtGui, QtWidgets
from PyQt6.QtGui import QFont
from PyQt6.QtWidgets import (QMainWindow, QApplication, QWidget, QLabel, QCheckBox, QPushButton, QRadioButton,
                             QComboBox, QListWidget, QLineEdit, QMessageBox, QInputDialog,
                             QVBoxLayout, QHBoxLayout, QSizePolicy)
from mplticker import MplCanvas
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolbar
from matplotlib.widgets import Cursor

from alpacaAPI import get_bars_dataframe, get_current_price
from ha import HA
from calcwindow import CalcWindow

BTN_BACKGROUND = 'floralwhite'

plot_type_dict = {'line': 'Line', 'candle': 'Candle', 'ha': 'Heiken-Ashi'}

def setAccountValue(value:int):
    with open("av.txt", 'w') as f:
        f.write(str(value))
    
def getAccountValue():
    with open("av.txt", 'r') as f:
        av = int(f.readline())
    return av


class MyToolbar(NavigationToolbar):
    origtoolitems = [*NavigationToolbar.toolitems]
    toolitems = [x for x in origtoolitems if x[0] in "Home Back Forward Pan Zoom Save".split()]
    def __init__(self, canvas, parent, coordinates=True):
        super().__init__(canvas, parent, coordinates)
        

class TickerMainWindow(QMainWindow):
    def __init__(self,  ticker, charttype, timeframe, timeperiod, av):
        df = get_bars_dataframe(ticker, timeperiod, timeframe)
        if df is None:
            self.failed = True
            return
        super().__init__()
        self.failed = False
        self.cmd_buttons = {}
        self.account_value = av
        self.ticker = ticker
        
        ploytype = plot_type_dict[charttype]
        title = f'{ticker}  {ploytype}   {timeperiod}  -  {timeframe}'
        self.setWindowTitle(title)
        match charttype:
            case 'line':
                mplcharttype = 'line'
                mpl_df = df
            case 'candle':
                mplcharttype = 'candle'
                mpl_df = df
            case 'ha':
                df.index = pd.to_datetime(df.index)
                mplcharttype = 'candle'
                mpl_df = HA(df)
        
        
        self.sc = MplCanvas(self, ticker, mpl_df, mplcharttype)
        toolbar = MyToolbar(self.sc, self)
        
        layout = QVBoxLayout()

        layout.addWidget(self.cmdLineWidget())
        layout.addWidget(self.sc)
        layout.addWidget(toolbar)

        self.calc_window = None
        self.cursor = Cursor(self.sc.ax, useblit=True)
        self.cursor.visible = False
        
        widget = QtWidgets.QWidget()
        widget.setLayout(layout)
        self.setCentralWidget(widget)

        self.show()
        
    def accountValueLabel(self):
        av = getAccountValue()
        av_label = QLabel("Acct Value : ${}".format(av))
        av_label.setFont(QFont('Arial', 18))
        return av_label
    

    def clearButtonBackgrounds(self):
        for btn in self.cmd_buttons.values():
            btn.setStyleSheet(f"background-color: {BTN_BACKGROUND}")
            
    
    def addButton(self, txt, layout, btn_dict, btncallbk) -> QPushButton:
        btn = QPushButton(txt)
        btn.setStyleSheet(f"background-color: {BTN_BACKGROUND}")
        btn.setFixedSize(50, 40)
        btn.clicked.connect(btncallbk)
        layout.addWidget(btn)
        btn_dict[txt] = btn
        return btn

    def cmdLineWidget(self):
        cmd_line_layout = QHBoxLayout()
        self.btnCursor = self.addButton('+', cmd_line_layout, self.cmd_buttons, self.on_btnCursorClicked)
        self.btnTrend = self.addButton('/', cmd_line_layout, self.cmd_buttons, self.on_btnTrendClicked)
        self.btnSR = self.addButton('SR', cmd_line_layout, self.cmd_buttons, self.on_btnSRClicked)
        self.btnTarget = self.addButton('Tar', cmd_line_layout, self.cmd_buttons, self.on_btnTargetClicked)
        self.btnStop = self.addButton('Stp', cmd_line_layout, self.cmd_buttons, self.on_btnStopClicked)

        cmd_line_layout.addWidget(QLabel("    "))

        rb_layout = QHBoxLayout()
        self.rbLong:QRadioButton = QRadioButton('Long')
        self.rbShort:QRadioButton = QRadioButton('Short')
        rb_layout.addWidget(self.rbLong)
        rb_layout.addWidget(self.rbShort)
        rb_widget = QWidget()
        rb_widget.setLayout(rb_layout)
        cmd_line_layout.addWidget(rb_widget)
        
        cmd_line_layout.addWidget(QLabel("    "))
        
        self.btnCalc = self.addButton('Calc', cmd_line_layout, self.cmd_buttons, self.on_btnCalcClicked)
        cmd_line_layout.addStretch()
        
        av = getAccountValue()
        avlabel = QLabel("Account Value : ${}".format(av))
        avlabel.setFont(QFont('Arial', 18))
        cmd_line_layout.addWidget(avlabel)
        
        cmd_line_widget = QWidget()
        cmd_line_widget.setLayout(cmd_line_layout)
        cmd_line_widget.setFixedHeight(60)
        cmd_line_widget.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        return cmd_line_widget
        

    def on_btnCursorClicked(self):
        self.cursor.visible = not self.cursor.visible

    def on_btnTrendClicked(self):
        pb: QPushButton = self.sender()
        self.clearButtonBackgrounds()
        if self.sc.addlinemode == 'Trend':
            self.sc.addlinemode = None
            self.sc.reset_trend()
        else:
            self.sc.addlinemode = 'Trend'
            pb.setStyleSheet("background-color: lightblue")

    def on_btnSRClicked(self):
        if self.sc.addlinemode == 'Trend':
            return
        pb: QPushButton = self.sender()
        self.clearButtonBackgrounds()
        if self.sc.addlinemode == 'SR':
            self.sc.addlinemode = None
            pb.setStyleSheet(f"background-color: {BTN_BACKGROUND}")
        else:
            self.sc.addlinemode = 'SR'
            pb.setStyleSheet("background-color: lightblue")

    def on_btnTargetClicked(self):
        if self.sc.addlinemode == 'Trend':
            return
        pb: QPushButton = self.sender()
        self.clearButtonBackgrounds()
        if self.sc.addlinemode == 'Target':
            self.sc.addlinemode = None
            pb.setStyleSheet(f"background-color: {BTN_BACKGROUND}")
        else:
            self.sc.addlinemode = 'Target'
            pb.setStyleSheet("background-color: lightgreen")


    def on_btnStopClicked(self):
        if self.sc.addlinemode == 'Trend':
            return
        pb: QPushButton = self.sender()
        self.clearButtonBackgrounds()
        if self.sc.addlinemode == 'Stop':
            self.sc.addlinemode = None
            pb.setStyleSheet(f"background-color: {BTN_BACKGROUND}")
        else:
            self.sc.addlinemode = 'Stop'
            pb.setStyleSheet("background-color: red")

    def on_btnCalcClicked(self):
        if self.rbLong.isChecked() + self.rbShort.isChecked()  == 0:
            QMessageBox.critical(self, 'Critical', 'Select Long or Short')
            return
        if self.sc.target_line is None:
            QMessageBox.critical(self, 'Critical', 'No Target Line')
            return
        if self.sc.stop_line is None:
            QMessageBox.critical(self, 'Critical', 'No Stop Line')
            return
        long = self.rbLong.isChecked()
        short = self.rbShort.isChecked()
        current_price = get_current_price(self.ticker)
        target_price = self.sc.target_line.get_ydata()[0]
        stop_price = self.sc.stop_line.get_ydata()[0]
        if long:
            if stop_price > target_price:
                problem_text = "Long and\nstop_price > target_price"
                QMessageBox.critical(self, 'Critical', problem_text)
                return
            if target_price < current_price:
                problem_text = "Long and\ntarget_price < current_price"
                QMessageBox.critical(self, 'Critical', problem_text)
                return
            if stop_price > current_price:
                problem_text = "Long and\nstop_price > current_price"
                QMessageBox.critical(self, 'Critical', problem_text)
                return     
        if short:
            if target_price > stop_price:
                problem_text = "Short and\ntarget_price > stop_price"
                QMessageBox.critical(self, 'Critical', problem_text)
                return
            if target_price > current_price:
                problem_text = "Short and\ntarget_price > current_price"
                QMessageBox.critical(self, 'Critical', problem_text)
                return
            if stop_price < current_price:
                problem_text = "Short and\nstop_price < current_price"
                QMessageBox.critical(self, 'Critical', problem_text)
                return
        
        if self.sc.addlinemode == 'Trend':
            return
        pb: QPushButton = self.sender()
        self.clearButtonBackgrounds()
        self.calc_window = CalcWindow(self, self.ticker)
        self.calc_window.show()
        

    def target_line_is_set(self):
        self.btnTarget.setStyleSheet(f"background-color: {BTN_BACKGROUND}")
        
    def stop_line_is_set(self):
        self.btnStop.setStyleSheet(f"background-color: {BTN_BACKGROUND}")
    
    def sr_line_set(self):
        self.btnSR.setStyleSheet(f"background-color: {BTN_BACKGROUND}")
        
    def trend_line_set(self):
        self.btnTrend.setStyleSheet(f"background-color: {BTN_BACKGROUND}")        
