# Script to get coordinates and likelihood in one clean csv/video
# Get all .h5 files

import pandas as pd
from pandas import IndexSlice as idx 
import os

print("------- Converting to Coordinate CSV :) -----")
# return all files as a list
files = []
# Change to the directory with your .h5 files 
# (usually the direcoty where you put your videos for analysis)
# directory = '/storage1/fs1/yaochen/Active/DLC/Circle_Cage/Testing/'
directory = '/storage1/fs1/yaochen/Active/DLC/Final_Models/day/Testing/'
for file in os.listdir(r'{}'.format(directory)):
     # check the files which are end with specific extension
    if file.endswith("_filtered.h5"):
        # print path name of selected files
        print(os.path.join(r'{}'.format(directory), file))
        files.append(file)

try:
  os.mkdir('{}'.format(directory+'coords_csv'))
except FileExistsError  as e:
  print("folder exists! Continuing")

for i in range(len(files)):
  df = pd.read_hdf('{}'.format(directory+files[i]))
  df.columns = df.columns.droplevel()
  temp_df = pd.DataFrame()
  feature_names = df.columns.levels[0].to_list()
  col_list = df.columns.levels[1].to_list()
  count = len(df.columns)
  for j in range(count):
    temp_df['{}'.format(df.columns[j][0] + '_' + df.columns[j][1])] = df[df.columns[j]].copy()
  temp_df = temp_df.reset_index()
  temp_df = temp_df.rename(columns={'index':'frames'})
  temp_df.to_csv('{}'.format(directory+'coords_csv/'+ 'Coord'+files[i][:-3]) + '.csv')

print("------ DONE!!!! ------")