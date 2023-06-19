
from PyQt6.QtWidgets import (QWidget, QLabel, QLineEdit, QLineEdit, 
                             QVBoxLayout, QHBoxLayout, QGridLayout)
from PyQt6.QtGui import QFont
from PyQt6.QtCore import Qt
from utils import getAccountValue, setAccountValue

from alpacaAPI import get_current_price

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
            potential_profit_per_share = target_price - current_price
            potential_loss_per_share = current_price - stop_price
        if short:
            potential_profit_per_share = current_price - target_price
            potential_loss_per_share = stop_price - current_price 
        profit_loss_ratio = round(potential_profit_per_share/potential_loss_per_share, 2)
        
        av = getAccountValue()
        risk_percent = .5
        risk_dollars = 0.01 * risk_percent * av
        num_shares = round( risk_dollars / potential_loss_per_share)
        
        
        self.layout:QGridLayout = QGridLayout()
        row = 0
        self.addLabelLabel(row, 'Account Value', "${}".format(av))
        row += 1
        self.layout.addWidget(QLabel(" "), row, 0)
        row += 1
        self.addLabelLabel(row, 'Current Price', "${:.2f}".format(current_price))
        row += 1
        self.addLabelLabel(row, 'Target Price', "${:.2f}".format(target_price))
        row += 1
        self.addLabelLabel(row, 'Stop Price', "${:.2f}".format(stop_price))
        row += 1
        self.addLabelLabel(row, 'Potential Profit', "${:.2f}".format(potential_profit_per_share))
        row += 1
        self.addLabelLabel(row, 'Potential Loss', "${:.2f}".format(potential_loss_per_share))
        row += 1
        self.addLabelLabel(row, 'Profit Loss Ratio', "{:.2f}".format(profit_loss_ratio))
        row += 1
        self.addLabelText(row, '% Risk', "{}%".format(risk_percent))
        row += 1
        self.addLabelText(row, '$ Risk', "${:.2f}".format(risk_dollars))
        row += 1
        self.layout.addWidget(QLabel(" "), row, 0)
        row += 1
        self.addLabelText(row, 'Number of Shares', "{}".format(num_shares))               
        self.setLayout(self.layout)

        
    def addLabelLabel(self, row:int, label_1:str, label_2:str):
        qlabel_1 = QLabel(label_1, alignment=Qt.AlignmentFlag.AlignRight)
        qlabel_2 = QLabel(label_2)
        qlabel_1.setFont(QFont('Arial', 24))
        qlabel_2.setFont(QFont('Arial', 24))
        self.layout.addWidget(qlabel_1, row, 0, alignment=Qt.AlignmentFlag.AlignRight)
        self.layout.addWidget(QLabel(':'), row, 1, alignment=Qt.AlignmentFlag.AlignCenter)
        self.layout.addWidget(qlabel_2, row, 2, alignment=Qt.AlignmentFlag.AlignLeft)

    def addLabelText(self, row:int, label:str, text:str):
        qlabel_1 = QLabel(label, alignment=Qt.AlignmentFlag.AlignRight)
        qlabel_1.setFont(QFont('Arial', 24))
        le = QLineEdit(text=text)
        le.setFont(QFont('Arial', 24))
        self.layout.addWidget(qlabel_1, row, 0, alignment=Qt.AlignmentFlag.AlignRight)
        self.layout.addWidget(QLabel(':'), row, 1, alignment=Qt.AlignmentFlag.AlignCenter)
        self.layout.addWidget(le, row, 2, alignment=Qt.AlignmentFlag.AlignLeft)


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
