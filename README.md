# DLC_version_control
ALL RELEVANT DOCUMENTATION: https://tinyurl.com/yc57nfxj

This is the repo to backup DLC trained-models specific to Yao Lab video datasets.

This is the documentation when you want to analyze your videos using pre-trained models! 

If you are just analyzing new videos on pre-trained models, move to SECTION 2. 

-----------------------------------------------------------------  

(Advanced) SECTION 1 – Retrain the model [Talk to Samarth before attempting this] 

If you want to re-train the model (Please consult Samarth to assess whether retraining is required), follow the guide here till after "label Frames" - https://deeplabcut.github.io/DeepLabCut/docs/PROJECT_GUI.html  

Once you have labeled frames, move the entire project folder created locally on your computer to Server (make a new folder in the DLC directory with the name - "Your_name_DLC_description") 

Navigate to any of the pre-trained DLC folders and go to "util_scripsts:" folder. 

Copy the "run_DLC_entire_runOnlyIfTrainingAgain.py" file to your project directory. 

Open  "run_DLC_entire_runOnlyIfTrainingAgain.py" file  in a text editor and change the file paths to point towards your project folder on the server (please use Linux syntax) 

Follow step 1 from below (but navigate to your project folder) and run python3 run_DLC_entire_runOnlyIfTrainingAgain.py 

Move to Step 3c from below!  

------------------------------------------------------------------- 

(Common Use) SECTION 2 – Analyze new videos on pre-trained model 

Everything is setup on our server! The entire process is reduced to just 3 steps!  

1. Uploading videos to be processed (to the server)! 
    a. Directory: Server/DLC/Final_Models 
    b. Decide what kind of videos you want to process?     

        Day? 
        Night? 

    c. Once you have decided, go to Yao Lab Server -> DLC (Z:\Active\DLC\Final_Models)
    d. Go in the folder applicable to your videos (day –or- night) 
    e. Navigate to "Testing" folder 
    f. Make sure there are no videos/folders in this folder. 
    g. Copy all of your videos to be processed (mp4) here! Please take them out of their respective folders. We need videos in the root directory. 

        Paste all day videos in day folder, and all night videos in night folder.  
     

DISCLAIMER: You can use one user account to run only one model.  
    Options 
    (Parallel) Use someone else’s account to access the server and start the process on the other folder.  
        Pros: Takes half as much time. 
        Cons: Needs coordinating with someone else. 
    (Sequential) Run one model first, and then the other. 
        Pros: No coordination needed 
        Cons: Takes twice as long. 

2. Connect to RIS (Our badass GPU Cluster!) 

    Go to terminal or command prompt or powershell (depending on your OS) 

        Use SSH Command to connect to RIS (*imp: You need access to RIS, ask Yao for access if your Wash U ID is not approved) 

        Command:  ssh wustlkey@compute1-client-1.ris.wustl.edu 

    Now, we need to access our docker (Currently we are using a stable DLC Docker from docker_hub created by Kiran. Samarth is currently working on getting Yao Lab's independent docker image! (Available Soon)) 

        Command:  

            LSF_DOCKER_VOLUMES="/storage1/fs1/yaochen/Active:/storage1/fs1/yaochen/Active" PATH="/opt/conda/bin:$PATH" bsub -G compute-yaochen -Is -n 8 -M 64GB -R 'gpuhost span[hosts=1] rusage[mem=64GB]' -gpu 'num=1' -q general-interactive -a 'docker(hlabdocker/hlabdlc2_2_1_1:latest)' /bin/bash 

 
        Wait for job to be executed!  
        Once executed, you should see TensorFlow written in your terminal!  
        This means you are connected successfully!  

3. Start the DLC Process! 

    Navigate to our server  

        Command: cd ../../storage1/fs1/yaochen/Active/DLC/Final_Models/{day -or- night} 

        PLEASE USE 'TAB' KEY TO COMPLETE THE PATH TO AVOID ANY TYPOS. 

    Start Analyzing videos using DLC! 

        All the settings are already set up correctly! You don't have to change anything, just run the following command!  

            Command: python3 run_DLC_process_videos.py 

        This command will give you trajectory plots, annotated videos and coordinate .h5 files. 

        We need to convert the .h5 files to coordinate CSVs to analyze them correctly. 

    Convert .h5 coordinate files to .csv 

        Command: python3 get_coords.py 


All the processed files will be in the /Testing folder! 

Done!!!! 

------------------------------------------------------------------- 

SECTION 2 (Supplement): Handing Transition videos (day_to_night, night_to_day): 

 ———COMING SOON——— 

------------------------------------------------------------------- 


Resources -  

DLC Docstring (to tweak commands and parameters – only do if you are curious. Make a copy of the project, don't alter the main project folder. ) - https://github.com/DeepLabCut/DeepLabCut/wiki/DOCSTRINGS  