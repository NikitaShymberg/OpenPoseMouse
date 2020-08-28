# OpenPoseMouse
Control the computer mouse using your body and a camera! See OpenPoseMouseControlMP4.mp4 for a better quality video.

![VIDEO](OpenPoseMouseControlGif.gif)

## Installation
- Install OpenPose: https://github.com/CMU-Perceptual-Computing-Lab/openpose
- (If using a FLIR machine vision camera) install PySpin: https://www.flir.com/products/spinnaker-sdk/
- Install OpenCV for Python
- You may want to use a GPU for this, on my GTX 1060, I got roughly 10-15 FPS

## Usage
Make sure that you've added the python folder in the build directory of OpenPose is in your PYTHONPATH. Then just run `python3 OpenPoseMouse.py`.

First put your right wrist in the right rectangle, and your left wrist in the left rectangle. Then start using the mouse!
