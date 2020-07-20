#############################################################################
##
## TASK LIST:
## 
## First we need a UI:
## - User should see a live cam feed
## - User should see a preview of processed images 
## - The app should contain a toolbox that helps them manage
##   camera settings, Image processing functions and anything
##   else they need
##
## Then we need to write functions that do tings :)
## - Face morph
## - Infrared (Detect fevers - especially useful considering Covid)
## - Malinoma detection? How? Detect blemishes on skin? Chris?
## - Aging process?
## 
## Things I'd do with infinite resources / time:
## - Mount the camera to a robotic arm - have it auto detect best pos.
## - Use a point cloud camera - 3D scan of face
## - Apply above processes in 3D
##
## To accomplish the above I will be making heavy use of 2 core packages. 
## PyQt5 to handle GUI and OpenCV to handle image processing.
## Both are well known and updated regularly. 
##
## Listing the resources I'm using for Academic integrity
## UI:
## PyQt5 Source code & tools: https://riverbankcomputing.com/software/pyqt/download5
## Qt docs: https://doc.qt.io/qt-5/index.html
## This will be all I need to use for GUI as 99% of everything else on the internet
## that tries to use & explain the PyQt package isn't coded too well
##
#############################################################################


import sys, os
import cv2
from PyQt5.QtCore import Qt, QByteArray, qFuzzyCompare, QTimer
from PyQt5.QtMultimedia import (QAudioEncoderSettings, QCamera,
        QCameraImageCapture, QImageEncoderSettings, QMediaMetaData,
        QMediaRecorder, QMultimedia, QVideoEncoderSettings)
from PyQt5.QtWidgets import (QAction, QActionGroup, QApplication, QDialog,
        QMainWindow, QMessageBox)
from PyQt5.uic import loadUi
from PyQt5.QtGui import QImage, QPalette, QPixmap

# First we want to get current path. 
# Will be needed for cross platform purposes
def getCurrentPath():
    if getattr(sys, 'frozen', False):
        return os.path.dirname(sys.executable)
    else:
        return os.path.dirname(os.path.abspath(__file__))

# Load UI
current_path = getCurrentPath()
uiMainApp = os.path.join(current_path,"BetterMain.ui")

class MainWindow(QMainWindow):

    def __init__(self, parent=None):
        super(MainWindow, self).__init__(parent)

        loadUi(uiMainApp, self)

        # Set title
        self.setWindowTitle("Face Morph tool")

        # We need to know what devices exist so..
        # Placeholder for available devices:
        camDevices = QByteArray()
        # Set this as an exclusive group (only one can be enabled at a time)
        camDevicesGroup = QActionGroup(self) # setExclusive(True) is default

        for devices in QCamera.availableDevices():
            deviceName = QCamera.deviceDescription(devices)
            deviceObject = QAction(deviceName, camDevicesGroup)
            deviceObject.setCheckable(True)
            deviceObject.setChecked(True)
            deviceObject.setData(devices)
            
            if camDevices.isEmpty():
                # QCamera.availableDevices() will return an empty object so..
                camDevices = devices
                deviceObject.setCheckable(True)
            
            # Add devices to the 'Devices' Menu
            self.menuDevices.addAction(deviceObject)
        
        # If we switch devices we want to refresh the feed:
        camDevicesGroup.triggered.connect(self.refreshCamDevice)

        # Start cam feed:
        self.initCam(camDevices)

    def initCam(self, camDevices):
        # If no device exists, object will be invalid so..
        if camDevices.isEmpty():
            self.camera = QCamera()
        else:
            self.camera = QCamera(camDevices)

        # Enable / Disable UI elements based on whether cam is on or off
        self.camera.stateChanged.connect(self.updateCameraState)

        # Error handling
        self.camera.error.connect(self.displayCameraError)

        # Place the feed into ui element camFeed
        self.camera.setViewfinder(self.camFeed)

        # Set the capture mode to capture a video feed
        self.camera.setCaptureMode(QCamera.CaptureVideo)

        # Start the cam
        self.camera.start()

    # Little bit of error handling
    def displayCameraError(self):
        QMessageBox.warning(self, "Camera error", self.camera.errorString())

    # Enable/Disable UI features based on camera state
    def updateCameraState(self, state):
        if state == QCamera.ActiveState:
            self.actionStart_Camera.setEnabled(False)
            self.actionStop_Camera.setEnabled(True)
            self.userTools.setEnabled(True)
        elif state in (QCamera.UnloadedState, QCamera.LoadedState):
            self.actionStart_Camera.setEnabled(True)
            self.actionStop_Camera.setEnabled(False)
            self.userTools.setEnabled(False)
    
    # Refreshing status by re-running initCam with new action data
    def refreshCamDevice(self, action):
        self.initCam(action.data())

    # QOL shortcuts
    def keyPressEvent(self,keyEvent):
        if keyEvent.key() == Qt.Key_Escape:
            self.closeApp()
        elif keyEvent.key()==Qt.Key_F1:
            return

# Start App:
if __name__=='__main__':
    app = QApplication(sys.argv)
    qt_app = MainWindow()
    qt_app.show()
    app.exec_()





            