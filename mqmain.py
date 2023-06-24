import sys
from matplotlib.axes._axes import Axes
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
from matplotlib.lines import Line2D

from alpacaAPI import get_bars_dataframe, get_current_price
from ha import HA
from calcwindow import CalcWindow
from draglines import Hline

BTN_BACKGROUND = 'floralwhite'

plot_type_dict = {'line': 'Line', 'candle': 'Candle', 'ha': 'Heiken-Ashi'}

def setAccountValue(value:int):
    with open("av.txt", 'w') as f:
        f.write(str(value))
    
def getAccountValue():
    with open("av.txt", 'r') as f:
        av = int(f.readline())
    return av

class MyCursor(Cursor):
    def __init__(self, ax: Axes, other_axes:Axes=None,
                 horizOn: bool = True, vertOn: bool = True, useblit: bool = False, **lineprops) -> None:
        super().__init__(ax, horizOn, vertOn, useblit, linewidth=1, color='black', **lineprops)
        self.other_axes = other_axes
        self.other_canvas = other_axes.get_figure().canvas
        x = sum(self.other_axes.get_xlim()) / 2
        self.other_cursor:Line2D = self.other_axes.axvline(x, lw=1, ls='--', color='black')
        

    def onmove(self, event):
        super().onmove(event)
        # print(event.xdata)
        # sys.stdout.flush()
        x = event.xdata
        if self.visible and  self.other_axes and x:
            # print(x, self.other_cursor.get_xdata())
            self.other_cursor.set_xdata([x,x])
            self.other_canvas.draw_idle()
            
            

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
        self.cursor = MyCursor(self.sc.ax, other_axes=self.sc.ax1, useblit=False, ls='--')
        
        widget = QtWidgets.QWidget()
        widget.setLayout(layout)
        self.setCentralWidget(widget)
        
        self.timer = QtCore.QTimer()
        self.timer.timeout.connect(self.on_btnRefreshPrice)
        self.timer.start(15000)

        self.show()

    def accountValueLabel(self):
        av = getAccountValue()
        av_label = QLabel("Acct Value : ${}".format(av))
        av_label.setFont(QFont('Arial', 18))
        return av_label
    

    def clearButtonBackgrounds(self):
        for btn in self.cmd_buttons.values():
            btn.setStyleSheet(f"background-color: {BTN_BACKGROUND}")
            
    
    def addButton(self, txt, layout, btn_dict, btncallbk, width=None, height=None) -> QPushButton:
        btn = QPushButton(txt)
        btn.setStyleSheet(f"background-color: {BTN_BACKGROUND}")
        if height: btn.setFixedHeight(height)
        if width: btn.setFixedWidth(width)
        btn.clicked.connect(btncallbk)
        layout.addWidget(btn)
        btn_dict[txt] = btn
        return btn

    def cmdLineWidget(self):
        cmd_line_layout = QHBoxLayout()
        self.btnCursor = self.addButton('+', cmd_line_layout, self.cmd_buttons, self.on_btnCursorClicked, 50, 40 )
        self.btnTrend = self.addButton('/', cmd_line_layout, self.cmd_buttons, self.on_btnTrendClicked, 50, 40)
        self.btnSR = self.addButton('SR', cmd_line_layout, self.cmd_buttons, self.on_btnSRClicked, 50, 40)
        self.btnTarget = self.addButton('Tar', cmd_line_layout, self.cmd_buttons, self.on_btnTargetClicked, 50, 40)
        self.btnStop = self.addButton('Stp', cmd_line_layout, self.cmd_buttons, self.on_btnStopClicked, 50, 40)

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
        
        self.btnCalc = self.addButton('Calc', cmd_line_layout, self.cmd_buttons, self.on_btnCalcClicked, 50, 40)
        self.btnAddMoveTarget = self.addButton('Set\nTarget', cmd_line_layout, self.cmd_buttons, self.on_btnAMTarget)
        cmd_line_layout.addWidget(QLabel("    "))
        
        cmd_line_layout.addStretch()
        
        self.btnRefresh = self.addButton('Refresh\nCurrent Price', cmd_line_layout, self.cmd_buttons, self.on_btnRefreshPrice)
        cmd_line_layout.addWidget(QLabel("    "))
        
        av = getAccountValue()
        avlabel = QLabel("Account Value : ${}".format(av))
        avlabel.setFont(QFont('Arial', 18))
        cmd_line_layout.addWidget(avlabel)
        
        cmd_line_widget = QWidget()
        cmd_line_widget.setLayout(cmd_line_layout)
        cmd_line_widget.setFixedHeight(60)
        cmd_line_widget.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        return cmd_line_widget
    
    def on_btnAMTarget(self):
        if self.rbLong.isChecked() + self.rbShort.isChecked()  == 0:
            QMessageBox.critical(self, 'Critical', 'Select Long or Short')
            return
        if self.sc.stop_line:
            stop_y = self.sc.stop_line.get_ydata()[0]
            price_line_y = self.sc.current_price_line.get_ydata()[0]
            current_atr = self.sc.current_ATR
        else:
            return
        if self.rbLong.isChecked():
            price_stop_diff = price_line_y - stop_y
            y2atr = price_line_y + 2 * price_stop_diff
        elif self.rbShort.isChecked():
            price_stop_diff = stop_y - price_line_y
            y2atr = price_line_y - 2 * price_stop_diff
        else:
            return
        if self.sc.target_line:
            self.sc.target_line.moveline(y2atr)
        else:
            line = Hline(self.sc.ax, y2atr, ticker=self, lineclass='Target', color='green')
            self.sc.ax.add_line(line)
            self.sc.fig.canvas.draw_idle()

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
        
    def on_btnRefreshPrice(self):
        self.sc.current_price = get_current_price(self.ticker)
        self.sc.current_price_line.moveline(self.sc.current_price)

        
    def target_line_is_set(self):
        self.btnTarget.setStyleSheet(f"background-color: {BTN_BACKGROUND}")
        
    def stop_line_is_set(self):
        self.btnStop.setStyleSheet(f"background-color: {BTN_BACKGROUND}")
    
    def sr_line_set(self):
        self.btnSR.setStyleSheet(f"background-color: {BTN_BACKGROUND}")
        
    def trend_line_set(self):
        self.btnTrend.setStyleSheet(f"background-color: {BTN_BACKGROUND}")        
