import sys
import mplfinance as mpf
import pandas_ta as ta

# from PyQt6 import QtCore, QtGui, QtWidgets

# from PyQt6.QtWidgets import ( QMainWindow, QApplication, QLabel, QCheckBox, QPushButton, QRadioButton,
#         QComboBox, QListWidget, QLineEdit, QLineEdit, QSpinBox, QDoubleSpinBox, QSlider,
#         QVBoxLayout, QHBoxLayout)

import matplotlib
matplotlib.use('QtAgg')

import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg, NavigationToolbar2QT as NavigationToolbar
from matplotlib.figure import Figure
from matplotlib.axes import Axes
from matplotlib.backend_bases import Event
from matplotlib.lines import Line2D

from alpacaAPI import get_current_price

from draglines import Hline, TLine

import pandas as pd
# def read_bars(fn: str):
#     df = pd.read_csv(f'/Users/ljp2/Alpaca/Data/bars1/{fn}.csv')
#     df['timestamp'] = pd.to_datetime(df.time)
#     df.drop('time',axis=1, inplace=True)
#     df.set_index('timestamp', drop=True, inplace=True)
#     return df

class MplCanvas(FigureCanvasQTAgg):
    def __init__(self, mw, ticker, df:pd.DataFrame, charttype):
        with_stoch_cols = list(df.columns)
        with_stoch_cols.extend(['K', 'D'])
        df.ta.stoch(append=True)
        df.columns = with_stoch_cols

        self.mw=mw
        self.ticker = ticker
        
        kwargs = dict(type=charttype)
        mc = mpf.make_marketcolors(up='g',down='r')
        s  = mpf.make_mpf_style(base_mpf_style='yahoo', marketcolors=mc)
        s  = mpf.make_mpf_style(base_mpf_style='yahoo', marketcolors=mc)
        
        self.fig = mpf.figure(figsize=(10,5), style=s)
        
        self.ax = self.fig.subplot(211)
        self.ax1 = self.fig.subplot(212, sharex=self.ax)
        
        # (self.ax, self.ax1) = self.fig.subplots(2, 1, gridspec_kw={'height_ratios' : [3,1]})
        
        
        ap = mpf.make_addplot(df[['K','D']], ax=self.ax1, ylabel='Stoch')
        mpf.plot(df, ax=self.ax, addplot=ap, xrotation=10, **kwargs)

        
        
        
        # mpf.plot(df, ax=self.ax, xrotation=10, style=s, **kwargs)
        # self.ax1.plot(df[['K','D']])
        
        self.fig.tight_layout()
    
         
         
        
        
        
        # apd = [mpf.make_addplot(df['K'], panel=1),
        #        mpf.make_addplot(df['D'], panel=1),                
        # ]
                  
        # # self.f, self.axlist = mpf.plot(df, returnfig=True, figsize=(10,5),
        # #                              addplot=apd, figscale=1.2,
        # #                              xlabel='', ylabel='', **kwargs, style=s )
        
        
        # mpf.plot(df, figsize=(10,5),  xlabel='', ylabel='',  addplot=apd )


        
        # self.fig:Figure = self.f
        # self.ax:Axes = self.axlist[0]
        # self.ax.set_position([0.0, 0.0, 0.95, 1])
        super().__init__(self.fig)
        
        self.current_price = get_current_price(ticker)
        self.current_price_line = Hline(self.ax, self.current_price, ticker=self, lineclass='CurrentPrice', color='violet', moveable=False)
        self.ax.add_line(self.current_price_line)
        
        self.bpid = self.fig.canvas.mpl_connect('button_press_event', self.mouseclick)
 
        self.addlinemode = None
        self.newTline = None
        self.target_line = None
        self.stop_line = None
        self.clicks = 0
        
        # self.fig.canvas.draw_idle()
        
    def reset_trend(self):
        if self.newTline is None:
            pass
        else:
            self.clicks = 0
            self.newTline.remove()
            self.fig.canvas.draw_idle()
            self.newTline = None
        
    def mouseclick(self, event:Event):
        match self.addlinemode:
            case 'Trend':
                y = event.ydata
                if y is None:
                    pass
                if self.clicks == 0:
                    self.x = event.xdata
                    self.y = event.ydata
                    self.clicks = 1
                    self.newTline = TLine(self.ax, self.x, self.y)
                    self.ax.add_line(self.newTline)
                    self.fig.canvas.draw_idle()
                elif self.clicks == 1:
                    self.newTline.secondPtAdded()
                    self.clicks = 0
                    self.addlinemode = None
                    self.newTline = None
                    self.mw.trend_line_set()
            
            case 'SR':
                y = event.ydata
                if y is None:
                    pass
                else:
                    line = Hline(self.ax, event.ydata, ticker=self, lineclass='SR', color='blue')
                    self.ax.add_line(line)
                    self.fig.canvas.draw_idle()
                    self.addlinemode = None
                    self.mw.sr_line_set()
                
            case 'Target':
                y = event.ydata
                if y is None:
                    pass
                elif (self.target_line is None):
                    line = Hline(self.ax, y, ticker=self, lineclass='Target', color='green')
                    self.ax.add_line(line)

                    self.fig.canvas.draw_idle()
                    self.addlinemode = None
                    self.target_line = line
                    self.mw.target_line_is_set()

            case 'Stop':
                y = event.ydata
                if y is None:
                    pass
                elif (self.stop_line is None):
                    line = Hline(self.ax, y, ticker=self, lineclass='Stop', color='red')
                    self.ax.add_line(line)
                    self.fig.canvas.draw_idle()
                    self.addlinemode = None
                    self.stop_line = line
                    self.mw.stop_line_is_set()

        