##\package qplot
# \brief Class for using matplotlib in QT6
#
# Vegard Fiksdal (C) 2024
#

## Import Matplotlib and QT modules
from PyQt6.QtWidgets import QFrame, QHBoxLayout
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
from mplcursors import cursor
import matplotlib.pyplot as plt
import logging

##\class QPlot
# \brief QT control to embed a matplotlib figure
class QPlot(FigureCanvas):
    ##\brief Constructor to configure the plot object
    # \param title Plot title
    # \param xtitle Plot x-axis annotation
    # \param ytitle Plot y-axis annotation
    # \param xfmt Formatter for x-axis
    # \param yfmt Formatter for y-axis
    # \param xlimit Min-max tuple to set fixed scaling on x-axis
    # \param ylimit Min-max tuple to set fixed scaling on y-axis
    def __init__(self,title='',xtitle='',ytitle='',xfmt=None,yfmt=None,xlimit=None,ylimit=None):
        fig = Figure()
        self.axes = fig.add_subplot(111)
        self.axes.format_coord=lambda x,y: f"x={x:.4f}, y={y:.4f}"
        fig.set_tight_layout(True)
        self.setData([],[],None,None,None)
        self.title=title
        self.xtitle=xtitle
        self.ytitle=ytitle
        self.xfmt=xfmt
        self.yfmt=yfmt
        self.xlimit=xlimit
        self.ylimit=ylimit
        self.style=''
        super(QPlot, self).__init__(fig)

    ##\brief Registers current dataset for export
    # \param xdata Dataset for x-axis
    # \param ydata Dataset for y-axis
    # \param legend List of legend entries (Can be None)
    # \param hlines List of horizontal lines (Can be None)
    # \param vlines List of vertical lines (Can be None)
    def setData(self,xdata,ydata,legend,hlines,vlines):
        self.xdata=xdata
        self.ydata=ydata
        self.legend=legend
        self.hlines=hlines
        self.vlines=vlines

    ##\brief Renders a plot of the current dataset
    # \param renderer Plot object to render with
    def renderPlot(self,renderer):
        renderer.ticklabel_format(style='plain',useOffset=False,axis='both')
        if self.legend:
            [renderer.plot(self.xdata,self.ydata[i],label=self.legend[i]) for i in range(len(self.ydata))]
            renderer.legend(loc='upper right')
        else:
            [renderer.plot(self.xdata,self.ydata[i]) for i in range(len(self.ydata))]
        if self.vlines: [renderer.axvline(l,color='red',linestyle='--',linewidth=1) for l in self.vlines]
        if self.hlines: [renderer.axhline(l,color='red',linestyle='--',linewidth=1) for l in self.hlines]
        renderer.grid()

    ##\brief Handles doubleclicks to plot current dataset in another window
    # \param event Not used
    def mouseDoubleClickEvent(self,event):
        try:
            plt.ion()
            self.renderPlot(plt)
            if len(self.title):  plt.title(self.title)
            if len(self.xtitle): plt.xlabel(self.xtitle)
            if len(self.ytitle): plt.ylabel(self.ytitle)
            plt.show()
        except Exception as e:
            logging.error('Failed to open interactive plot:\n'+str(e))
            plt.ioff()

    ##\brief Plots a dataset using Y-axis data
    # \param data Dataset for y-axis
    # \param xfunc Lambda to calculate x-axis data from y-axis indexes
    # \param legend List of legend entries (Can be None)
    # \param hlines List of horizontal lines (Can be None)
    # \param vlines List of vertical lines (Can be None)
    def plotY(self,data,xfunc=lambda x:x,legend=None,hlines=None,vlines=None):
        self.plotXY([xfunc(v) for v in range(len(data[0]))],data,legend,hlines,vlines)

    ##\brief Plots a dataset
    # \param xdata Dataset for x-axis
    # \param ydata Dataset for y-axis
    # \param legend List of legend entries (Can be None)
    # \param hlines List of horizontal lines (Can be None)
    # \param vlines List of vertical lines (Can be None)
    def plotXY(self,xdata,ydata,legend=None,hlines=None,vlines=None):
        self.setData(xdata,ydata,legend,hlines,vlines)
        self.axes.clear()
        self.renderPlot(self.axes)
        self.cursor=cursor(self.axes.get_lines(),hover=2)
        if self.xlimit!=None: self.axes.set_xlim(self.xlimit)
        if self.ylimit!=None: self.axes.set_ylim(self.ylimit)
        if self.xfmt: self.axes.xaxis.set_major_formatter(self.xfmt)
        if self.yfmt: self.axes.yaxis.set_major_formatter(self.yfmt)
        if len(self.title):  self.axes.set_title(self.title)
        if len(self.xtitle): self.axes.set_xlabel(self.xtitle)
        if len(self.ytitle): self.axes.set_ylabel(self.ytitle)
        try:
            self.draw()
        except Exception as error:
            logging.warning('Exception occurred while plotting: '+str(error))

    ##\brief Clear plot
    def clear(self):
        self.setData([],[],None,None,None)
        self.axes.clear()

##\class QStyledPlot
# \brief Component capable of reloading a plot with different styles
class QStyledPlot(QFrame):
    ##\brief Constructor to configure the plot object
    # \param title Plot title
    # \param xtitle Plot x-axis annotation
    # \param ytitle Plot y-axis annotation
    # \param xfmt Formatter for x-axis
    # \param yfmt Formatter for y-axis
    # \param xlimit Min-max tuple to set fixed scaling on x-axis
    # \param ylimit Min-max tuple to set fixed scaling on y-axis
    # \param mplstyle Matplotlib style to apply
    def __init__(self,title='',xtitle='',ytitle='',xfmt=None,yfmt=None,xlimit=None,ylimit=None,mplstyle='default'):
        super().__init__()
        plt.style.use(mplstyle)
        self.mplstyle=mplstyle
        self.plot=QPlot(title,xtitle,ytitle,xfmt,yfmt,xlimit,ylimit)
        self.wlayout=QHBoxLayout()
        self.wlayout.addWidget(self.plot,1)
        self.wlayout.setContentsMargins(0,0,0,0)
        self.setLayout(self.wlayout)

    def setStyle(self,mplstyle):
        # Load new plot
        plt.style.use(mplstyle)
        self.mplstyle=mplstyle
        p=self.plot
        p=QPlot(p.title,p.xtitle,p.ytitle,p.xfmt,p.yfmt,p.xlimit,p.ylimit)

        # Switch plots in layout
        self.wlayout.removeWidget(self.plot)
        self.wlayout.addWidget(p,1)
        self.plot=p

    ##\brief Registers current dataset for export
    # \param xdata Dataset for x-axis
    # \param ydata Dataset for y-axis
    # \param legend List of legend entries (Can be None)
    # \param hlines List of horizontal lines (Can be None)
    # \param vlines List of vertical lines (Can be None)
    def setData(self,xdata,ydata,legend,hlines,vlines):
        self.plot.setData(xdata,ydata,legend,hlines,vlines)

    ##\brief Renders a plot of the current dataset
    # \param renderer Plot object to render with
    def renderPlot(self,renderer):
        self.plot.renderPlot(renderer)

    ##\brief Handles doubleclicks to plot current dataset in another window
    # \param event Not used
    def mouseDoubleClickEvent(self,event):
        self.plot.mouseDoubleClickEvent(event)

    ##\brief Plots a dataset using Y-axis data
    # \param data Dataset for y-axis
    # \param xfunc Lambda to calculate x-axis data from y-axis indexes
    # \param legend List of legend entries (Can be None)
    # \param hlines List of horizontal lines (Can be None)
    # \param vlines List of vertical lines (Can be None)
    def plotY(self,data,xfunc=lambda x:x,legend=None,hlines=None,vlines=None):
        self.plot.plotY(data,xfunc,legend,hlines,vlines)

    ##\brief Plots a dataset
    # \param xdata Dataset for x-axis
    # \param ydata Dataset for y-axis
    # \param legend List of legend entries (Can be None)
    # \param hlines List of horizontal lines (Can be None)
    # \param vlines List of vertical lines (Can be None)
    def plotXY(self,xdata,ydata,legend=None,hlines=None,vlines=None):
        self.plot.plotXY(xdata,ydata,legend,hlines,vlines)

    ##\brief Clear plot
    def clear(self):
        self.plot.clear()
