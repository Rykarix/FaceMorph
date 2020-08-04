import os
import sys
import dlib
import cv2
import numpy as np
import glob
#from PIL import Image
import matplotlib.image as mpimg
import matplotlib.pyplot as plt

#print(os.path.dirname(sys.executable))

PATH = os.path.join( "images" , "*.jpg" )
DATA_FILE = os.path.join( "data" , "shape_predictor_68_face_landmarks.dat" )


# Function that draws a bounding box around a detected face:
def drawBB(image,bound):
    image = image.copy()
    point_topleft = ( bound.left() , bound.top() )
    point_bottomright = ( bound.right() , bound.bottom() )
    return cv2.rectangle( image , point_topleft , point_bottomright , (0,0,255) , 3)

def saveBBImg(PATH):
    '''
    Feed function a folder path and it will

    1 Save all faces to a folder called faces
    2 Save all face data to a corresponding 

    '''
    
    # Detector object:
    object_detector = dlib.get_frontal_face_detector()

    # For each image in a directory, detect a face
    for image in glob.glob(PATH):

        filename =  os.path.basename( image )
        im = mpimg.imread(image)

        parse_detector = object_detector(im)

        print( "# of faces detected = {}".format( len( parse_detector ) ) )
        print( image )

        # If a face is detected, draw a bounding box around each one
        if len( parse_detector ): 
            for i,j in enumerate( parse_detector ):
                
                print( " Detected face #: {}".format( i + 1 ) )
                im = drawBB( im , j)
        else:
            print( "No Face detected" )        
            return
        plt.xticks( [] ), plt.yticks( [] )
        plt.imsave( os.path.join( "images" , "faces" , str( filename ) ) , im )

saveBBImg(PATH)
    
