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
        with_stoch_cols = list(df.columns)
        with_stoch_cols.extend(['K', 'D'])
        df.ta.stoch(append=True)
        df.dropna(inplace=True)
        df.columns = with_stoch_cols

        self.mw=mw
        self.ticker = ticker
        
        kwargs = dict(type=charttype)
        mc = mpf.make_marketcolors(up='g',down='r')
        s  = mpf.make_mpf_style(base_mpf_style='yahoo', marketcolors=mc)
        s  = mpf.make_mpf_style(base_mpf_style='yahoo', marketcolors=mc)
        
        self.fig = mpf.figure(figsize=(12,8), style=s)
        
        gs = GridSpec(4,1, figure=self.fig)
 
        self.ax = self.fig.add_subplot(gs[:3, 0])
        self.ax1 = self.fig.add_subplot(gs[3, 0], sharex=self.ax)
        
        self.ax1.yaxis.tick_right()
        self.ax1.yaxis.set_label_position("right")
        self.ax1.set_ylim(bottom=0, top=100)
        
        sf = df[['K', 'D']]
        aps = [
                mpf.make_addplot(sf['K'], ax=self.ax1, color='orange', width=1),
                mpf.make_addplot(sf['D'], ax=self.ax1, color='blue', width=1),
        ]
        mpf.plot(df, ax=self.ax, addplot=aps, xrotation=10, **kwargs)
        
        self.ax1.add_line(Line2D(self.ax1.get_xlim(), [80,80], color='r', linewidth=1))
        self.ax1.add_line(Line2D(self.ax1.get_xlim(), [20,20], color='g', linewidth=1))
        
        self.ax.tick_params('x', labelbottom=False)
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

        