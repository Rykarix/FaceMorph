import sys, os
import cv2
from PyQt5.QtCore import Qt, QByteArray, qFuzzyCompare, QTimer
from PyQt5.QtMultimedia import (QAudioEncoderSettings, QCamera,
        QCameraImageCapture, QImageEncoderSettings, QMediaMetaData,
        QMediaRecorder, QMultimedia, QVideoEncoderSettings)
from PyQt5.QtWidgets import (QAction, QActionGroup, QApplication, QDialog,
        QMainWindow, QMessageBox, QComboBox, QInputDialog, QDialogButtonBox)
from PyQt5.uic import loadUi
from PyQt5.QtGui import QImage, QPalette, QPixmap, QScreen
import traceback #Can be removed once fully functional
import numpy as np
import glob

# First we want to get current path. 
# Will be needed for cross platform purposes
def getCurrentPath():
    if getattr(sys, 'frozen', False):
        return os.path.dirname(sys.executable)
    else:
        return os.path.dirname(os.path.abspath(__file__))

# Handle errors as PyQt doesn't output them to console
sys._excepthook = sys.excepthook
def exception_hook(exctype, value, traceback):
    sys._excepthook(exctype, value, traceback)
    sys.exit(1)
sys.excepthook = exception_hook

def makeDirs():
    IMAGE_PATH = os.path.join( getCurrentPath() , "images" )
    TEMP_PATH = os.path.join( getCurrentPath() , "temp" )
    FACES_PATH = os.path.join( getCurrentPath() , "images" , "faces" )
    MORPHED_FINAL_PATH = os.path.join( getCurrentPath() , "images" , "final" )

    if not os.path.exists( IMAGE_PATH ):
        os.makedirs( IMAGE_PATH )
    if not os.path.exists( TEMP_PATH ):
        os.makedirs( TEMP_PATH )
    if not os.path.exists( FACES_PATH ):
        os.makedirs( FACES_PATH )
    if not os.path.exists( MORPHED_FINAL_PATH ):
        os.makedirs( MORPHED_FINAL_PATH )

# Load UI
makeDirs()
current_path = getCurrentPath()
uiMainApp = os.path.join(current_path,"BetterMain.ui")

class MainWindow(QMainWindow):

    def __init__(self, parent=None):
        super(MainWindow, self).__init__(parent)

        loadUi(uiMainApp, self)

        # Set title
        self.setWindowTitle("Face Morph tool")
        
        # Set initial vars
        self.cameraDevices = None # QArray of devices

        # Get devices:
        self.getCameraDevices()

        # Connect button sugnals
        self._connectSignals()

        # Set relevant actions

        # Start cam feed:
        self.initCam(self.cameraDevices)

    # Prevent users from trying to break the app
    def idiotchecker(self):
        if not self.dd_devices:
            return QMessageBox.about(self, "Error", "No device selected")
        else:
            return
    # Connecting buttons to functions:

    def _connectSignals(self):
        self.button_startcam.clicked.connect(self.startCamera)
        self.button_stopcam.clicked.connect(self.stopCamera)
        self.button_captureimage.clicked.connect(self.captureImage)
        self.button_addface.clicked.connect(self.addFace)
        self.button_updatelast.clicked.connect(self.updateLast)

    # Button Functions: Start Camera
    def startCamera(self):
        self.camera.start()
        self.camFeed.show()
        return

    # Button Functions: Stop Camera
    def stopCamera(self):
        self.camera.stop()
        self.camFeed.hide()
    
    # Button Functions: Capture image
    def imageCapture(self):
        self.capture
        return
    

    # Button Functions: Device dropdown
    def ddUpdate(self, deviceObject):
        # loop over camera devices and match deviceObject with str of item
        # then initCam(deviceObject.data())
        return self.initCam(deviceObject.data())

    def getCameraDevices(self):
        # We need to know what devices exist so..
        # Placeholder for available devices:
        self.cameraDevices = QByteArray()
        # Set this as an exclusive group (only one can be enabled at a time)
        camDevicesGroup = QActionGroup(self) # setExclusive(True) is default

        for devices in QCamera.availableDevices():
            deviceName = QCamera.deviceDescription(devices)
            deviceObject = QAction(deviceName, camDevicesGroup)
            deviceObject.setCheckable(True)
            deviceObject.setData(devices)
            
            # If no devices, QCamera.availableDevices() will return an empty object so..
            if self.cameraDevices.isEmpty():
                self.cameraDevices = devices
                deviceObject.setChecked(True)
            
            # Add devices to the 'Devices' Menu
            self.menuDevices.addAction(deviceObject)
            #self.dd_devices.addItem(deviceName)
            #self.dd_devices.addAction(deviceObject)

        # If we switch devices we want to refresh the feed:
        camDevicesGroup.triggered.connect(self.refreshCamDevice)

    def initCam(self, cameraDevices):
        # If no device exists, object will be invalid so..

        ##
        ## Camera Feed related
        ##
        if cameraDevices.isEmpty():
            self.camera = QCamera()
        else:
            self.camera = QCamera(cameraDevices)

        # Enable / Disable UI elements based on whether cam is on or off
        self.camera.stateChanged.connect(self.updateCameraState)

        # Error handling
        self.camera.error.connect(self.displayCameraError)

        # Place the feed into ui element camFeed
        self.camera.setViewfinder(self.camFeed)

        # Set the capture mode to capture a video feed
        self.camera.setCaptureMode(QCamera.CaptureVideo)

        ##
        ## Image capture related
        ##

        self.capture = QCameraImageCapture(self.camera)
        self.capture.imageCaptured.connect(self.processImage)

        # When image is captured, display it in camMod
        #self.capture.imageCaptured.connect(self.captureImage)


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
            self.userTools.setEnabled(True)
    
    # Refreshing status by re-running initCam with new action data
    def refreshCamDevice(self, action):
        self.initCam(action.data())
        self.camFeed.show()

    # QOL shortcuts
    def keyPressEvent(self,keyEvent):
        if keyEvent.key() == Qt.Key_Escape:
            sys.exit()

    def captureImage(self):
        # Bunch of error checking for valid emails blabla 
        # but for now just complain if it's empty & use a name.
        # The point of this is to have 1 image per person for the face average function
        if not self.line_email.text():
            QMessageBox.about(self,"Error","Please enter a name")
            return

        name = self.line_email.text()
        # Save the image using persons name

        self.stackedWidget.setCurrentIndex(1)
        # Okay so at this point I need to figure out whether I want to automatically run
        # the morphing process or give the user the option to proceed.
        # Since the current application is in the form of a basic desktop application
        # I've opted for the latter:

        self.capture.capture(os.path.join(current_path,"temp",str(name))) # This captures and saves directly from cam

        # Resizing, aligning and other landmark detection goes here

        # Face detection goes here
        filename = str(name + ".jpg")
        temp_file_path = os.path.join(current_path,"temp",filename)
        image_file_path = os.path.join(current_path,"images",filename)

        confirmation = self.confirmCapture()

        if confirmation:
            # Trigger face morph sequence:
            # 1 Check existing file names. Throw except if file exists and ask if they wish to retake
            # 2 run facial recognition, throw except if face exists with qmessagebox
            # 3 if 2 returns none, save to images
            # 4 run average program
            # 5 display average_of_faces.jpg in the second viewport

            # 1
            exists = self.imageNameCheck(filename)

            single_face_check = self.imageContainsSingleFace( temp_file_path )

            if ( not exists ) and ( single_face_check == 1 ):    
                import detector
                detector.saveSingleFace( temp_file_path )
                os.replace(temp_file_path, image_file_path)
                self.stackedWidget.setCurrentIndex(0)
            elif ( not exists ) and ( single_face_check == 0 ):
                QMessageBox.about(self, "Error", "No face detected. Please ensure your face is displayed and that you're not covering your face")
                os.remove(temp_file_path)
                self.stackedWidget.setCurrentIndex(0)
            elif ( not exists ) and ( single_face_check > 1 ):
                QMessageBox.about(self, "Error", "Too many faces detected. One image per person please")
                os.remove(temp_file_path)
                self.stackedWidget.setCurrentIndex(0)
            else:
                os.remove(temp_file_path)
                self.stackedWidget.setCurrentIndex(0)
        else:
            os.remove(temp_file_path)
            self.stackedWidget.setCurrentIndex(0)

    def processImage(self,requestId,img):
        # We want to force the capture to maintain aspect ratio of the left window so..
        scaledImage = img.scaled(self.camFeed.size(),Qt.KeepAspectRatio)
        # Apply the image to the right window
        self.camMod.setPixmap(QPixmap.fromImage(scaledImage))

    def confirmCapture(self):
        confirmation = QMessageBox(QMessageBox.Question,'Confirmation','Are you happy with this image?', QMessageBox.Yes|QMessageBox.No)
        
        result = confirmation.exec_()
        filename = str(self.line_email.text() + ".jpg")

        if result == confirmation.Yes:
            return True
        else:
            return False

    def imageNameCheck(self, filename):
        img_dir = os.path.join(current_path,"images")
        for images in os.listdir(img_dir):

            if images == filename:
                exists = QMessageBox(QMessageBox.Question,'Warning','You have already saved an image. Do you wish to overwrite it?', QMessageBox.Yes|QMessageBox.No)
                result = exists.exec_()

                if result == exists.Yes:
                    return False
                else:
                    return True
            else:
                return False

    def imageContainsSingleFace(self, image):               
        import detector

        filename =  os.path.basename( image )
                
        number_of_faces = detector.detectFace(filename, image)         
         
        return number_of_faces


        
    def addFace(self):
        # Run Detector.py
        # Run faceAverage.py
        # Display morphed_faces.jpg from Final
        import detector
        import faceAverage

        image_files = os.path.join( "images" , "faces" , "*.jpg")

        files = len( glob.glob( image_files ) )
        print(files)
        if files < 2:
            QMessageBox.about(self, "Error", "Not enough images. Need at least 2")
            return
    
        detector.savePlt()
        faceAverage.saveMorphedFace()

        if os.path.isfile( os.path.join( "images" , "final" , "morphed_faces.jpg" ) ):
            print("File Exists")
            morphed_image = QPixmap( os.path.join( "images" , "final" , "morphed_faces.jpg" ) )
            scaled_morphed_image = morphed_image.scaled(self.imgMorphed.size(),Qt.KeepAspectRatio)
            self.imgMorphed.setPixmap( scaled_morphed_image )
        else:
            print("Missing")

    def updateLast(self):

        FACE_PATH = os.path.join( "images" , "faces" , "*.jpg" )
        try:
            latest_image = max( glob.iglob( FACE_PATH ) , key = os.path.getctime )
        except ValueError:
            QMessageBox.about(self, "Error", "No images saved")
            return
                    
        try:
            last_face = QPixmap( latest_image )
            scaled_last_face = last_face.scaled(self.img_lastfaceadded.size(),Qt.KeepAspectRatio)
            self.img_lastfaceadded.setPixmap( scaled_last_face )
        except IOError:
            QMessageBox.about(self, "Error", "No images saved")
        

# Start App:
if __name__=='__main__':
    app = QApplication(sys.argv)
    qt_app = MainWindow()
    qt_app.show()
    app.exec_()




            