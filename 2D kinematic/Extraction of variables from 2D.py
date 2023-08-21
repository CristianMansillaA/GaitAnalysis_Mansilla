import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
import math
import pandas as pd

#%%  (The #%% are to separate the code in the Spyder software)
#Here you have to change the file_path to the one produced after the analysis of the video in 3DVideoPose.
#The file is a .npy file, with 3 columns (x,y and visibility), there is 17 anatomical keypoints represented by the rows.
# The frames are represented by the third dimension of the data. 


file_path = r"C:\Users\crist\OneDrive - University of Leeds\UoLeeds\Lab stuff\3D kinematic analysis and code\post2_output.txt.npy"

keypoints_d = np.load(file_path)

#%% 
def extract_length_sections(key1,key2, keypoint_data):
    # Iterate through the third dimension (frames), extracting the distance between key1 and key2. 
    save_data = []
    for i in range(len(keypoint_data)):
        sample_keypoints = keypoint_data[i]
        x1, y1, v1 = sample_keypoints[key1]
        x2, y2, v2 = sample_keypoints[key2]
        
        distance = math.sqrt((x2 - x1)**2 + (y2 - y1)**2)
        save_data.append(distance)
    return np.array(save_data)

def extract_midpoint(key1, key2, keypoint_data):
    # Create an empty DataFrame to store the midpoint data
    midpoint_df = pd.DataFrame(columns=['x_midpoint', 'y_midpoint'])
    
    # Iterate through the frames and calculate the midpoints for the selected key1 and key2
    for i in range(len(keypoint_data)):
        sample_keypoints = keypoint_data[i]
        x1, y1, v1 = sample_keypoints[key1]
        x2, y2, v2 = sample_keypoints[key2]
        
        x_midpoint = (x1 + x2) / 2
        y_midpoint = (y1 + y2) / 2
        
        # Append the midpoint data to the DataFrame
        midpoint_df = pd.concat([midpoint_df, pd.DataFrame({'x_midpoint': [x_midpoint], 'y_midpoint': [y_midpoint]})], ignore_index=True)
    
    return midpoint_df


def extract_length_pelvis_midfoot(key1, keypoint_data, data_frame):
    # Iterate through the frames and save the data
    distances = []
    for i in range(len(keypoint_data)):
        sample_keypoints = keypoint_data[i]
        x1, y1, v1 = sample_keypoints[key1]
        x2 = data_frame.iloc[i,0].astype(float)
        y2 = data_frame.iloc[i,1].astype(float)
        
        distance = math.sqrt((x2 - x1)**2 + (y2 - y1)**2)
        distances.append(distance)
    return np.array(distances)

def extract_distance_legreal(key1, key2, key3, key4, keypoint_data):
    full_leg = []
    
    # Iterate through the keypoints and calculate the midpoints for the selected sample
    for i in range(len(keypoint_data)):
        sample_keypoints = keypoint_data[i]
        x1, y1, v1 = sample_keypoints[key1]
        x2, y2, v2 = sample_keypoints[key2]
        
        x3, y3, v3 = sample_keypoints[key3]
        x4, y4, v4 = sample_keypoints[key4]
        
        distance_left = math.sqrt((x2 - x1)**2 + (y2 - y1)**2)
        distance_right = math.sqrt((x4 - x3)**2 + (y4 - y3)**2)
        
        if distance_left > distance_right:
            full_leg.append(distance_left)
        else:
            full_leg.append(distance_right)
        
    return np.array(full_leg)


#The next section is going to extract all of the distances and create a excel file with multiple columns. Each column is a different distance.
#The keypoints are based in the provides by 3DVideoPose, but other machine learning change the keypoints numbers, if you are working with other
#keypoints is better to change the numbers below. Currently the keypoints in 3DVideoPose are:

# 0 = Bottom torso, 1 = Left hip, 2 = Left knee, 3 = Left foot, 4 = Right hip, 5 = Right knee, 6 = Right foot
# 7 = Centre torso, 8 = Upper torso, 9 = Neck base, 10 = centre head
# 11 = Right shoulder, 12 = Right elbow, 13 = Right hand, 14 = Left shoulder, 15 = Left elbow, 16 = Left hand. 

def csv_distances(keypoints, file_name):
    #This section calculates multiple distances between multiple combination of keypoints using the previos functions.
    distance_headpelvis = extract_length_sections(0, 10, keypoints_d)
    distance_pelvisfoot_left = extract_length_sections(3, 0, keypoints_d)
    distance_pelvisfoot_right = extract_length_sections(6,0, keypoints_d)
    distance_arm_rigth = extract_length_sections(11, 12, keypoints_d)
    distance_arm_left = extract_length_sections(14, 15, keypoints_d)
    distance_forearm_rigth = extract_length_sections(12, 13, keypoints_d)
    distance_forearm_left = extract_length_sections(15, 16, keypoints_d)    
    distance_thigh_rigth = extract_length_sections(4, 5, keypoints_d)
    distance_thigh_left = extract_length_sections(1, 2, keypoints_d)
    distance_calf_rigth = extract_length_sections(5, 6, keypoints_d)
    distance_calf_left = extract_length_sections(2, 3, keypoints_d)
    distance_betweenpelvis = extract_length_sections(4, 1, keypoints_d)  
    
    df_midpoints = extract_midpoint( 6, 3, keypoints_d)
    
    distance_pelvis_averagefeet = extract_length_pelvis_midfoot(0, keypoints_d, df_midpoints)

    distance_totalbody = extract_length_pelvis_midfoot(10, keypoints_d, df_midpoints)

    proportion_lowerbody = np.array((distance_pelvis_averagefeet*100)/distance_totalbody)
    proportion_upperbody = np.array((distance_headpelvis*100)/distance_totalbody)
    
    leg_real_ground = extract_distance_legreal(3,1, 6, 4, keypoints_d)
    
    #this section is going to save the information inside the excel file
    
    # Create a dictionary with variable names as keys and corresponding data as values
    data = {"head_pelvis": distance_headpelvis, 'rigth_arm': distance_arm_rigth , 'left_arm': distance_arm_left, 
            "rigth_forearm": distance_forearm_rigth, "left_forearm": distance_forearm_left, "rigth_thight": distance_thigh_rigth,
            "left_thight": distance_thigh_left, "rigth_calf": distance_calf_rigth, "left_calf": distance_calf_left,
            "hip_to_hip": distance_betweenpelvis, "pelvis_average_feet": distance_pelvis_averagefeet, 
            "proportion_lowerbody": proportion_lowerbody, "proportion_upperbody": proportion_upperbody, 
            "leg_ground_full": leg_real_ground}

    # Create a data frame from the dictionary, so later can be saved as a excel file.
    df = pd.DataFrame(data)

    # Specify the output file path and folder in which you want to save the new file.
    output_folder = r"C:\Users\crist\OneDrive - University of Leeds\UoLeeds\Lab stuff\Video Track"
    output_file = output_folder + file_name

    # Save the data frame to an Excel file
    df.to_excel(output_file, index=False)
    
#%%
#file name should have the structure: '\\file_name.xlsx'
file = '\\post_fatigue_subject1.xlsx'

csv_distances(keypoints_d, file)
