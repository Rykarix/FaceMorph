<i><b>
Archived due to being redundant and abandoned. This was a fun project, started to solve a problem and abandoned once it helped me land my first 'proper coding job' and my priorities shifted.</b>
</i>

## Notes from future self
This was my final project for Uni

This is really old, shockingly bad code. A complete mess... But it was one of my first code projects as a 'baby yoda' coder. Left for nostalgia & a demonstration of how to not write python code

--- 

# Face-Morph

# Version 1.0
Basic GUI now made including connected camera

<p align="center">
  <img src="https://github.com/Rykarix/FaceMorph/blob/master/images/face_morph_gui.png">
</p>


## TASK LIST:

 First we need a UI:
 ~~User should see a live cam feed~~
 ~~User should see a preview of processed images~~
 - The app should contain a toolbox that helps them manage
   camera settings, Image processing functions and anything
   else they need

 Then we need to write functions that do tings :)
 - ~~Face morph~~
 - Will morph/merge multiple faces into a single face. Using test images produces the following:

<p align="center">
  <img src="https://github.com/Rykarix/FaceMorph/blob/master/images/morphed_faces.jpg">
</p>


 Things to consider:
 - Infrared (Detect fevers - especially useful considering Covid)
 - Malinoma detection? How? Detect blemishes on skin? Chris?
 - Aging process?

 Things I'd do with infinite resources / time:
 - Mount the camera to a robotic arm - have it auto detect best pos.
 - Use a point cloud camera - 3D scan of face
 - Apply above processes in 3D

 To accomplish the above I will be making heavy use of 2 core packages.
 PyQt5 to handle GUI and OpenCV to handle image processing.
 Both are well known and updated regularly.

## Listing the resources I'm using for Academic integrity
 UI:
 PyQt5 Source code & tools: https://riverbankcomputing.com/software/pyqt/download5
 Qt docs: https://doc.qt.io/qt-5/index.html
 This will be all I need to use for GUI. (Many guides on the internet
explain & write examples of the PyQt package poorly)
