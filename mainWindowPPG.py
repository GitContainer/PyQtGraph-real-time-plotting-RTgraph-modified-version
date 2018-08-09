"""
Basic example to plot data from a function in real time
Created on Thu Dec 21 12:07:49 2017
by the author: Kevin Machado Gamboa
Contct: ing.kevin@hotmail.com
Modified on Sat Jan 06 08:50:23 2018
Ref1: https://github.com/ssepulveda
Ref2: https://github.com/ssepulveda/RTGraph/tree/oldRTGraph
Ref3: https://github.com/LatinAmericanProgramer/PyQtGraph-real-time-plotting-RTgraph-modified-version
"""
import sys
from PyQt5 import QtWidgets, QtCore
from PyQt5.uic import loadUi
from PyQt5.QtWidgets import QApplication, QMainWindow
from pyqtgraph import GraphicsLayoutWidget
from multiprocessing import Queue
from collections import deque

from time import time
import numpy as np


##
# @brief Buffer size for the data (number of points in the plot)
N_SAMPLES = 100
##s
# @brief Point to update in each redrawIR
PLOT_UPDATE_POINTS = -2

class mainWindow(QMainWindow):
        # Metodo constructor de la clase
    def __init__(self):
        #Inicia el objeto QMainWindow
        QMainWindow.__init__(self)
        #carga la configuracion del archivo .ui en el objeto
        loadUi("mainWindowPPG.ui",self)
        # Loads everything about mainWindowPPG configuration
        self.setupUI()
        # Shared variables, initial values
        self.queue = Queue(N_SAMPLES)
        self.dataR = deque([], maxlen=N_SAMPLES)
        self.dataIR = deque([], maxlen=N_SAMPLES)
        self.TIME = deque([], maxlen=N_SAMPLES)
        self._plt = None
        self._timer_plot = None
        self.plot_colors = ['#0072bd', '#d95319']
        # configures
        self._configure_plot()
        self._configure_timers()
        self._configure_signals()

# Loads everything about mainWindowPPG configuration        
    def setupUI(self):
        """
       Configures everything about the mainWindow
        """
        self.plt = GraphicsLayoutWidget(self.centralwidget) # Bringing my plot wiindow as plt
        self.plt.setAutoFillBackground(False)
        self.plt.setStyleSheet("border: 0px;")
        self.plt.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.plt.setFrameShadow(QtWidgets.QFrame.Plain)
        self.plt.setLineWidth(0)
        self.Layout_graphs.addWidget(self.plt, 0, 0, 1, 1) # Set the plotting squared graph
    
    def _configure_plot(self):
        """
        Configures specific elements of the PyQtGraph plots.
        :return:
        """
        self.plt.setBackground(background=None)
        self.plt.setAntialiasing(True)
        self._plt = self.plt.addPlot(row=1, col=1)
        self._plt.setLabel('bottom', "Time", "s")
        pass
    
    def _configure_timers(self):
        """
        Configures specific elements of the QTimers.
        :return:
        """
        self._timer_plot = QtCore.QTimer(self) # gives _timer_plot the attribute of QtCore.QTimer
        self._timer_plot.timeout.connect(self._update_plot)  # connects with _update_plot method  
        pass
    
    def _update_plot(self):
        """
        Updates and redraws the graphics in the plot.
        This function us connected to the timeout signal of a QTimer.
        :return:
        """
        # Spo2 signal parameters
        f=2
        amp1 = 0.5       # amplitud for Sine signal
        zeroDes1 = 0.5413   # Desplacement from zero for Sine signal
        amp2 = 0.5       # amplitud for Cosine signal
        zeroDes2 = 1.5413   # Desplacement from zero for Cosine signal
        # generate the time
        tsignal = time() - self.timestamp
        # Sine signal function
        sR= zeroDes1 + amp1 * 0.8 *np.sin(2*np.pi*tsignal*3*f)
        # Cosine signal function
        sIR= zeroDes2 + amp2 * 0.8 *np.cos(2*np.pi*tsignal*3*f)
        # put the data generate (time & signal) into queue
        self.queue.put([tsignal,sR,sIR])
        # get the data generate into queue
        data = self.queue.get(True, 1)
        # store data into variables 
        self.TIME.append(data[0])
        self.dataR.append(data[1])
        self.dataIR.append(data[2])
        # Draw new data
        self._plt.clear()
        self._plt.plot(x=list(self.TIME)[-PLOT_UPDATE_POINTS:], y=list(self.dataR)[-PLOT_UPDATE_POINTS:], pen=self.plot_colors[1])
        self._plt.plot(x=list(self.TIME)[-PLOT_UPDATE_POINTS:], y=list(self.dataIR)[-PLOT_UPDATE_POINTS:], pen=self.plot_colors[0])
    
    def _configure_signals(self):
        """
        Configures the connections between signals and UI elements.
        :return:
        """
        self.startButton.clicked.connect(self.start)
        self.stopButton.clicked.connect(self.stop)

    def start(self):
        """
        Starts the acquisition of the selected serial port.
        This function is connected to the clicked signal of the Start button.
        :return:
        """
        self.timestamp= time()
        self._timer_plot.start(16)
        
    def stop(self):
        """
        Stops the acquisition of the selected serial port.
        This function is connected to the clicked signal of the Stop button.
        :return:
        """
        self._timer_plot.stop()  # stop the Qt timer
        self.reset_buffers()     # Go to reset the vector containing values
    
    def reset_buffers(self):
        self.dataR.clear()
        self.dataIR.clear()
        self.TIME.clear()
  
#Instancia para iniciar una aplicacion en windows
app = QApplication(sys.argv)
#debemos crear un objeto para la clase creada arriba
_mainWindow = mainWindow()
    #muestra la ventana
_mainWindow.show()
    #ejecutar la aplicacion
app.exec_()