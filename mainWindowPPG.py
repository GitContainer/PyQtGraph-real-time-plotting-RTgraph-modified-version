"""
Example to plot data from a function in real time
Ref: https://github.com/ssepulveda
Ref: https://github.com/ssepulveda/RTGraph/tree/oldRTGraph
Created on Thu Dec 21 12:07:49 2017
by the author: Kevin Machado Gamboa
Ref: https://github.com/LatinAmericanProgramer/PyQtGraph-real-time-plotting-RTgraph-modified-version
Contct: ing.kevin@hotmail.com
Modified on Sat Jan 06 08:50:23 2018
"""
import sys
import numpy as np
from time import time
from collections import deque
from multiprocessing import Queue
# Librery for the management of Qt v5. UI platform
from PyQt5.uic import loadUi
from PyQt5 import QtWidgets, QtCore
from PyQt5.QtWidgets import QApplication, QMainWindow, QSlider
# graphics and GUI library
from pyqtgraph import GraphicsLayoutWidget


# @brief Buffer size for the data (number of points in the plot)
N_SAMPLES = 100
# @brief Update time of the plot, in ms
PLOT_UPDATE_TIME = 1
# @brief Point to update in each redraw
PLOT_UPDATE_POINTS = -1

class mainWindow(QMainWindow):
    def __init__(self):
        #Inicia el objeto QMainWindow
        QMainWindow.__init__(self)
        # Loads an .ui file 
        loadUi("mainWindowPPG.ui",self)
        # Shared variables, initial values
        self.queue = Queue(N_SAMPLES)
        self.dataR = deque([], maxlen=N_SAMPLES)
        self.dataIR = deque([], maxlen=N_SAMPLES)
        self.TIME = deque([], maxlen=N_SAMPLES)
        
        self._plt = None
        self._timer_plot = None
        self.plot_colors = ['#0072bd', '#d95319']
        # Spo2 signal parameters
        self.timestamp = 0.0
        self.ampR = 1.0814       # amplitud for Red signal
        self.minR = 0.0   # Desplacement from zero for Red signal
        self.ampIR = 1.0814       # amplitud for InfraRed signal
        self.minIR = 1.0   # Desplacement from zero for Red signal
        # UI connectors
        self.HRBox.valueChanged.connect(self._initial)        
        self.spo2sl.valueChanged.connect(self.spo2sl_change)
        
        # Configurations
        self.setupUI()
        self._enable_ui(True)       
        self._configure_plot()
        self._configure_timers()
        self.buttons()
        self._initial()

    def start(self):
        """
        This function works when the start button is clicked
        It generates a t0 time and activates the Qt timer which connects to update_plot
        :return:
        """
        self._enable_ui(False)
        self.timestamp= time()
        self._timer_plot.start(PLOT_UPDATE_TIME)
        
    def stop(self):
        """
        This function works when the stop button is clicked
        it stop the timer and resets the buffers
        """
        self._enable_ui(True)
        self._timer_plot.stop()  
        self.reset_buffers()
    
    def _update_plot(self):
        """
        Updates and redraws the graphics in the plot.
        :return:
        """
        # generates the time
        self.tPPG = time() - self.timestamp
        self.sR, self.sIR = self.ppg_parameters(self.minR, self.ampR, self.minIR, self.ampIR, self.tPPG)
        self.queue.put([self.tPPG,self.sR,self.sIR])
        data = self.queue.get(True, 1)
        # store data into variables 
        self.TIME.append(data[0])
        self.dataR.append(data[1])
        self.dataIR.append(data[2])
        # Draw new data
        self._plt.clear()
        self._plt.plot(x=list(self.TIME)[-PLOT_UPDATE_POINTS:], y=list(self.dataR)[-PLOT_UPDATE_POINTS:], pen=self.plot_colors[1])
        self._plt.plot(x=list(self.TIME)[-PLOT_UPDATE_POINTS:], y=list(self.dataIR)[-PLOT_UPDATE_POINTS:], pen=self.plot_colors[0])
                
    def setupUI(self):
        """
       Configures everything regarding the UI
        """
        self.plt = GraphicsLayoutWidget(self.centralwidget)
        self.plt.setAutoFillBackground(False)
        self.plt.setStyleSheet("background-color: rgb(0,0,0)")
        self.plt.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.plt.setFrameShadow(QtWidgets.QFrame.Plain)
        self.plt.setLineWidth(0)
        self.Layout_graphs.addWidget(self.plt, 0, 0, 1, 1) # Set the plotting squared into UI graph
        # Defult Heart Rate Widget configuration
        self.HRBox.setRange(50,150)
        self.HRBox.setProperty("value", 80)
        # SpO2 Slider configuration
        self.spo2sl.setMaximum(100)
        self.spo2sl.setMinimum(50)
        self.spo2sl.setValue(100)
        self.spo2sl.setTickPosition(QSlider.TicksBelow)
        self.spo2sl.setTickInterval(1)
    
    def _configure_plot(self):
        """
        Configures specific elements of the PyQtGraph plots.
        :return:
        """
        self.plt.setBackground(background=None)
        self.plt.setAntialiasing(True)
        self._plt = self.plt.addPlot(row=1, col=1)
        self._plt.setLabel('bottom', "Time", "s")
        self._plt.showGrid(x=False, y=True)
    
    def _configure_timers(self):
        """
        Configures specific elements of the QTimers.
        :return:
        """
        self._timer_plot = QtCore.QTimer(self) # gives _timer_plot the attribute of QtCore.QTimer
        self._timer_plot.timeout.connect(self._update_plot)  # connects with _update_plot method  
    
    def ppg_parameters(self, minR, ampR, minIR, ampIR, t):
        """
        Store the function of two signals - e.g PPG Red and Infrared channel signals
        We can also put here a sine, cosine, etc.
        """
        # Spo2 signal parameters
        HR = float(self.HRBox.value())
        #speed=float(self.ui.cBox_Speed.currentText())
        f= HR * (1/60)
        # Spo2 Red signal function
        self.sR= minR + ampR * (0.05*np.sin(2*np.pi*t*3*f)
        + 0.4*np.sin(2*np.pi*t*f) + 0.25*np.sin(2*np.pi*t*2*f+45))
        # Spo2 InfraRed signal function
        self.sIR= minIR + ampIR * (0.05*np.sin(2*np.pi*t*3*f)
        + 0.4*np.sin(2*np.pi*t*f) + 0.25*np.sin(2*np.pi*t*2*f+45))
        
        return self.sR, self.sIR
    
    def _initial(self):
        """
        contain the initial figure in the UI
        """
        t=np.linspace(0,1,100);
        sR,sIR = self.ppg_parameters(self.minR, self.ampR, self.minIR, self.ampIR, t)

        self._plt.clear()
        self._plt.plot(x=list(t)[-PLOT_UPDATE_POINTS:], y=list(sR)[-PLOT_UPDATE_POINTS:], pen=self.plot_colors[1])
        self._plt.plot(x=list(t)[-PLOT_UPDATE_POINTS:], y=list(sIR)[-PLOT_UPDATE_POINTS:], pen=self.plot_colors[0])
    
    def spo2values(self):
        """
        It have the list of SpO2 values vs the R value
        """
        pass
    
    def buttons(self):
        """
        Configures the connections between signals and UI elements.
        """
        self.startButton.clicked.connect(self.start)
        self.stopButton.clicked.connect(self.stop)
    
    def reset_buffers(self):
        """
        Clear everything into the vectors that have the signals
        """
        self.dataR.clear()
        self.dataIR.clear()
        self.TIME.clear()
        
    def spo2sl_change(self):
        """
        Change the value of the SpO2 when movind the slider
        """
        spo2value = str(self.spo2sl.value())
        self.showSpo2.setText(spo2value)
        
    def _enable_ui(self, enabled):
        """
        Enable touching the buttons in the UI
        """
        self.startButton.setEnabled(enabled)
        self.spo2sl.setEnabled(enabled)
        self.showSpo2.setEnabled(enabled)
        self.HRBox.setEnabled(enabled)
        self.stopButton.setEnabled(not enabled)
        
#Instancia para iniciar una aplicacion en windows
app = QApplication(sys.argv)
#debemos crear un objeto para la clase creada arriba
_mainWindow = mainWindow()
    #muestra la ventana
_mainWindow.show()
    #ejecutar la aplicacion
app.exec_()
