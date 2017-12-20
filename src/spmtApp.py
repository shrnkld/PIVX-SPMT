#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import sys
import os.path
from qt.dlg_configureRPCserver import ConfigureRPCserver_dlg
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))
from misc import getSPMTVersion, printDbg
from constants import starting_height, starting_width
from PyQt5.Qt import QMainWindow, QIcon, QAction
from mainWindow import MainWindow
import signal

class ServiceExit(Exception):
    """
    Custom exception which is used to trigger the clean exit
    of all running threads and the main program.
    """
    pass
 
 
def service_shutdown(signum, frame):
    print('Caught signal %d' % signum)
    raise ServiceExit



class App(QMainWindow):
 
    def __init__(self, masternode_list, imgDir):
        super().__init__()
        # Register the signal handlers
        signal.signal(signal.SIGTERM, service_shutdown)
        signal.signal(signal.SIGINT, service_shutdown)
    
        self.version = getSPMTVersion()
        self.title = 'SPMT - Secure Pivx Masternode Tool - v.%s-%s' % (self.version['number'], self.version['tag'])
        
        self.initUI(masternode_list, imgDir)
 
    def initUI(self, masternode_list, imgDir):
            
        self.setWindowTitle(self.title)
        self.resize(starting_width, starting_height)
        #self.setMinimumWidth(starting_width)
        #self.setMinimumHeight(starting_height)
        spmtIcon_file = os.path.join(imgDir, 'spmtLogo_shield.png')
        self.spmtIcon = QIcon(spmtIcon_file)
        self.setWindowIcon(self.spmtIcon)
        
        mainMenu = self.menuBar()
        confMenu = mainMenu.addMenu('Setup')
        self.rpcConfMenu = QAction(self.spmtIcon, 'Local RPC Server...', self)
        self.rpcConfMenu.triggered.connect(self.onEditRPCServer)
        confMenu.addAction(self.rpcConfMenu)
        
        masternode_list.sort(key=self.extract_name)
        
        self.mainWindow = MainWindow(self, masternode_list, imgDir)

        self.setCentralWidget(self.mainWindow)

        self.show()
        self.activateWindow()
        
    def extract_name(self, json):
        try:
            return json['name'].lower()
        except KeyError:
            return 0
        
        
        
    def closeEvent(self, *args, **kwargs):
        sys.stdout = sys.__stdout__
        sys.stderr = sys.__stderr__
        # Terminate the running threads.
        # Set the shutdown flag on each thread to trigger a clean shutdown of each thread.
        self.mainWindow.myRpcWd.shutdown_flag.set()

        print("Saving stuff & closing...")
        if getattr(self.mainWindow.hwdevice, 'dongle', None) is not None:
            self.mainWindow.hwdevice.dongle.close()
            print("Dongle closed")
        print("Bye Bye.")
        return QMainWindow.closeEvent(self, *args, **kwargs)
    
    
    
    def onEditRPCServer(self):
        # Create Dialog
        try:
            ui = ConfigureRPCserver_dlg(self)
            if ui.exec():
                printDbg("Configuring RPC Server...")
        except Exception as e:
            print(e)
