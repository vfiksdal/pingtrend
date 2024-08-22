##\package qlog
# \brief GUI logging output for QT6
#
# Vegard Fiksdal (C) 2024
#
from PyQt6.QtWidgets import QHBoxLayout, QVBoxLayout, QMessageBox, QFrame, QFileDialog, QListWidget, QComboBox, QPushButton
from PyQt6.QtGui import QFont
from PyQt6.QtCore import QTimer
import logging,datetime


##\class LogHandler
# \brief Custom logging handler for dynamic output handling
class LogHandler(logging.Handler):
    ## Reference to the output object (Falls back to print())
    output=None

    ## Effective log level to display
    level=logging.INFO

    ##\brief Initializes handler
    def __init__(self):
        super().__init__()
        #LogHandler.instance=self

    ##\brief Handle output
    # \param record Log record to handle
    def emit(self, record):
        if record.levelno>=LogHandler.level:
            if LogHandler.output:
                LogHandler.output.processLog(record)
            else:
                t=datetime.datetime.now().strftime('%c')
                msg='%s  %-*s %s' % (t,8,record.levelname,record.msg)
                print(msg)

##\class QLog
# \brief Frame to display realtime log output
class QLog(QFrame):
    ##\brief Constructor sets up frame layout
    def __init__(self):
        super().__init__()
        self.listbox=QListWidget()
        self.listbox.setFont(QFont('cascadia mono'))
        self.dropdown=QComboBox()
        self.clearbutton=QPushButton('Clear logs')
        self.clearbutton.clicked.connect(self.clear)
        self.savebutton=QPushButton('Save log to file')
        self.savebutton.clicked.connect(self.saveLog)
        self.messages=[]
        self.msgbox=True

        # Manage loglevels
        levels=['CRITICAL','ERROR','WARNING','INFO','DEBUG']
        level=3
        for i in range(len(levels)): self.dropdown.addItem(levels[i])
        self.dropdown.currentIndexChanged.connect(self.currentIndexChanged)
        self.dropdown.setCurrentIndex(level)

        # Add any controls to the layout
        layout=QVBoxLayout()
        layout.addWidget(self.listbox,1)
        layout.addWidget(self.dropdown)
        layout.addWidget(self.clearbutton)
        layout.addWidget(self.savebutton)
        layout.setContentsMargins(0,0,0,0)
        self.setLayout(layout)

        # Enable logging
        logging.basicConfig(level=logging.DEBUG,handlers=[LogHandler()])
        LogHandler.level=logging._nameToLevel['INFO']
        LogHandler.output=self

    ##\brief Called when loglevel has changed
    # \param index New loglevel
    def currentIndexChanged(self,index):
        levelname=self.dropdown.itemText(index)
        level=logging._nameToLevel[levelname]
        LogHandler.level=level

    ##\brief Clear existing log
    def clear(self):
        self.messages=[]
        self.listbox.clear()

    ##\brief Process messages from logger
    def processLog(self,message):
        self.messages.append(message)

    ##\brief Manually adds a text string
    # \param text Text string to add
    def addText(self,text):
        self.listbox.addItem(text)

    ##\brief Saves log output to file
    def saveLog(self):
        text=''
        for message in self.messages:
            text+=message+'\n'
        filename, _ = QFileDialog.getSaveFileName(self,'Save process log','mbserver.log','Log files(*.log);;All Files(*.*)',options=QFileDialog.Options())
        if filename:
            with open(filename, 'w') as f:
                f.write(text)
                f.close()

    ##\brief Show errors in a messagebox
    # \param show True to display messagebox for error messages
    #
    # This is useful when expecting errors otherwise presented to the user. eg polling.
    def showMessagebox(self,show):
        self.msgbox=show

    ##\brief Updates GUI with added messages
    def updateLog(self):
        messages=self.messages
        self.messages=[]
        for message in messages:
            if self.msgbox and (message.levelno==logging.ERROR or message.levelno==logging.CRITICAL):
                QMessageBox.critical(self,message.module,str(message.msg))
            s='%s  %-*s %s' % (datetime.datetime.now().strftime('%c'),8,message.levelname,message.msg)
            self.listbox.addItem(s)
        if len(messages):
            self.listbox.scrollToBottom()

