"""
For each video we need the following -
- Labeled video output from DLC
- Coordinates csv file (post running get_coords.py)
"""

# Open particular frame from video
import cv2

global videopath
import pandas as pd
import matplotlib.pyplot as plt

# import plotly.express as px
# from plotly.subplots import make_subplots
# import plotly.graph_objects as go
import numpy as np
from scipy import stats, integrate
import seaborn as sns
from scipy.stats import zscore
import os
import glob

# Get all the videos in the directory.
global data_directory, new_directory, all_video_correct_frames_df
all_video_correct_frames_df = pd.DataFrame()
data_directory = '/storage1/fs1/yaochen/Active/DLC/Test_Models/iteration2_day_night/night/Testing/'
#data_directory = r"C:\Users\Chen Lab\Desktop\DLC_final\Jitter_code_data\\"
extension_csv = "csv"  # All frames are indexed at 0
extension_video = "mp4"
new_directory = data_directory + "clean_coords/"
os.chdir(data_directory)
import os
try: 
    os.makedirs(new_directory)
except OSError:
    if not os.path.isdir(new_directory):
        raise
csv_files = glob.glob("*.{}".format(extension_csv))
video_files = glob.glob("*.{}".format(extension_video))
print("\nCoordinate CSV Files Found: ", csv_files)
print("\nVideo Files Found: ", video_files)
print("\nNumber of video-csv: ", len(video_files))

# Align correct files together in a list of lists.
# Idean output: [[video_1, csv_1],[video_2, csv_2], [video_3, csv_3].....]

# The current problem is that the list don't have the same names coming in in the same sequence, so will need to sort.
csv_files.sort()
video_files.sort()
i = 0
# list of lists holding the correct csv-video pairs
data_list = []
for i in range(len(csv_files)):
    temp_list = [csv_files[i], video_files[i]]
    data_list.append(temp_list)
    i = i + 1
# Printing all the aligned pairs
i = 0
print("\nSorted List")
for i in range(len(data_list)):
    print("\n", data_list[i])


# Input: the respective video name
# Usage: The function prompts the user to select the best frame for each body part

# Input: the respective csv-video pair
# Usage: The function prompts the user to select the best
# Opencv2 Trackbar documentation: https://docs.opencv.org/4.x/d7/dfc/group__highgui.html#gaf78d2155d30b728fc413803745b67a9b
def get_frame(csv_name, video_name, body_parts):
    correct_frame = pd.DataFrame(columns=[body_parts])
    # Access video
    # load video capture from file
    print(
        "AFTER getting to the desired frame, press enter."
    )
    print("Then Press S: Save, Q: To skip the body part.; Just choose the correct frame, and the code will propogate in both directions")
    print("Use the trackbar to select the FRAME"
    )
    body_num = 0
    correct_list = []
    for body_num in range(len(body_parts)): # Load the video for each body frame.
        print("Choose best frame for: {}".format(body_parts[body_num]))
        # window name and size
        video = cv2.VideoCapture(os.path.join(data_directory, video_name))
        video_prompt_name = "{}".format(body_parts[body_num]) + "-{}".format(video_name)
        def onChange(trackbarValue):
        	video.set(cv2.CAP_PROP_POS_FRAMES,trackbarValue)
        	err,img = video.read()
        	cv2.imshow(video_prompt_name, img)
        	pass
        length = int(video.get(cv2.CAP_PROP_FRAME_COUNT))
        cv2.namedWindow(video_prompt_name, cv2.WINDOW_AUTOSIZE)
        cv2.createTrackbar( 'Frame', video_prompt_name, 0, length, onChange)
        # cv2.createTrackbar( 'end'  , video_prompt_name, length, length, onChange)
        onChange(0)
        cv2.waitKey(0)
        start = cv2.getTrackbarPos('Frame',video_prompt_name)
        # end   = cv2.getTrackbarPos('end',video_prompt_name)

        video.set(cv2.CAP_PROP_POS_FRAMES,start)
        while video.isOpened():
            # Read video capture
            ret, frame = video.read()
            # Display each frame
            frame_number = video.get(cv2.CAP_PROP_POS_FRAMES)
            frame_number = int(frame_number - 1)  # to get index at 0
            # show one frame at a time
            key = cv2.waitKey(0)
            # character 's' to save the correct currect frame
            # Add slider to navigate through the window rapidly.
            while key not in [ord("s"), ord("q")]:
                key = cv2.waitKey(0)
            if key == ord("s"):
                print("Frame {} saved".format(frame_number))
                correct_list.append(frame_number)
               	print(correct_list)
                break
            elif key == ord("q"):
            	frame_number_correct = None
            	correct_list.append(frame_number_correct)
            	print(correct_list)
            	break
        body_num = body_num + 1
    cv2.destroyAllWindows()
    correct_frame.loc[len(correct_frame)] = correct_list
    correct_frame['video_name'] = video_name
    return correct_frame

# Function to call all auxilary functions

"""
Logic flow:
1. (Done) Grap the CSV, Video file pairs (Initialization)
2. (Done) Identify the correct frame for each body part.
3. Set reference frame as a baseline annotation for each body part.
4. Use the reference frame to calculate subsequent frame difference in x-y axis
  1. look for what needs to be done here so we get a releative distance from each coordinate (what happens when you have a big jitter, we need the relevant distance to be calculated with the previous small distance)
5. Calculate euclidean distance for each in reference to the previous "correct frame"
6. Calculate z-score for euclidean distance.
7. Drop all distances over 2 standard deviations.
8. Output a summary instance file of all the videos processed in this batch to list the number of correct/incorrect frames/body part/video.
"""
# List to keep track of all the body parts in a video (to account for different models)
global body_parts_list
body_parts_list = []

# This is the control house for all the thingies.
def mega_call():
    i = 0
    for i in range(
        len(data_list)
    ):  # Each pair of csv-video. We do everything in this loop.
        print("\nCSV-Video Pair {}: ".format(i + 1), data_list[i])
        # Printing the current pair.
        # Extract the frames from a video and select the frame for the correct annotation (5 frames/video - 1 body part/frame/video)
        # LHS = correct frame number (index) for each body part
        # Make sure these are in the same sequence in both LSH and the function call
        # RHS = function call for each video. We are passing the csv=video pair for respective videos. func get_frame(csv, video) takes the path for the respective
        data = pd.read_csv(
            data_directory + data_list[i][0]
        )  # Accessing the csv file for the
        del data["Unnamed: 0"]  # Deleting the read_output extra column from pandas.
        column_list = data.columns[
            1:
        ]  # Starting at position 1 (indexed at 0) to get all the body parts (Ignoring: Frames column).
        body_parts_list = (
            column_list.str.rsplit("_", 1).str[0].unique().to_list()
        )  # Splitting the column name string name to just get the body part name. Saving the unique instances.
        print("Body parts: {}".format(body_parts_list))
        # Get a df of correct frame number (indexed at 0) for the respective video for all body parts
        body_parts_correct_frame = get_frame(
            data_list[i][0], data_list[i][1], body_parts_list
        )
        print("\nCorrect Frames for each body part: ")
        print(body_parts_correct_frame)
        print("\nOverall correct frames")
        global all_video_correct_frames_df
        all_video_correct_frames_df = all_video_correct_frames_df.append(body_parts_correct_frame, ignore_index = True)
        print(all_video_correct_frames_df)
    i = i + 1  # Moving onto the next pair
    all_video_correct_frames_df.to_csv(new_directory+"selected_frames_for_all_videos.csv")



mega_call()

# Using the post-user selected frames as ground truth to identify jitters.
print("Coordinate CSV Files Found: ", csv_files)
print("Video Files Found: ", video_files)
print("Number of video-csv: ", len(video_files))
selected_frames = pd.read_csv(new_directory+"selected_frames_for_all_videos.csv")
del selected_frames["Unnamed: 0"]
# print(data_list)

# Access the correct x_y csv for each video
i = 0
coordinate_file_list = []
for index, row in selected_frames.iterrows():
   video_name = row['video_name']
   j = 0 # loop through the list of lists containing the pair
   for j in range(len(data_list)):
     if video_name == data_list[j][1]:
       coordinate_file_list.append(data_list[j][0])
selected_frames['coordinate_file'] = coordinate_file_list

from pandas.core.missing import clean_interp_method
# loop through each labaled video
for index, row in selected_frames.iterrows():
  data = pd.read_csv(data_directory+row['coordinate_file'])
  print("File: ", row['coordinate_file'])
  del data['Unnamed: 0']
  # Subtract the baseline coordinate from each body part
  x_nose_correct = data['nose_x'][row['nose']]
  y_nose_correct = data['nose_y'][row['nose']]

  x_ear1_correct = data['ear1_x'][row['ear1']]
  y_ear1_correct = data['ear1_y'][row['ear1']]

  x_ear2_correct = data['ear2_x'][row['ear2']]
  y_ear2_correct = data['ear2_y'][row['ear2']]

  x_center_correct = data['center_x'][row['center']]
  y_center_correct = data['center_y'][row['center']]

  x_baseoftail_correct = data['baseoftail_x'][row['baseoftail']]
  y_baseoftail_correct = data['baseoftail_y'][row['baseoftail']]

  data['x_nose_diff'] = data['nose_x'] - x_nose_correct
  data['y_nose_diff'] = data['nose_y'] - y_nose_correct

  data['x_ear1_diff'] = data['ear1_x'] - x_ear1_correct
  data['y_ear1_diff'] = data['ear1_y'] - y_ear1_correct

  data['x_ear2_diff'] = data['ear2_x'] - x_ear2_correct
  data['y_ear2_diff'] = data['ear2_y'] - y_ear2_correct

  data['x_center_diff'] = data['center_x'] - x_center_correct
  data['y_center_diff'] = data['center_y'] - y_center_correct

  data['x_baseoftail_diff'] = data['baseoftail_x'] - x_baseoftail_correct
  data['y_baseoftail_diff'] = data['baseoftail_y'] - y_baseoftail_correct


  # Calculate running euclidean distance.
  from scipy.spatial.distance import pdist
  import itertools
  nose_x = data['x_nose_diff'].values
  nose_y = data['y_nose_diff'].values

  ear1_x = data['x_ear1_diff'].values
  ear1_y = data['y_ear1_diff'].values

  ear2_x = data['x_ear2_diff'].values
  ear2_y = data['y_ear2_diff'].values

  center_x = data['x_center_diff'].values
  center_y = data['y_center_diff'].values

  baseoftail_x = data['x_baseoftail_diff'].values
  baseoftail_y = data['y_baseoftail_diff'].values

  nose_coord = [list(x) for x in zip(nose_x, nose_y)]
  ear1_coord = [list(x) for x in zip(ear1_x, ear1_y)]
  ear2_coord = [list(x) for x in zip(ear2_x, ear2_y)]
  center_coord = [list(x) for x in zip(center_x, center_y)]
  baseoftail_coord = [list(x) for x in zip(baseoftail_x, baseoftail_y)]

  # Calculate Euclidean
  import math
  from scipy.spatial import distance
  i = 0
  dist = 0
  nose_ed = [0]
  ear1_ed = [0]
  ear2_ed = [0]
  center_ed = [0]
  baseoftail_ed = [0]

  nose_boolean = []
  ear1_boolean = []
  ear2_boolean = []
  center_boolean = []
  baseoftail_boolean = []

  while i<len(nose_coord)-1:
      dist = distance.euclidean(nose_coord[i],nose_coord[i+1])
      nose_ed.append(dist)
      i = i+1
  #print(nose_ed)
  data['nose_distance'] = nose_ed

  # Getting mean and sd for distance
  des = data['nose_distance'].describe()
  mean = des.loc[['mean']].values[0]
  sd = des.loc[['std']].values[0]
  print("\nMean for nose distance: ", mean)
  print("Standard Deviation for nose distance: ", sd)
  sd_2_plus = mean+(2*sd)
  sd_2_minus = mean-(2*sd)
  print("2 std deviation range: {} - {}".format(sd_2_minus, sd_2_plus))
  j=0
  while j<len(nose_coord):
  	if ((data['nose_distance'][j] <= sd_2_plus) & (data['nose_distance'][j] >= sd_2_minus)):
  		nose_boolean.append(True)
  	else:
  		nose_boolean.append(False)
  	j = j+1
  print(len(nose_boolean))


  i = 0
  dist = 0
  while i<len(ear1_coord)-1:
      dist = distance.euclidean(ear1_coord[i],ear1_coord[i+1])
      ear1_ed.append(dist)
      i = i+1
  data['ear1_distance'] = ear1_ed

  # Getting mean and sd for distance
  des = data['ear1_distance'].describe()
  mean = des.loc[['mean']].values[0]
  sd = des.loc[['std']].values[0]
  print("\nMean for ear1 distance: ", mean)
  print("Standard Deviation for ear1 distance: ", sd)
  sd_2_plus = mean+(2*sd)
  sd_2_minus = mean-(2*sd)
  print("2 std deviation range: {} - {}".format(sd_2_minus, sd_2_plus))
  j = 0
  while j<len(ear1_coord):
  	if ((data['ear1_distance'][j] <= sd_2_plus) & (data['ear1_distance'][j] >= sd_2_minus)):
  		ear1_boolean.append(True)
  	else:
  		ear1_boolean.append(False)
  	j=j+1
  print(len(ear1_boolean))


  i = 0
  dist = 0
  while i<len(ear2_coord)-1:
      dist = distance.euclidean(ear2_coord[i],ear2_coord[i+1])
      ear2_ed.append(dist)
      i = i+1
  data['ear2_distance'] = ear2_ed
  
  # Getting mean and sd for distance
  des = data['ear2_distance'].describe()
  mean = des.loc[['mean']].values[0]
  sd = des.loc[['std']].values[0]
  print("\nMean for ear2 distance: ", mean)
  print("Standard Deviation for ear2 distance: ", sd)
  sd_2_plus = mean+(2*sd)
  sd_2_minus = mean-(2*sd)
  print("2 std deviation range: {} - {}".format(sd_2_minus, sd_2_plus))
  j=0
  while j<len(ear2_coord):
  	if ((data['ear2_distance'][j] <= sd_2_plus) & (data['ear2_distance'][j] >= sd_2_minus)):
  		ear2_boolean.append(True)
  	else:
  		ear2_boolean.append(False) 
  	j=j+1
  print(len(ear2_boolean))

  i = 0
  dist = 0
  while i<len(center_coord)-1:
      dist = distance.euclidean(center_coord[i],center_coord[i+1])
      center_ed.append(dist)
      i = i+1
  data['center_distance'] = center_ed

  # Getting mean and sd for distance
  des = data['center_distance'].describe()
  mean = des.loc[['mean']].values[0]
  sd = des.loc[['std']].values[0]
  print("\nMean for center distance: ", mean)
  print("Standard Deviation for center distance: ", sd)
  sd_2_plus = mean+(2*sd)
  sd_2_minus = mean-(2*sd)
  print("2 std deviation range: {} - {}".format(sd_2_minus, sd_2_plus))
  j=0
  while j<len(center_coord):
  	if ((data['center_distance'][j] <= sd_2_plus) & (data['center_distance'][j] >= sd_2_minus)):
  		center_boolean.append(True)
  	else:
  		center_boolean.append(False)
  	j=j+1
  print(len(center_boolean))

  i = 0
  dist = 0
  while i<len(baseoftail_coord)-1:
      dist = distance.euclidean(baseoftail_coord[i],baseoftail_coord[i+1])
      baseoftail_ed.append(dist)
      i = i+1
  data['baseoftail_distance'] = baseoftail_ed
  # Getting mean and sd for distance
  des = data['baseoftail_distance'].describe()
  mean = des.loc[['mean']].values[0]
  sd = des.loc[['std']].values[0]
  print("\nMean for baseoftail distance: ", mean)
  print("Standard Deviation for baseoftail distance: ", sd)
  sd_2_plus = mean+(2*sd)
  sd_2_minus = mean-(2*sd)
  print("2 std deviation range: {} - {}".format(sd_2_minus, sd_2_plus))
  j=0
  flag = 0
  while j<len(baseoftail_coord):
  	if ((data['baseoftail_distance'][j] <= sd_2_plus) & (data['baseoftail_distance'][j] >= sd_2_minus)):
  		baseoftail_boolean.append(True)
  	else:
  		baseoftail_boolean.append(False)
  	j=j+1
  print(len(baseoftail_boolean))
  
  print("Adding boolean columns for each body part")
  data['nose_boolean'] = nose_boolean
  data['ear1_boolean'] = ear1_boolean
  data['ear2_boolean'] = ear2_boolean
  data['center_boolean'] = center_boolean
  data['baseoftail_boolean'] = baseoftail_boolean

  print("---------------------- FINAL DATASET ------------------------")
  data.to_csv(new_directory + "mid_processed_" + row['coordinate_file'])

print("Saving summary stats for all videos")
# Create a singular file with the number of true annotations for each body part per video
summary_columns = ['video_name', 'center','ear1','ear2','center','baseoftail','all_true']
summary_df = pd.DataFrame(columns = summary_columns)
print(summary_df)
for index, row in selected_frames.iterrows():
  data = pd.read_csv(new_directory+"mid_processed_"+row['coordinate_file'])
  summary_list = []
  del data['Unnamed: 0']
  correct_nose = data['nose_boolean'].sum()
  correct_ear1 = data['ear1_boolean'].sum()
  correct_ear2 = data['ear2_boolean'].sum()
  correct_center = data['center_boolean'].sum()
  correct_baseoftail = data['baseoftail_boolean'].sum()
  summary_list.append(row['coordinate_file'])
  summary_list.append(correct_nose)
  summary_list.append(correct_ear1)
  summary_list.append(correct_ear2)
  summary_list.append(correct_center)
  summary_list.append(correct_baseoftail)
  count = 0
  for index, row in data.iterrows():
  	if (row['nose_boolean'] & row['ear1_boolean'] & row['ear2_boolean'] & row['center_boolean'] & row['baseoftail_boolean']):
  		count = count + 1
  summary_list.append(count)
  print("Summary_list: ", summary_list)
  summary_df = summary_df.reset_index(drop=True)
  summary_df.loc[index] = summary_list
print("Summary data saved!")
summary_df.to_csv(new_directory + "summary_stats.csv")
print("------------- Done --------------")