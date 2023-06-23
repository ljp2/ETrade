
from PyQt6.QtWidgets import (QWidget, QLabel, QLineEdit, QLineEdit, 
                             QVBoxLayout, QHBoxLayout, QGridLayout)
from PyQt6.QtGui import QFont
from PyQt6.QtCore import Qt
from utils import getAccountValue, setAccountValue

from alpacaAPI import get_current_price

class MyLineEdit(QLineEdit):

    def __init__(self, text:str):
        super().__init__(text)

    def enterEvent(self, QEvent):
        self.enter_txt = self.text()

    def leaveEvent(self, QEvent):
        print("Leaving text", self.text())

class CalcWindow(QWidget):
    
    def __init__(self, mainwindow, ticker:str):
        super().__init__()
        self.mainwindow = mainwindow
        long = self.mainwindow.rbLong.isChecked()
        short = self.mainwindow.rbShort.isChecked()
        current_price = get_current_price(ticker)
        target_price = self.get_target_price()
        stop_price = self.get_stop_price()
        if long:
            self.potential_profit_per_share = target_price - current_price
            self.potential_loss_per_share = current_price - stop_price
        if short:
            self.potential_profit_per_share = current_price - target_price
            self.potential_loss_per_share = stop_price - current_price 
        profit_loss_ratio = round(self.potential_profit_per_share/self.potential_loss_per_share, 2)
        self.av = getAccountValue()
        self.risk_percent = .5
        self.risk_dollars = 0.01 * self.risk_percent * self.av
        self.num_shares = round( self.risk_dollars / self.potential_loss_per_share)
        
        self.layout:QGridLayout = QGridLayout()
        row = 0
        self.addLabelLabel(row, 'Account Value', "${}".format(self.av))
        row += 1
        self.layout.addWidget(QLabel(" "), row, 0)
        row += 1
        self.addLabelLabel(row, 'Current Price', "${:.2f}".format(current_price))
        row += 1
        self.addLabelLabel(row, 'Target Price', "${:.2f}".format(target_price))
        row += 1
        self.addLabelLabel(row, 'Stop Price', "${:.2f}".format(stop_price))
        row += 1
        self.pot_profit = self.addLabelLabel(row, 'Potential Profit', "${:.2f}".format(self.potential_profit_per_share))
        row += 1
        self.pot_loss = self.addLabelLabel(row, 'Potential Loss', "${:.2f}".format(self.potential_loss_per_share))
        row += 1
        self.pl_ratio = self.addLabelLabel(row, 'Profit Loss Ratio', "{:.2f}".format(profit_loss_ratio))
        row += 1
        self.pct_risk_LE = self.addLabelLineEdit(row, '% Risk', "{:.2f}%".format(self.risk_percent), self.on_mouse_leave_risk_percent)
        row += 1
        self.dollars_risk_LE = self.addLabelLineEdit(row, '$ Risk', "${:.0f}".format(self.risk_dollars), self.on_mouse_leave_risk_dollars)
        row += 1
        self.layout.addWidget(QLabel(" "), row, 0)
        row += 1
        self.addLabelLineEdit(row, 'Number of Shares', "{}".format(self.num_shares))               
        self.setLayout(self.layout)


    def addLabelLabel(self, row:int, label_1:str, label_2:str):
        qlabel_1 = QLabel(label_1, alignment=Qt.AlignmentFlag.AlignRight)
        qlabel_2 = QLabel(label_2)
        qlabel_1.setFont(QFont('Arial', 24))
        qlabel_2.setFont(QFont('Arial', 24))
        self.layout.addWidget(qlabel_1, row, 0, alignment=Qt.AlignmentFlag.AlignRight)
        self.layout.addWidget(QLabel(':'), row, 1, alignment=Qt.AlignmentFlag.AlignCenter)
        self.layout.addWidget(qlabel_2, row, 2, alignment=Qt.AlignmentFlag.AlignLeft)
        return qlabel_2

    def addLabelLineEdit(self, row:int, label:str, text:str, callback=None):
        qlabel_1 = QLabel(label, alignment=Qt.AlignmentFlag.AlignRight)
        qlabel_1.setFont(QFont('Arial', 24))
        le = MyLineEdit(text=text)
        le.setFont(QFont('Arial', 24))
        if callback is not None:
            le.leaveEvent = callback
        self.layout.addWidget(qlabel_1, row, 0, alignment=Qt.AlignmentFlag.AlignRight)
        self.layout.addWidget(QLabel(':'), row, 1, alignment=Qt.AlignmentFlag.AlignCenter)
        self.layout.addWidget(le, row, 2, alignment=Qt.AlignmentFlag.AlignLeft)
        return le

    def closeEvent(self, event):
        self.mainwindow.calc_window = None

    def get_target_price(self):
        yy = self.mainwindow.sc.target_line.get_ydata()
        price = round(yy[0],2)
        return price
    
    def get_stop_price(self):
        yy = self.mainwindow.sc.stop_line.get_ydata()
        price = round(yy[0],2)
        return price
    
    def on_mouse_leave_risk_percent(self, event):
        txt = self.pct_risk_LE.text()
        self.risk_percent = float(txt.split('%')[0])
        self.risk_dollars = 0.01 * self.risk_percent * self.av
        self.dollars_risk_LE.setText("${:.0f}".format(self.risk_dollars))

        
    def on_mouse_leave_risk_dollars(self, event):
        txt = self.dollars_risk_LE.text()
        self.risk_dollars = float(txt.split('$')[1])
        self.risk_percent = (self.risk_dollars / self.av) * 100
        self.pct_risk_LE.setText("{:.2f}%".format(self.risk_percent))


