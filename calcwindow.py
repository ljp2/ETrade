
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
        self.long = self.mainwindow.rbLong.isChecked()
        self.short = self.mainwindow.rbShort.isChecked()
        self.current_price = get_current_price(ticker)
        self.target_price = self.get_target_price()
        self.stop_price = self.get_stop_price()
        if self.long:
            self.potential_profit_per_share = self.target_price - self.current_price
            self.potential_loss_per_share = self.current_price - self.stop_price
        if self.short:
            self.potential_profit_per_share = self.current_price - self.target_price
            self.potential_loss_per_share = self.stop_price - self.current_price 
        self.profit_loss_ratio = round(self.potential_profit_per_share/self.potential_loss_per_share, 2)
        self.av = getAccountValue()
        self.risk_percent = .5
        self.risk_dollars = 0.01 * self.risk_percent * self.av
        self.num_shares = round( self.risk_dollars / self.potential_loss_per_share)
        self.last_risk_percent = self.risk_percent
        self.last_risk_dollars = self.risk_dollars
        
        self.layout:QGridLayout = QGridLayout()
        row = 0
        self.addLabelLabel(row, 'Account Value', "${}".format(self.av))
        row += 1
        self.layout.addWidget(QLabel(" "), row, 0)
        row += 1
        self.addLabelLabel(row, 'Current Price', "${:.2f}".format(self.current_price))
        row += 1
        self.addLabelLabel(row, 'Target Price', "${:.2f}".format(self.target_price))
        row += 1
        self.addLabelLabel(row, 'Stop Price', "${:.2f}".format(self.stop_price))
        row += 1
        self.pot_profit_label = self.addLabelLabel(row, 'Potential Profit', "${:.2f} per share".format(self.potential_profit_per_share))
        row += 1
        self.pot_loss_label= self.addLabelLabel(row, 'Potential Loss', "${:.2f} per share".format(self.potential_loss_per_share))
        row += 1
        self.pl_ratio_label = self.addLabelLabel(row, 'Profit Loss Ratio', "{:.2f}".format(self.profit_loss_ratio))
        row += 1
        self.pct_risk_LE = self.addLabelLineEdit(row, '% Risk', "{:.2f}".format(self.risk_percent), self.on_risk_percent_done)
        row += 1
        self.dollars_risk_LE = self.addLabelLineEdit(row, '$ Risk', "{:.0f}".format(self.risk_dollars), self.on_risk_dollars_done)
        row += 1
        self.layout.addWidget(QLabel(" "), row, 0)
        row += 1
        self.num_shares_lbl = self.addLabelLineEdit(row, 'Number of Shares', "{}".format(self.num_shares))               
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
        le = QLineEdit(text=text)
        le.setFont(QFont('Arial', 24))
        if callback is not None:
            le.leaveEvent = callback
            le.returnPressed.connect(callback)
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

    
    def on_risk_percent_done(self, event=None):
        txt = self.pct_risk_LE.text()
        try:
            risk_percent = float(txt)
            risk_dollars = 0.01 * risk_percent * self.av
        except:
            risk_percent = self.last_risk_percent
            risk_dollars = self.last_risk_dollars
        self.risk_percent = risk_percent
        self.risk_dollars = risk_dollars
        self.num_shares = round( self.risk_dollars / self.potential_loss_per_share)
        self.pct_risk_LE.setText("{:.2f} ".format(self.risk_percent))
        self.dollars_risk_LE.setText("{:.0f}".format(self.risk_dollars))
        self.num_shares_lbl.setText("{}".format(self.num_shares))
        self.last_risk_dollars = self.risk_dollars    
        
           
    def on_risk_dollars_done(self, event=None):
        txt = self.dollars_risk_LE.text()
        try:
            risk_dollars = float(txt)
            risk_percent = (risk_dollars / self.av) * 100
        except:
            risk_percent = self.last_risk_percent
            risk_dollars = self.last_risk_dollars
        self.risk_percent = risk_percent
        self.risk_dollars = risk_dollars
        self.num_shares = round( self.risk_dollars / self.potential_loss_per_share)
        self.pct_risk_LE.setText("{:.2f} ".format(self.risk_percent))
        self.dollars_risk_LE.setText("{:.0f}".format(self.risk_dollars))
        self.num_shares_lbl.setText("{}".format(self.num_shares))
        self.last_risk_dollars = self.risk_dollars