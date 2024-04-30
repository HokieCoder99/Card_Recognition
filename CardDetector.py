############## Python-OpenCV Playing Card Detector ###############
#
# Author: Evan Juras
# Date: 9/5/17
# Description: Python script to detect and identify playing cards
# from a PiCamera video feed.
#

# Import necessary packages
import cv2
import numpy as np
import time
import os
import Cards
import VideoStream


### ---- INITIALIZATION ---- ###
# Define constants and initialize variables

## Camera settings
IM_WIDTH = 1280
IM_HEIGHT = 720 
FRAME_RATE = 10

## Initialize calculated frame rate because it's calculated AFTER the first time it's displayed
frame_rate_calc = 1
freq = cv2.getTickFrequency()

## Define font to use
font = cv2.FONT_HERSHEY_PLAIN

# Initialize camera object and video feed from the camera. The video stream is set up
# as a seperate thread that constantly grabs frames from the camera feed. 
# See VideoStream.py for VideoStream class definition
## IF USING USB CAMERA INSTEAD OF PICAMERA,
## CHANGE THE THIRD ARGUMENT FROM 1 TO 2 IN THE FOLLOWING LINE:
videostream = VideoStream.VideoStream((IM_WIDTH,IM_HEIGHT),FRAME_RATE,2,0).start()
time.sleep(1) # Give the camera time to warm up

# Load the train rank and suit images
path = os.path.dirname(os.path.abspath(__file__))
train_ranks = Cards.load_ranks( path + '/Card_Imgs/')
train_suits = Cards.load_suits( path + '/Card_Imgs/')


### ---- MAIN LOOP ---- ###
# The main loop repeatedly grabs frames from the video stream
# and processes them to find and identify playing cards.

cam_quit = 0 # Loop control variable

# Begin capturing frames
while cam_quit == 0:

    # Grab frame from video stream
    image = videostream.read()

    # Start timer (for calculating frame rate)
    t1 = cv2.getTickCount()

    # Pre-process camera image (gray, blur, and threshold it)
    pre_proc = Cards.preprocess_image(image)
	
    # Find and sort the contours of all cards in the image (query cards)
    cnts_sort, cnt_is_card = Cards.find_cards(pre_proc)

    # If there are no contours, do nothing
    if len(cnts_sort) != 0:

        # Initialize a new "cards" list to assign the card objects.
        # k indexes the newly made array of cards.
        cards = []
        k = 0
        previous_card_values = []

        # For each contour detected:
        for i in range(len(cnts_sort)):
            if (cnt_is_card[i] == 1):

                # Create a card object from the contour and append it to the list of cards.
                # preprocess_card function takes the card contour and contour and
                # determines the cards properties (corner points, etc). It generates a
                # flattened 200x300 image of the card, and isolates the card's
                # suit and rank from the image.
                cards.append(Cards.preprocess_card(cnts_sort[i],image))

                # Find the best rank and suit match for the card.
                cards[k].best_rank_match,cards[k].best_suit_match,cards[k].rank_diff,cards[k].suit_diff = Cards.match_card(cards[k],train_ranks,train_suits)
                #Will Brown edit
                previous_card_values.append(cards[k].best_rank_match)

                # Draw center point and match result on the image.
                image = Cards.draw_results(image, cards[k])
                k = k + 1
	    
        # Draw card contours on image (have to do contours all at once or
        # they do not show up properly for some reason)
                # Draw card contours on image
        if len(cards) != 0:
            temp_cnts = []
            for card in cards:
                temp_cnts.append(card.contour)
            cv2.drawContours(image, temp_cnts, -1, (128, 0, 0), 3)

    # Draw framerate in the corner of the image
    #cv2.putText(image, "FPS: " + str(int(frame_rate_calc)), (10, 26), font, 1, (0, 255, 255), 2, cv2.LINE_AA)

    # Display previous card values in a structured box
    cv2.putText(image, "Previous Cards: " + ", ".join(previous_card_values[-10:]), (70, IM_HEIGHT - 40), font, 1.5, (232, 119, 34), 2, cv2.LINE_AA)

    # Finally, display the image with the identified cards!
    cv2.imshow("Card Detector", image)


    # Calculate framerate
    t2 = cv2.getTickCount()
    time1 = (t2-t1)/freq
    frame_rate_calc = 1/time1
    
    # Poll the keyboard. If 'q' is pressed, exit the main loop.
    key = cv2.waitKey(1) & 0xFF
    if key == ord("q"):
        cam_quit = 1
        # New function to update the running count based on card value
def update_running_count(card_value, running_count):
    if card_value in [2, 3, 4, 5, 6]:
        running_count += 1
    else if card_value in [10, J, Q, K, A]:
        running_count -= 1
    return running_count

# Modification in the card detection loop in `CardDetector.py` or appropriate place
# Initialize running count
running_count = +0

# When a card is detected and its value is extracted
running_count = update_running_count(card_value, running_count)

# Update the video stream with the current running count
# This might involve modifying a function in `VideoStream.py` or directly in `CardDetector.py`


# Close all windows and close the PiCamera video stream.
cv2.destroyAllWindows()
videostream.stop()

