##\package pingtrend
# \brief Simple tool to trend ping times
#
# Vegard Fiksdal (C) 2024
#

# Import QT modules
from PyQt6.QtWidgets import QApplication, QMainWindow, QSplitter, QTreeView, QFrame, QVBoxLayout, QScrollArea
from PyQt6.QtGui import QStandardItemModel, QStandardItem, QFont
from PyQt6.QtCore import Qt, QTimer
import sys

# Import local modules
from qpinger import *
from qplot import *
from qlog import *

# Simple identification
appversion='0.6.0'
appname='PingTrend'
pkgstring=appname+' '+appversion
aboutstring=pkgstring+'\n'
aboutstring+='Simple tool to trend and log ping times\n'
aboutstring+='vegard@fiksdal.cc\n'

##\class StandardItem
# \brief Define how a standard treeview item should look like
class StandardItem(QStandardItem):
    ##\brief Configures StandardItem
    # \param txt Text to display
    # \param font_size Size of font
    # \param set_bold Wether to have bold font
    # \param color Color of the text
    def __init__(self, txt='', font_size=12, set_bold=False, color=None):
        super().__init__()
        if color!=None: self.setForeground(color)
        fnt = QFont('Open Sans', font_size)
        fnt.setBold(set_bold)
        self.setEditable(False)
        self.setFont(fnt)
        self.setText(txt)

##\class Frame
# \brief Holds a selectable frame
class Frame():
    ##\brief Configures StandardItem
    # \param object Frame object
    # \param label Frame label
    def __init__(self,object,label):
        self.object=object
        self.label=label
        self.item=StandardItem(label)
        object.setVisible(False)

##\class MainWindow
# \brief Main Application class
class MainWindow(QMainWindow):
    def __init__(self,parent=None):
        super(MainWindow,self).__init__(parent)
        # Create panels
        self.pinger=QPinger()
        self.trend=QStyledPlot('Ping Trend','Measurement time','Response time (ms)')
        self.log=QLog()
        self.frames=[]
        self.frames.append(Frame(self.pinger,'Config'))
        self.frames.append(Frame(self.trend,'Trend'))
        self.frames.append(Frame(self.log,'Log'))

        # Present application info
        for string in aboutstring.split('\n'):
            self.log.addText(string)
        self.log.addText('')

        # Build treeview
        self.treeview=QTreeView()
        self.treeview.setHeaderHidden(True)
        treemodel=QStandardItemModel()
        rootnode=treemodel.invisibleRootItem()
        for frame in self.frames:
            rootnode.appendRow(frame.item)

        # Wrap up treeview
        self.treeview.setModel(treemodel)
        self.treeview.expandAll()
        self.treeview.clicked.connect(self.TreeviewClick)
        index=treemodel.indexFromItem(self.frames[0].item)
        self.treeview.setCurrentIndex(index)
        self.frames[0].object.setVisible(True)

        # Use a timer to process data from the queue
        self.timer=QTimer()
        self.timer.timeout.connect(self.Process)
        self.timer.start(100)

        # Show window
        layout=QVBoxLayout()
        widget=QFrame()
        scrollarea=QScrollArea()
        for frame in self.frames:
            layout.addWidget(frame.object)
        widget.setLayout(layout)
        scrollarea.setWidgetResizable(True)
        scrollarea.setWidget(widget)
        splitter=QSplitter(Qt.Orientation.Horizontal)
        splitter.addWidget(self.treeview)
        splitter.addWidget(scrollarea)
        splitter.setSizes([100,600])
        self.setCentralWidget(splitter)
        self.setWindowTitle(pkgstring)
        self.resize(800,600)
        self.showMaximized()

    ##\brief Stop background processes upon terminating the application
    # \param event Not used
    def closeEvent(self, event):
        #self.timer.stop()
        super().close()

    ##\brief Respond to user clicking on the treeview
    # \param Value The clicked item
    def TreeviewClick(self,Value):
        # Show/hide dynamic panels
        title=Value.data()
        for frame in self.frames:
            frame.object.setVisible(title==frame.label)

    ##\brief Timer event to update plots
    def Process(self):
        # Update pinger
        xdata,ydata,legend=self.pinger.updatePing()

        # Update plot
        if self.trend.mplstyle!=self.pinger.ctrl_style.combo.currentText():
            self.trend.setStyle(self.pinger.ctrl_style.combo.currentText())
        if xdata!=None:
            self.trend.plotXY(xdata,ydata,legend)

        # Update logger
        self.log.updateLog()

# Start application
if __name__ == "__main__":
    app=QApplication(sys.argv)
    window=MainWindow()
    app.exec()

