import cv2
file_name = "SAEEGEMGPhT_SleepD_GCaMP_10192022_517.mp4"
day_to_night = True
night_to_day = False
cap = cv2.VideoCapture(file_name)
# Get frame count
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
print(identified_frame)
print("only using a within 30 frame window.")

initial = identified_frame[0] # first frame
end = identified_frame[-1] # last frame
for i in range(len(identified_frame)-1):
    if identified_frame[i+1] - initial <= 30:
        i=i+1
    else:
        end = identified_frame[i-1]

print("Done")
print("Saving frames")
print("Total transitioning frames: ",end-initial)
cap = cv2.VideoCapture(file_name)
start = initial - 2
stop = end + 2
for i in range(start, stop):
    print("i: ", i)
    cap.set(cv2.CAP_PROP_POS_FRAMES,i)
    ret,frame = cap.read()
    cv2.imwrite("frame_{}.jpg".format(i), frame)
    i = i+1

print("Done saving frames")



