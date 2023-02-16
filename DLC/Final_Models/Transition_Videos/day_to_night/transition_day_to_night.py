# Script to get coordinates and likelihood in one clean csv/video
# Get all .h5 files


import pandas as pd
from pandas import IndexSlice as idx 
import os
import cv2

print("------- Accessing day/night files -----")
# return all files as a list
csv_day = []
csv_night = []
videos =[]

# Change to the directory with your .h5 files 
# (usually the direcoty where you put your videos for analysis)
# directory = '/storage1/fs1/yaochen/Active/DLC/Circle_Cage/Testing/'
directory = '/storage1/fs1/yaochen/Active/DLC/Final_Models/Transition_Videos/day_to_night/'
for file in os.listdir(r'{}'.format(directory)):
     # check the files which are end with specific extension
    if file.endswith("_day.csv"):
        # print path name of selected files
        print(os.path.join(r'{}'.format(directory), file))
        csv_day.append(file)

for file in os.listdir(r'{}'.format(directory)):
     # check the files which are end with specific extension
    if file.endswith("_night.csv"):
        # print path name of selected files
        print(os.path.join(r'{}'.format(directory), file))
        csv_night.append(file)

for file in os.listdir(r'{}'.format(directory)):
    # check the files which end wth specific extension
    if file.endswith(".mp4"):
        #print path name of selected files 
        print(os.path.join(r'{}'.format(directory), file))
        videos.append(file)

csv_day.sort()
csv_night.sort()
videos.sort()

print("----- Please check the sequence of the files below. Make sure they match -------")
print("All day csv: ", csv_day)
print("All night csv: ", csv_night)
print("All video files: ", videos)

print("Does the same index in each of the three lists correspond to the same video?")
user_confirmation = input("Continue? (y/n): ")
if user_confirmation == 'y':
    None
else:
    quit()

print("Creating list of lists for easier file path handling")

data_list = []
for i in range(len(csv_day)):
    temp_list = [videos[i], csv_day[i], csv_night[i]]
    data_list.append(temp_list)
    i = i + 1

# Printing all the aligned pairs
i = 0
print("\nSorted List")
for i in range(len(data_list)):
    print("\n", data_list[i])

user_confirmation2 = input("Continue? (y/n)")
if user_confirmation2 == 'y':
    None
else:
    quit()

for i in range(len(data_list)):
    file_name = data_list[i][0]
    day = data_list[i][1]
    night = data_list[i][2]

    print("Video Processing: ", file_name)
    day_to_night = True
    night_to_day = False

    cap = cv2.VideoCapture(file_name)
    #  Get frame count

    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    print("Total no. of Frames: ",total_frames)
    # Set the contrast threshold
    if day_to_night == True:
        threshold = 5
    if night_to_day == True:
        threshold = 10
    # Initialize frame counter
    frame_counter = 0

    identified_frame = []
    # Loop through each frame
    while True:
        # Read the next frame
        ret, frame = cap.read()
        if not ret:
            break
        # Convert to grayscale
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        # Calculate the mean luminance of the frame
        mean_luminance = cv2.mean(gray)[0]
    
        # Compare the mean luminance with the previous frame
        if frame_counter > 0 and abs(mean_luminance - previous_mean_luminance) > threshold:
            print("Contrast change at frame: ", frame_counter)
            identified_frame.append(frame_counter)
        # Store the mean luminance of the current frame
        previous_mean_luminance = mean_luminance
        # Increment the frame counter
        frame_counter += 1
    # Release the video capture
    cap.release()
    #identified_frame = [10,12]
    print(identified_frame)
    print("only using a within 30 frame window.")

    initial = identified_frame[0] # first frame
    end = identified_frame[-1] # last frame
    for j in range(len(identified_frame)-1):
        if identified_frame[j+1] - initial <= 30:
            j=j+1
        else:
            end = identified_frame[j-1]

    print("Done")
    print("Total transitioning frames: ",end-initial)

    print(data_list[i])
    combined_pd = pd.DataFrame()
    day_pd = pd.read_csv(directory + "{}".format(data_list[i][1]))
    night_pd = pd.read_csv(directory +"{}".format(data_list[i][2]))
    rows = night_pd.shape[0]

    start = initial - 5
    stop = end + 5

    check = stop - start
    print("Check: ", check)
    if check < 50:
        day_pd = day_pd.head(start) 
        night_pd = night_pd.iloc[start:rows]
        combined_pd = pd.concat([day_pd, night_pd])
        combined_pd = combined_pd.reset_index(drop=True)
        string = data_list[i][1][:-8]
        print(string)
        combined_pd = combined_pd.loc[:, ~combined_pd.columns.str.contains('^Unnamed')]
        combined_pd.to_csv(directory + "{}".format(string) + ".csv")
    else:
        print("Check the number of frames in transition. The transition period seems too high.")
    print("Done saving transition csv")
    i = i+1