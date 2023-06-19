import sys
import matplotlib.pyplot as plt
from matplotlib.axes import Axes
from matplotlib.lines import Line2D
import matplotlib.transforms as transforms
from matplotlib.artist import Artist
import sys


class TLine(Line2D):

    def __init__(self, ax: Axes, x, y, color='red'):
        super().__init__([x,x], [y,y], color=color, picker=5)
        self.startX = x
        self.startY = y
        self.ax = ax
        self.c = ax.get_figure().canvas
        self.follower2pt=self.c.mpl_connect(
            "motion_notify_event", self.followmouseforsecondpt)
        
    def followmouseforsecondpt(self, event):
        x=event.xdata
        y=event.ydata
        if (y is None) or (x is None):
            return
        self.set_xdata([self.startX, x])
        self.set_ydata([self.startY, y])
        self.c.draw_idle()     
        
    def secondPtAdded(self):
        self.c.mpl_disconnect(self.follower2pt)
        self.sid = self.c.mpl_connect('pick_event', self.clickonline)

    def clickonline(self, event):
        sys.stdout.flush()
        if event.artist == self:
            button = event.mouseevent.button
            if button == 1:
                self.ends_x = self.get_xdata()
                self.ends_y = self.get_ydata()
                self.orig_mx = event.mouseevent.xdata
                self.orig_my = event.mouseevent.ydata
                self.follower=self.c.mpl_connect(
                    "motion_notify_event", self.followmouseformove)
                self.releaser=self.c.mpl_connect(
                    "button_press_event", self.releaseonclick)
            else:
                self.remove()
                self.c.draw_idle()

    def followmouseformove(self, event):
        x=event.xdata
        y=event.ydata
        if (y is None) or (x is None):
            return
        dx = x - self.orig_mx    
        dy = y - self.orig_my    
        newx = [ax + dx for ax in self.ends_x]   
        newy = [ay + dy for ay in self.ends_y]   
        self.set_xdata(newx)
        self.set_ydata(newy)
        self.c.draw_idle()

    def releaseonclick(self, event):
        self.c.mpl_disconnect(self.releaser)
        self.c.mpl_disconnect(self.follower)

class Hline(Line2D):

    def __init__(self, ax: Axes, y: float, ticker, lineclass, color, moveable=True):
        super().__init__(ax.get_xlim(), [y, y], color=color, picker=5)
        
        self.moveable=moveable
        self.lineclass = lineclass
        self.ticker = ticker
        self.ax=ax
        self.c=ax.get_figure().canvas
        self.sid=self.c.mpl_connect('pick_event', self.clickonline)

        trans=transforms.blended_transform_factory(
            ax.transAxes, ax.transData)
        self.txtclass=ax.text(0, y, f'{lineclass}', c=color, transform=trans, horizontalalignment='left',
            verticalalignment='bottom')
        self.txtloc=ax.text(1, y, f'{y:.2f}', c=color, transform=trans, horizontalalignment='right',
            verticalalignment='bottom')

    def clickonline(self, event):
        if not self.moveable:
            return
        if event.artist == self:
            button=event.mouseevent.button
            if button == 1:
                self.follower=self.c.mpl_connect(
                    "motion_notify_event", self.followmouse)
                self.releaser=self.c.mpl_connect(
                    "button_press_event", self.releaseonclick)
            else:
                self.removeLine()
                
    def removeLine(self):
        self.remove()
        Artist.remove(self.txtloc)
        Artist.remove(self.txtclass)
        self.c.draw_idle()
        match self.lineclass:
            case 'Target':
                self.ticker.target_line = None
            case 'Stop':
                self.ticker.stop_line = None


    def followmouse(self, event):
        y=event.ydata
        if y is None:
            return
        self.moveline(y)
        
    def moveline(self, y):
        self.set_ydata([y, y])
        self.txtclass.set_y(y)
        self.txtloc.set_y(y)
        self.txtloc.set_text(f'{y:.2f}')
        self.c.draw_idle()

    def releaseonclick(self, event):
        self.c.mpl_disconnect(self.releaser)
        self.c.mpl_disconnect(self.follower)

