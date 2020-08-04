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

IMAGE_FOLDER = os.path.join( "images" , "*.jpg" )
FACE_PATH = os.path.join( "images" , "faces" , "*.jpg" )
DATA_FILE = os.path.join( "data" , "shape_predictor_68_face_landmarks.dat" )
TEST_FILE = os.path.join( "images" , "testfem1.jpg" )

# Detector object:
detector = dlib.get_frontal_face_detector()

# Predictor object
predictor = dlib.shape_predictor( DATA_FILE )

# face dimensions 
w = 600
h = 600

# Function that draws a bounding box around a detected face:
def drawBB( image , bound ):
    image = image.copy()
    point_topleft = ( bound.left() , bound.top() )
    point_bottomright = ( bound.right() , bound.bottom() )
    return cv2.rectangle( image , point_topleft , point_bottomright , (0,0,255) , 3)

def getCoords( shape , dtype = "int" ):
    coords = np.zeros( ( 68, 2 ) , dtype=dtype )

    for i in range( 0, 68 ):
        coords[i] = ( shape.part( i ).x , shape.part( i ).y )

    return coords

def coordsToFile( filename , shape ):
    landmark_path = os.path.join( "images" , "faces" , filename )

    with open( landmark_path + ".txt" , "w" ) as f:
        for e,i in enumerate(shape):

            # We don't want a trailing empty line at the end of the file so
            if e == 67:
                f.write( str( i[0] ) + " " + str( i[1] ) )
            else:
                f.write( str( i[0] ) + " " + str( i[1] ) + "\n")

        f.close()

def getPoints( image ):
    dets = detector( image )
    
    for i,j in enumerate( dets ):
        gray = cv2.cvtColor( image , cv2.COLOR_RGB2GRAY )
        shape = getCoords( predictor( gray , j ) )

    return shape 

def faceExtractor( filename , image ):
    # Read the image file
    img = mpimg.imread( image )

    # Save original image to another variable
    img_original = img.copy()

    # Save feature points to a local variable
    pts = getPoints( img )

    # Write points to text file
    #coordsToFile( filename , pts )

    # Generate a convex hull to create a mask using polylines and fillConvexPoly which 
    # will be used to crop out faces
    hull = cv2.convexHull( pts )
    hull = np.array( [[x[0][0],x[0][1]] for x in hull] , np.int32 )
    hull = hull.reshape( ( -1 , 1 , 2 ) )
    cv2.polylines( img , [hull] , True , ( 255 , 255 , 255 ) )
    mask = np.ones( img.shape[:-1] , dtype = np.uint8 )
    cv2.fillConvexPoly( mask , np.int32( hull ) , ( 0 , 0 , 0 ) )
    
    mask *= 255
    mask = cv2.bitwise_not( mask )
    
    ret , thresh = cv2.threshold( mask , 127 , 255 , 0 )
    contours , heirarchy = cv2.findContours( thresh , 1 , 2 )

    # Find the contours of the mask and put a box around it
    cont = contours[0]
    rect = cv2.minAreaRect( cont )
    box = cv2.boxPoints( rect )
    box = np.int0( box )

    xmax , xmin = np.max( box[:,0] ) , np.min( box[:,0] )
    ymax , ymin = np.max( box[:,1] ) , np.min( box[:,1] )

    masked_img = cv2.bitwise_and( img_original , img_original , mask = mask )

    crop_img = masked_img[ ymin:ymax , xmin:xmax ] 
    resize_img = cv2.resize( crop_img , ( h , w ) )
    shape = getPoints( resize_img )

    # Draw circles around each landmark - testing purposes only
    #for ( x , y ) in shape1:
    #    cv2.circle( img_original , ( x , y ) , 1 , ( 0 , 0 , 0 ) , -1 )
    #for ( x , y ) in shape2:
    #    cv2.circle( resize_img , ( x , y ) , 1 , ( 0 , 0 , 0 ) , -1 )
    #plt.imsave( os.path.join( "images" , "faces" , str( "orig" + filename ) ) , img_original )

    return resize_img , shape

def detectFace( filename , image ):
    '''
    Feed function a jpg path and it will detect any and all faces and return: 

    0 if no face is detected
    1 if 1 face is detected
    2 if more than one face is detected
    
    If I have time: 
    3 if glasses are detected
    4 if a mask is detected
    5 if a hat is detected
    '''

    im = mpimg.imread( image )
    number_of_faces = len( detector ( im ) )
    print( "{} faces detected in file {}".format( number_of_faces , filename ) )

    # If a face is detected, draw a bounding box around each one
    if number_of_faces == 0:
        return 0
    elif number_of_faces > 2: 
        return 2
    elif number_of_faces == 1:
        return 1

def savePlt( IMAGE_FOLDER ):
    '''
    Feed function a folder path and it will

    1 Save all faces to a folder called faces
    2 Save all face data to a corresponding 
    '''
    
    # For each image in a directory, detect a face
    for image in glob.glob( IMAGE_FOLDER ):
        filename =  os.path.basename( image )
        print("Processing: " + str( filename ))

        img_check = detectFace( filename , image )

        if img_check == 1:
            resized_img, shape = faceExtractor( filename , image )
            plt.imsave( os.path.join( "images" , "faces" , str( "resized" + filename ) ) ,  resized_img )
            coordsToFile( filename , shape )

        elif img_check == 0:
            print("No faces detected")
        
        elif img_check > 1:
            print( "Multiple faces detected in {}. Skipping (for now). ".format( filename ) )



savePlt( IMAGE_FOLDER )