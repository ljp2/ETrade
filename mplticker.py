import sys
import mplfinance as mpf
import pandas_ta as ta

import matplotlib
from matplotlib.gridspec import GridSpec
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

class MplCanvas(FigureCanvasQTAgg):
    def __init__(self, mw, ticker, df:pd.DataFrame, charttype):
        with_stoch_atr_cols = list(df.columns)
        with_stoch_atr_cols.extend(['K', 'D', 'ATR'])
        df.ta.stochrsi(append=True)
        df.ta.atr(append=True)
        df.dropna(inplace=True)
        df.columns = with_stoch_atr_cols
        
        df['low-atr'] = df.low - df.ATR
        df['high+atr'] = df.high + df.ATR
        
        self.current_ATR = df.iloc[-1]['ATR']
        self.mw=mw
        self.ticker = ticker
        
        kwargs = dict(type=charttype)
        mc = mpf.make_marketcolors(up='g',down='r')
        s  = mpf.make_mpf_style(base_mpf_style='yahoo', marketcolors=mc)
        s  = mpf.make_mpf_style(base_mpf_style='yahoo', marketcolors=mc)
        
        self.fig = mpf.figure(figsize=(12,8), style=s)
        
        gs = GridSpec(5,1, figure=self.fig)
 
        self.ax = self.fig.add_subplot(gs[:3, 0])
        self.ax2 = self.fig.add_subplot(gs[3, 0], sharex=self.ax)    
        self.ax1 = self.fig.add_subplot(gs[4, 0], sharex=self.ax)
        
        self.ax2.yaxis.tick_right()
        self.ax2.yaxis.set_label_position("right")
        self.ax2.set_ylabel('ATR')
        
        self.ax1.yaxis.tick_right()
        self.ax1.yaxis.set_label_position("right")
        self.ax1.set_ylim(bottom=-5, top=105)
        self.ax1.set_yticks([0,20,40,60,80,100])

        aps = [
                mpf.make_addplot(df['ATR'], ax=self.ax2, color='black', width=1),
                mpf.make_addplot(df['K'], ax=self.ax1, color='orange', width=1),
                mpf.make_addplot(df['D'], ax=self.ax1, color='blue', width=1),
                mpf.make_addplot(df['low-atr'], ax=self.ax, color='r', width=1),
                mpf.make_addplot(df['high+atr'], ax=self.ax, color='g', width=1),
        ]
        mpf.plot(df, ax=self.ax, addplot=aps, xrotation=10,  datetime_format='%b%d %I:%M%p',**kwargs)
        
        atr_txt = f'ATR = {self.current_ATR:.2f}'
        self.ax.text(0.05, 0.95, atr_txt, transform=self.ax.transAxes, fontsize=10, verticalalignment='top')
        
        
        self.ax1.add_line(Line2D(self.ax1.get_xlim(), [80,80], color='r', linewidth=1))
        self.ax1.add_line(Line2D(self.ax1.get_xlim(), [20,20], color='g', linewidth=1))
        
        self.ax.tick_params('x', labelbottom=False)
        self.ax2.tick_params('x', labelbottom=False)
        self.ax1.tick_params('x', labelsize=8)

        self.fig.tight_layout()
        
        super().__init__(self.fig)
        
        self.current_price = get_current_price(ticker)
        self.current_price_line = Hline(self.ax, self.current_price, ticker=self, lineclass='CurrentPrice', color='violet', moveable=False)
        self.ax.add_line(self.current_price_line)
        
        self.bpid = self.fig.canvas.mpl_connect('button_press_event', self.mouseclick)
 
        self.addlinemode = None
        self.newTline = None
        self.target_line = None
        self.stop_line = None
 
        
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

        