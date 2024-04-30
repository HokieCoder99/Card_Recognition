############## Camera video stream creator ###############
#
# Author: Evan Juras  (heavily copying from Adrian Rosebrock)
# Date: 1/12/18
# Description: Defines the VideoStream object, which controls
# acquisition of frames from a PiCamera or USB camera. The object uses
# multi-threading to aquire camera frames in a separate thread from the main
# program. This allows the main thread to grab the most recent camera frame
# without having to take it directly from the camera feed, reducing I/O time,
# which slightly improves framerate.
#
# When using this with a USB Camera on a desktop or laptop, the framerate tends
# to be too fast. The Card Detector program still works, but it is intended
# for the lower processing power of the Raspberry Pi.
#
# See the following web pages for a full explanation of the source code:
# https://www.pyimagesearch.com/2015/12/28/increasing-raspberry-pi-fps-with-python-and-opencv/
# https://www.pyimagesearch.com/2015/12/21/increasing-webcam-fps-with-python-and-opencv/

# Import the necessary packages
from threading import Thread
import cv2

class VideoStream:
    """Camera object that captures video frames and displays the running count."""
    def __init__(self, resolution=(640,480), framerate=30, PiOrUSB=1, src=0):
        self.PiOrUSB = PiOrUSB
        self.resolution = resolution
        self.running_count = 0  # Initialize running count to zero

        if self.PiOrUSB == 1:  # PiCamera
            from picamera.array import PiRGBArray
            from picamera import PiCamera

            self.camera = PiCamera()
            self.camera.resolution = resolution
            self.camera.framerate = framerate
            self.rawCapture = PiRGBArray(self.camera, size=resolution)
            self.stream = self.camera.capture_continuous(
                self.rawCapture, format="bgr", use_video_port=True)
            self.frame = []

        elif self.PiOrUSB == 2:  # USB camera
            self.stream = cv2.VideoCapture(src)
            ret = self.stream.set(3, resolution[0])
            ret = self.stream.set(4, resolution[1])
            (self.grabbed, self.frame) = self.stream.read()

        self.stopped = False

    def start(self):
        Thread(target=self.update, args=()).start()
        return self

    def update(self):
        if self.PiOrUSB == 1:
            for f in self.stream:
                self.frame = f.array
                self.rawCapture.truncate(0)
                self.frame = self.display_running_count(self.frame)

                if self.stopped:
                    self.stream.close()
                    self.rawCapture.close()
                    self.camera.close()

        elif self.PiOrUSB == 2:
            while True:
                if self.stopped:
                    self.stream.release()
                    return
                (self.grabbed, self.frame) = self.stream.read()
                self.frame = self.display_running_count(self.frame)

    def read(self):
        return self.frame

    def stop(self):
        self.stopped = True
    
    def set_running_count(self, count):
        """Update the running count."""
        self.running_count = count

    def display_running_count(self, frame):
        """Draw the running count on the frame."""
        cv2.putText(frame, f"Count: 0", (50, 100),
                    cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)
        return frame

