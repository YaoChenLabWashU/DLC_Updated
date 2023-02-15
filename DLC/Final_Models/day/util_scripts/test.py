# Testing the bash script
print("--------------- Confirming there are no temporary video files ------------")
import subprocess
from subprocess import call
with open('/storage1/fs1/yaochen/Active/DLC/Circle_Cage/temporary_remove.sh', 'rb') as file:
    script = file.read()
rc = call(script, shell=True)
print("------------- Temporary files removed ---------------------")

ProjectFolderName = '/storage1/fs1/yaochen/Active/DLC/Circle_Cage'
VideoType = 'mp4' 

#don't edit these:
videofile_path = [ProjectFolderName+'/Testing/'] #Enter the list of videos or folder to analyze.
print("Video Path: ", videofile_path)

#This creates a path variable that links to your google drive copy
#No need to edit this, as you set it up before: 
path_config_file = ProjectFolderName+'/config.yaml'
print("Config file path: ",path_config_file)

import deeplabcut
deeplabcut.__version__

print("----- Creating labeled videos begins -----")
deeplabcut.create_labeled_video(path_config_file,videofile_path, videotype=VideoType)
print("----- Done creating labeled videos!! :)) -----")

# Extract Outlier frames
print("----- Extracting outlier frames -----")
#Get outlier frames
deeplabcut.extract_outlier_frames(path_config_file, videofile_path, videotype=VideoType, shuffle=1, trainingsetindex=0, outlieralgorithm='jump', 
comparisonbodyparts='all', epsilon=20, p_bound=0.01, ARdegree=3, MAdegree=1, alpha=0.01, extractionalgorithm='kmeans', automatic=True)
print("----- Done extracting outlier frames!! :)) -----")

print(" -------------------- DLC Process Done! --------------------")