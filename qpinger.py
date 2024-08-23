##\package logframe
# \brief Frame for pinging
#
# Vegard Fiksdal (C) 2024
#
from PyQt6.QtWidgets import QGroupBox,QCheckBox, QPushButton, QHBoxLayout, QVBoxLayout, QLabel, QFrame, QLineEdit, QFileDialog, QComboBox
from PyQt6.QtCore import Qt,QTimer
from datetime import datetime
import time,logging,os,socket,ping3,netifaces,json

##\class ConfigBox
# \brief Class to display a label + edit control for simple configuration
class ConfigBox(QFrame):
    ##\brief Constructor sets default values
    # \param label Textual description to be displayed in label
    # \param text Default value to be displayed in editbox
    # \param callback Optional function to be called upon value changes
    # \param locked Sets value to be read-only
    def __init__(self,label,text='0',callback=None,locked=False):
        super().__init__()
        self.label=QLabel(label)
        self.edit=QLineEdit(str(text))
        self.edit.setEnabled(not locked)
        layout=QHBoxLayout()
        layout.addWidget(self.label,1)
        layout.addWidget(self.edit,1)
        layout.setContentsMargins(0,0,0,0)
        self.setLayout(layout)
        if callback:
            self.edit.textChanged.connect(callback)

    ##\brief Get current value
    # \param Fallback Value to use if value was invalid
    # \return Current value as a floating point number
    def GetValue(self,Fallback):
        try:
            value=float(self.edit.text())
            self.edit.setStyleSheet("")
        except:
            self.edit.setStyleSheet("background-color: rgb(255,50,50);")
            value=Fallback
        return value
    
##\class ComboBox
# \brief Class to display a label + combo control for simple configuration
class ComboBox(QFrame):
    ##\brief Constructor sets default values
    # \param label Textual description to be displayed in label
    # \param text Default value to be displayed in editbox
    # \param callback Optional function to be called upon value changes
    # \param locked Sets value to be read-only
    def __init__(self,label,locked=False):
        super().__init__()
        self.label=QLabel(label)
        self.combo=QComboBox()
        self.combo.setEnabled(not locked)
        layout=QHBoxLayout()
        layout.addWidget(self.label,1)
        layout.addWidget(self.combo,1)
        layout.setContentsMargins(0,0,0,0)
        self.setLayout(layout)

##\class BrowseBox
# \brief Class to display a label + edit control + browse button to set paths
class BrowseBox(QFrame):
    def __init__(self,label,text=os.getcwd(),locked=False):
        super().__init__()
        self.label=QLabel(label)
        self.edit=QLineEdit(str(text))
        self.button=QPushButton('...')
        self.edit.setEnabled(not locked)
        self.button.setEnabled(not locked)
        self.button.clicked.connect(self.browse)
        layout=QHBoxLayout()
        ilayout=QHBoxLayout()
        ilayout.addWidget(self.edit,1)
        ilayout.addWidget(self.button)
        layout.addWidget(self.label,1)
        layout.addLayout(ilayout,1)
        layout.setContentsMargins(0,0,0,0)
        self.setLayout(layout)

    ##\brief Opens a file dialog to set the path visually
    def browse(self):
        folder = str(QFileDialog.getExistingDirectory(self, "Select Output"))
        if len(folder): self.edit.setText(str(folder))

##\class PingItemBox
# \brief Class to display and hold a target for logging
class PingItemBox(QFrame):
    def __init__(self):
        super().__init__()
        # Load controls
        self.name=QLineEdit()
        self.address=QLineEdit()
        self.button=QPushButton()
        namelabel=QLabel('Name: ')
        adrlabel=QLabel('IP Address: ')
        namelabel.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
        adrlabel.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
        layout=QHBoxLayout()
        layout.addWidget(namelabel)
        layout.addWidget(self.name,1)
        layout.addWidget(adrlabel)
        layout.addWidget(self.address,1)
        layout.addWidget(QLabel(''),1)
        layout.addWidget(self.button,1)
        layout.setContentsMargins(0,0,0,0)
        self.setLayout(layout)

        # Set default results
        self.result=None

##\class PingItems
# \brief Class to manage PingItemBox instances
class PingItems(QFrame):
    def __init__(self):
        super().__init__()
        self.ilayout=QVBoxLayout()
        self.ilayout.setContentsMargins(0,0,0,0)
        self.setLayout(self.ilayout)
        self.items=[]

    ##\brief Counts the number of items
    # \return Number of items loaded
    def count(self):
        return len(self.items)

    ##\brief Remove all items
    def clear(self):
        for item in self.items:
            self.remItem(item)
            self.clear()

    ##\brief Find an item from the pressed button object
    # \param button The button object that issued the original event
    # \return PingItemBox instance associated with the button, or None upon failure
    def findItem(self,button):
        for item in self.items:
            if item.button==button:
                return item
        return None
    
    ##\brief Parse an item into address and channels
    # \param index Index of the item to parse
    # \return address, ultrasound channel, temperature channel as tuple
    def parseItem(self,index):
        item=self.items[index]
        name=item.name.text()
        address=item.address.text()
        return name,address

    ##\brief Add a PingItemBox instance
    # \param item Object to add
    def addItem(self,item):
        self.items.append(item)
        self.ilayout.addWidget(item)

    ##\brief Remove a PingItemBox instance
    # \param item Object to remove
    def remItem(self,item):
        self.items.remove(item)
        self.ilayout.removeWidget(item)

##\class QPinger
# \brief Frame to present the logging options visually
class QPinger(QFrame):
    ##\brief Constructor sets layout and creates necessary objects
    # \param Label Name of the frame
    def __init__(self,):
        super().__init__()
        # Add plots
        layout=QVBoxLayout()
        pinglayout=QVBoxLayout()
        ctrllayout=QHBoxLayout()
        self.xdata=[]
        self.ydata=[]
        self.legend=[]
        self.dataflag=False

        # Load ping items
        self.cfg_items=PingItems()
        cfg_layout=QVBoxLayout()
        self.cfg_group=QGroupBox('Ping items')
        self.cfg_newitem=PingItemBox()
        self.cfg_newitem.button.setText('Add')
        self.cfg_newitem.button.clicked.connect(self.addItem)
        self.cfg_newitem.address.editingFinished.connect(self.addressChanged)
        self.cfg_newitem.name.editingFinished.connect(self.nameChanged)
        self.cfg_group.setLayout(cfg_layout)
        cfg_layout.addWidget(self.cfg_items)
        cfg_layout.addWidget(QLabel(''),1)
        cfg_layout.addWidget(self.cfg_newitem)
        pinglayout.addWidget(self.cfg_group)

        # Add configuration controls
        ctrl_options=QHBoxLayout()
        opt_layout=QHBoxLayout()
        self.opt_label=QLabel('File writing options')
        self.opt_csv=QCheckBox('Write CSV files')
        opt_layout.addWidget(self.opt_csv,1)
        ctrl_options.addWidget(self.opt_label,1)
        ctrl_options.addLayout(opt_layout,1)
        #self.opt_csv.setChecked(True)
        ctrl_layout=QVBoxLayout()
        self.ctrl_group=QGroupBox('Ping settings')
        self.ctrl_interval=ConfigBox('Ping interval [s]',60)
        self.ctrl_filtertk=ConfigBox('Average over N samples (<=1 to disable)',4)
        self.ctrl_nsamples=ConfigBox('Number of samples in plot',100)
        self.ctrl_path=BrowseBox('Path for logged data')
        self.ctrl_style=ComboBox('Plot style')
        self.ctrl_load=QPushButton('Load configuration')
        self.ctrl_save=QPushButton('Save configuration')
        self.ctrl_start=QPushButton('Start pinging')
        self.ctrl_stop=QPushButton('Stop pinging')
        self.ctrl_load.clicked.connect(lambda: self.loadConfig(str(QFileDialog.getOpenFileName(self,'Load configuration','','Config file(*.cfg);;All Files(*.*)')[0])))
        self.ctrl_save.clicked.connect(lambda: self.saveConfig(str(QFileDialog.getSaveFileName(self,'Save configuration','','Config file(*.cfg);;All Files(*.*)')[0])))
        self.ctrl_start.clicked.connect(self.startPinging)
        self.ctrl_stop.clicked.connect(self.stopPinging)
        self.ctrl_group.setLayout(ctrl_layout)
        ctrl_layout.addWidget(self.ctrl_interval)
        ctrl_layout.addWidget(self.ctrl_filtertk)
        ctrl_layout.addWidget(self.ctrl_nsamples)
        ctrl_layout.addWidget(self.ctrl_style)
        ctrl_layout.addWidget(self.ctrl_path)
        ctrl_layout.addLayout(ctrl_options)
        ctrl_layout.addWidget(self.ctrl_load)
        ctrl_layout.addWidget(self.ctrl_save)
        ctrllayout.addWidget(self.ctrl_group)
        self.ctrl_style.combo.addItem('default')
        self.ctrl_style.combo.addItem('classic')
        self.ctrl_style.combo.addItem('dark_background')
        self.ctrl_style.combo.setCurrentIndex(self.ctrl_style.combo.count()-1)

        # Wrap up dialog
        layout.addLayout(pinglayout,1)
        layout.addLayout(ctrllayout)
        layout.addWidget(self.ctrl_start)
        layout.addWidget(self.ctrl_stop)
        layout.setContentsMargins(0,0,0,0)
        self.setLayout(layout)

        # Add some default reference targets
        gw=netifaces.gateways()
        if 'default' in gw: self.addTarget('Gateway',gw['default'][netifaces.AF_INET][0])
        self.addTarget('Google','google.com')

        # Some simple runtime variables
        self.running=False
        self.next=0
        self.fd=None
        self.stopPinging()

    def loadConfig(self,filename):
        if len(filename)==0: return
        with open(filename,'r') as fd:
            config=fd.read()
        config=json.loads(config)
        try:
            self.ctrl_interval.edit.setText(str(config['settings']['interval']))
            self.ctrl_filtertk.edit.setText(str(config['settings']['filtertk']))
            self.ctrl_nsamples.edit.setText(str(config['settings']['nsamples']))
            self.ctrl_path.edit.setText(str(config['settings']['path']))
            self.ctrl_style.combo.setCurrentIndex(config['settings']['style'])
            self.cfg_items.clear()
            for target in config['targets']:
                self.addTarget(target[0],target[1])
        except Exception as e:
            logging.error('Failed to read configuration: '+str(e))

    def saveConfig(self,filename):
        if len(filename)==0: return
        config={}
        config['settings']={}
        config['settings']['interval']=int(self.ctrl_interval.GetValue(60))
        config['settings']['filtertk']=int(self.ctrl_filtertk.GetValue(4))
        config['settings']['nsamples']=int(self.ctrl_nsamples.GetValue(100))
        config['settings']['path']=self.ctrl_path.edit.text()
        config['settings']['style']=self.ctrl_style.combo.currentIndex()
        config['targets']=[]
        for index in range(len(self.cfg_items.items)):
            name,address=self.cfg_items.parseItem(index)
            config['targets'].append([name,address])
        config=json.dumps(config,indent=4)
        with open(filename,'w') as fd:
            fd.write(config)

    ##\brief Set name to address if empty
    def addressChanged(self):
        if self.cfg_newitem.name.text()=='':
            self.cfg_newitem.name.setText(self.cfg_newitem.address.text())

    ##\brief Set address to name if empty
    def nameChanged(self):
        if self.cfg_newitem.address.text()=='':
            self.cfg_newitem.address.setText(self.cfg_newitem.name.text())

    ##\brief Calculates next pinging slot
    # \return Next pinging slot in seconds
    def nextTimeout(self):
        now=time.time()
        return now+(self.interval-(now%self.interval))
    
    ##\brief Timer event to poll for next scheduled pinging
    def updatePing(self):
        if self.running and time.time()>=self.next:
            # Execute requests
            self.next=self.nextTimeout()
            for i in range(self.cfg_items.count()):
                item=self.cfg_items.items[i]
                item.result=ping3.ping(item.address.text())

            # Register values
            csv=str(datetime.now())
            self.xdata.append(datetime.now())
            while len(self.xdata)>self.nsamples: self.xdata=self.xdata[1:]
            for index in range(len(self.cfg_items.items)):
                item=self.cfg_items.items[index]
                result=item.result
                self.ydata[index].append(float('nan'))
                while len(self.ydata[index])>self.nsamples: self.ydata[index]=self.ydata[index][1:]
                if result==None:
                    logging.info(item.name.text()+': Reply from '+item.address.text()+' timed out')
                    csv+=',No reply'
                elif result==False:
                    logging.info(item.name.text()+': Could not resolve '+item.address.text())
                    csv+=',Cannot resolve'
                else:
                    result*=1000
                    if self.filteracc[index]==0: self.filteracc[index]=result
                    if self.filtertk>1: result=(self.filteracc[index]*(self.filtertk-1)+result)/self.filtertk
                    logging.debug(item.name.text()+': '+item.address.text()+' '+str(result)+'ms')
                    csv+=','+str(result)
                    self.ydata[index][-1]=result

            # Update CSV file
            if self.fd!=None:
                self.fd.write(csv+'\n')
                self.fd.flush()

            # Flag new data
            return self.xdata,self.ydata,self.legend

        # No new data
        return None,None,None

    ##\brief Stops timer and resets dialog
    def stopPinging(self):
        self.running=False
        self.cfg_group.setEnabled(True)
        self.ctrl_start.setEnabled(True)
        self.ctrl_stop.setEnabled(False)
        self.ctrl_group.setEnabled(True)
        if self.fd!=None: self.fd.close()
        self.fd=None

    ##\brief Starts timer and initiates log files
    def startPinging(self):
        # Check if there is anything to even do
        if self.cfg_items.count()==0:
            logging.error('No channels are slated for logging')
            return

        # Parse interval and offset.
        self.interval=self.ctrl_interval.GetValue(-1)
        if self.interval<=0:
            logging.error('Interval must be a numeric value greater than zero')
            return
        self.nsamples=self.ctrl_nsamples.GetValue(-1)
        if self.nsamples<0:
            logging.error('Number of samples must be a numeric value')
            return
        self.filtertk=self.ctrl_filtertk.GetValue(-1)
        if self.filtertk<0:
            logging.error('Filter Tk must be a numeric value')
            return


        # Prepare CSV file for writing
        if self.opt_csv.isChecked():
            folder=self.ctrl_path.getValue()+'/'
            filename=datetime.now().strftime('PingTrend - %Y%m%d %H%M%S')+'.csv'
            path=folder+filename
            try:
                self.fd = open(path,'w')
                csv='Time'
                for index in range(len(self.cfg_items.items)):
                    name,address=self.cfg_items.parseItem(index)
                    csv+=','+name
                self.fd.write(csv+'\n')
            except:
                logging.error('Could not open file for writing in '+path)
                return

        # Unset dataseries
        self.xdata=[]
        self.ydata=[]
        self.legend=[]
        self.filteracc=[]
        for i in range(len(self.cfg_items.items)):
            name,address=self.cfg_items.parseItem(i)
            self.ydata.append([])
            self.filteracc.append(0.0)
            self.legend.append(name+' ['+address+']')

        # Set UI state
        self.cfg_group.setEnabled(False)
        self.ctrl_start.setEnabled(False)
        self.ctrl_stop.setEnabled(True)
        self.ctrl_group.setEnabled(False)
        self.running=True
        self.next=0

    ##\brief Adds an target to be logged
    # \param name Name of ping target
    # \param address Address of ping target
    def addTarget(self,name,address):
        oldname=self.cfg_newitem.name.text()
        oldaddress=self.cfg_newitem.address.text()
        self.cfg_newitem.name.setText(name)
        self.cfg_newitem.address.setText(address)
        self.addItem()
        self.cfg_newitem.name.setText(oldname)
        self.cfg_newitem.address.setText(oldaddress)

    ##\brief Adds an item to be logged
    def addItem(self):
        # Validate inputs
        if len(self.cfg_newitem.name.text())==0:
            logging.error('No name given!')
            return
        if len(self.cfg_newitem.address.text())==0:
            logging.error('No address given!')
            return
        try:
            address=socket.gethostbyname(self.cfg_newitem.address.text())
            self.cfg_newitem.address.setText(address)
        except Exception as e:
            logging.error('Invalid address: '+str(e))
            return
        
        # Create a new item with the current settings
        newitem=PingItemBox()
        newitem.name.setText(self.cfg_newitem.name.text())
        newitem.address.setText(self.cfg_newitem.address.text())
        newitem.name.setEnabled(False)
        newitem.address.setEnabled(False)
        newitem.button.setText('Remove')
        newitem.button.clicked.connect(self.remItem)
        self.cfg_items.addItem(newitem)

        # Clear configuration item
        self.cfg_newitem.name.setText('')
        self.cfg_newitem.address.setText('')

    ##\brief Removes an item from the logging schedule
    def remItem(self):
        item=self.sender()
        item=self.cfg_items.findItem(item)
        if item!=None: self.cfg_items.remItem(item)

