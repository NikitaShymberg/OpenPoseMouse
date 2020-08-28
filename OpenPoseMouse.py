# Keypoints:
# 0 - Nose
# 1 - Chest
# 2 - Right shoulder
# 3 - Right elbow
# 4 - Right wrist
# 5 - Left shoulder
# 6 - Left elbow
# 7 - Left wrist
# 8 - Crotch
# 9 - Right hip
# 10 - Right knee
# 11 - Right ankle
# 12 - Left hip
# 13 - Left knee
# 14 - Left ankle
# 15 - Right eye
# 16 - Left eye
# 17 - Right ear
# 18 - Left ear
# 19 - Left toe 1
# 20 - Left toe 2
# 21 - Left heel
# 22 - Right toe 1
# 23 - Right toe 2
# 24 - Right heel

import cv2
import pyautogui
import time
import PySpin
from openpose import pyopenpose as op  # Don't forget to add this to PYTHONPATH

# Constants
SETUP_RECT_L = [(50, 50), (150, 150)]
SETUP_RECT_R = [(540, 50), (640, 150)]
MOUSE_DOWN_RECT = [(50, 50), (200, 240)]
MOUSE_CLICK_RECT = [(50, 240), (200, 430)]
MOUSE_POINT_RECT = [(50, 50), (590, 430)]
MOUSE_POINT_RECT_W = MOUSE_POINT_RECT[1][0] - MOUSE_POINT_RECT[0][0]
MOUSE_POINT_RECT_H = MOUSE_POINT_RECT[1][1] - MOUSE_POINT_RECT[0][1]
LEFT_WRIST = 4
RIGHT_WRIST = 7
CLICK_TIMEOUT = 2  # Number of seconds bw clicks
WINDOW_NAME = 'OpenPoseMouse'


def run_inference(frame):
    """
    Runs inference on the given `frame` using the globap opWrapper and datum.
    Returns the keypoints and output image.
    """
    datum.cvInputData = frame
    opWrapper.emplaceAndPop([datum])
    keypoints = datum.poseKeypoints
    out_img = datum.cvOutputData

    return keypoints, out_img


def is_in_rect(point, rectangle):
    """
    Returns whether the given `point` is inside or outside the `rectangle`.
    """
    if point[0] > rectangle[0][0] and point[0] < rectangle[1][0]\
            and point[1] > rectangle[0][1] and point[1] < rectangle[1][1]:
        return True
    return False


def setup_openpose():
    """
    Does the initial OpenPose setup. Returns the opWrapper and datum to use for inference.
    """
    # Custom Params (refer to include/openpose/flags.hpp for more parameters)
    params = {}
    params['model_folder'] = '/home/nikita/Desktop/openpose/models/'

    # Starting OpenPose
    opWrapper = op.WrapperPython()
    opWrapper.configure(params)
    opWrapper.start()
    datum = op.Datum()

    return opWrapper, datum


def setup_camera():
    """
    Initializes the camera.
    Returns the camera object to use to get images.
    """
    cam_list = system.GetCameras()
    cam = cam_list[0]
    cam.Init()
    cam.AcquisitionStop()  # recover from a crash
    s_node_map = cam.GetTLStreamNodeMap()

    cam.PixelFormat.SetValue(PySpin.PixelFormat_BGR8)
    handling_mode = PySpin.CEnumerationPtr(s_node_map.GetNode('StreamBufferHandlingMode'))
    handling_mode_entry = handling_mode.GetEntryByName('NewestOnly')  # keep the steam as "live" as possible
    handling_mode.SetIntValue(handling_mode_entry.GetValue())
    cam.BeginAcquisition()

    # This code can be used instead to use a webcam
    # cam = cv2.VideoCapture(0)
    # Capture a frame
    # ret, frame = cam.read()
    # if not ret:
    #     print('failed to grab frame')

    return cam


def setup_person():
    """
    Shows two rectangles.
    Once the person places their hands into the matching rectangle, this function returns.
    """
    while True:
        # Get image
        frame = cam.GetNextImage().GetNDArray()
        frame = cv2.flip(frame, 1)

        # Run inference
        keypoints, out_img = run_inference(frame)

        # Add rectangles
        out_img = cv2.rectangle(out_img, SETUP_RECT_L[0], SETUP_RECT_L[1], (0, 0, 255), 2)
        out_img = cv2.putText(out_img, 'Left Hand', SETUP_RECT_L[0], cv2.FONT_HERSHEY_PLAIN, 2, (0, 0, 0), 2)
        out_img = cv2.rectangle(out_img, SETUP_RECT_R[0], SETUP_RECT_R[1], (0, 0, 255), 2)
        out_img = cv2.putText(out_img, 'Right Hand', SETUP_RECT_R[0], cv2.FONT_HERSHEY_PLAIN, 2, (0, 0, 0), 2)

        # Check if hands are in the right place
        if len(keypoints.shape) != 0:
            right_hand_point = [int(keypoints[0, RIGHT_WRIST, 0]), int(keypoints[0, RIGHT_WRIST, 1])]
            left_hand_point = [int(keypoints[0, LEFT_WRIST, 0]), int(keypoints[0, LEFT_WRIST, 1])]
            if is_in_rect(left_hand_point, SETUP_RECT_L) and is_in_rect(right_hand_point, SETUP_RECT_R):
                print('Person detected, turning mouse on...')
                cv2.imshow(WINDOW_NAME, out_img)
                cv2.waitKey(1)
                return

        # Show
        cv2.imshow(WINDOW_NAME, out_img)
        cv2.waitKey(1)


def pause_person(t):
    """
    Pauses the hand detection for t half-seconds. This gives the operator a few seconds to get ready.
    Displays a countdown to give time to prepare
    """
    out_img = datum.cvOutputData
    for i in range(t, 0, -1):
        countdown = '{}...'.format(i)
        out_img[:, :, :] = 0
        out_img = cv2.putText(out_img, countdown, SETUP_RECT_L[0], cv2.FONT_HERSHEY_PLAIN, 2, (255, 255, 255), 2)
        cv2.imshow(WINDOW_NAME, out_img)
        cv2.waitKey(1)
        print(countdown)
        time.sleep(1)


def run_mouse():
    """
    The 'main' part of the program that lets the operator control the mouse with their hands.
    """
    prev_click_time = 0

    while True:
        frame = cam.GetNextImage().GetNDArray()
        frame = cv2.flip(frame, 1)

        # Run inference
        keypoints, out_img = run_inference(frame)

        # Add rectangles
        out_img = cv2.rectangle(out_img, MOUSE_DOWN_RECT[0], MOUSE_DOWN_RECT[1], (0, 0, 255), 2)
        out_img = cv2.putText(out_img, 'Mouse Down', MOUSE_DOWN_RECT[0], cv2.FONT_HERSHEY_PLAIN, 2, (0, 0, 0), 2)
        out_img = cv2.rectangle(out_img, MOUSE_CLICK_RECT[0], MOUSE_CLICK_RECT[1], (0, 0, 255), 2)
        out_img = cv2.putText(out_img, 'Mouse Click', MOUSE_CLICK_RECT[0], cv2.FONT_HERSHEY_PLAIN, 2, (0, 0, 0), 2)
        out_img = cv2.rectangle(out_img, MOUSE_POINT_RECT[0], MOUSE_POINT_RECT[1], (0, 255, 0), 2)

        if len(keypoints.shape) != 0:
            # Move mouse
            right_hand_point = [int(keypoints[0, RIGHT_WRIST, 0]), int(keypoints[0, RIGHT_WRIST, 1])]
            out_img[right_hand_point[1]] = [0, 0, 0]
            out_img[:, right_hand_point[0]] = [0, 0, 0]
            if is_in_rect(right_hand_point, MOUSE_POINT_RECT):
                relative_x = (right_hand_point[0] - MOUSE_POINT_RECT[0][0]) / MOUSE_POINT_RECT_W
                relative_y = (right_hand_point[1] - MOUSE_POINT_RECT[0][1]) / MOUSE_POINT_RECT_H
                screen_x = relative_x * pyautogui.size()[0]
                screen_y = relative_y * pyautogui.size()[1]
                screen_right_hand_point = [screen_x, screen_y]
                print('Mouse coords:', right_hand_point, screen_right_hand_point, out_img.shape, pyautogui.size())
                pyautogui.moveTo(screen_right_hand_point[0], screen_right_hand_point[1])

            # Click buttons
            left_hand_point = [int(keypoints[0, LEFT_WRIST, 0]), int(keypoints[0, LEFT_WRIST, 1])]
            out_img[left_hand_point[1]] = [0, 0, 0]
            out_img[:, left_hand_point[0]] = [0, 0, 0]
            if is_in_rect(left_hand_point, MOUSE_DOWN_RECT):
                pyautogui.mouseDown()
                print('MouseDown')
            elif is_in_rect(left_hand_point, MOUSE_CLICK_RECT) and prev_click_time + CLICK_TIMEOUT < time.time():
                pyautogui.click()
                prev_click_time = time.time()
                print('Clicked')
            else:
                pyautogui.mouseUp()

        cv2.imshow(WINDOW_NAME, out_img)
        cv2.waitKey(1)


if __name__ == "__main__":
    pyautogui.FAILSAFE = False
    system = PySpin.System.GetInstance()  # system cannot go out of scope or cam will crash
    opWrapper, datum = setup_openpose()  # keeping these global for convenience
    cam = setup_camera()
    setup_person()
    pause_person(5)
    run_mouse()
