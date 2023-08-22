# -*- coding: utf-8 -*-
"""
Created on Tue Aug 22 13:37:26 2023

@author: crist
"""
import matplotlib.pyplot as plt
import matplotlib.animation as animation
import numpy as np
import pandas as pd

#%%
def transpose_data(dataframe):
    #This function prepares the data to be plotted. In data1 the first and last columns are eliminated (do not contain usuful information)
    data1 = dataframe.iloc[:,1:-1]
    #Data2 and data3 are lines in which the data is reestructured to be plotted with a X,Y shape together with the dimension of frames.
    data2 = data1.values.reshape(len(data1[1]),118,24)
    #(number of frames, heigth, length )
    data3 = data2.transpose(0,2,1)
    return data3

#Open txt or CSV file. If text file change the delimiter to "\t".
dt1 = pd.read_csv(r"C:\Users\crist\OneDrive - University of Leeds\UoLeeds\Lab stuff\Exeter protocol testing\AS - walking pre fatigue.txt", header= None, delimiter=",")
dt = dt1.fillna(0)

#This line contains the transpose data ready to be used.
data_gait_t = transpose_data(dt)

#%%
#file name should have the structure: '\\file_name.xlsx'
#The folder is fixed into the last section of the code, it can be changed there.
file = '\\gait_variables_pre_s1.xlsx'

#This threshold set the minimun intensity of preasure to be plotted.
threshold = 60
thresh = data_gait_t > threshold
#Z is the number of frames, it need to be change every time you change the file, because each file have different amount of frames
#Z is the amount of frames in "data_gait2" -1
z = 747

fig, ax = plt.subplots(figsize= (45,5))
txt = fig.text(0.12, 0.14, '', backgroundcolor="w")

cx = ax.contourf(data_gait_t[10,:,:], cmap="CMRmap")


#The X and Y coordinates of the clicks. Use left click of the mouse to extract the heels contacts and the right click of the mouse to store the anterior foot.
x_coordinates = []
y_coordinates = []
anterior_foot_x = []
anterior_foot_y = []
# Create a list to store the frame numbers corresponding to each click
clicked_frames = []

#Saved distances
distances = []

line, = ax.plot(x_coordinates, y_coordinates, color='r', marker='o')

# Function to calculate the Euclidean distance between two points (X1, Y1) and (X2, Y2)
def calculate_distance(x1, y1, x2, y2):
    return np.sqrt((x2 - x1)**2 + (y2 - y1)**2)

def update_time():
    t = 0
    t_max = z
    while t<t_max:
        t += anim.direction
        yield t

def update_plot(t):
    ax.clear()
    txt.set_text("Frame: %s" % t)
    contour = ax.contourf(thresh[t,:,:], cmap="CMRmap")
    contour.set_array(thresh[t,:,:].ravel())
    fig.canvas.draw()
    return contour

#This funtion give to option to "pause", and move with arrows to new frames of the "video".
def on_press(event):
    if event.key.isspace():
        if anim.running:
            anim.event_source.stop()
        else:
            anim.event_source.start()
        anim.running ^= True
    elif event.key == 'left':
        anim.direction = -1
    elif event.key == 'right':
        anim.direction = +1

    # Manually update the plot
    if event.key in ['left','right']:
        t = next(anim.frame_seq)
        update_plot(t)
        plt.draw()

# This function store the coordinates of X and Y when you click with the mouse in the 2D plot.
def on_pick(event):
    m_x, m_y = event.x, event.y
    x, y = ax.transData.inverted().transform([m_x, m_y])

    if event.button == 1:  # Left-click event
        x_coordinates.append(x)
        y_coordinates.append(y)
        line.set_xdata(x_coordinates)
        line.set_ydata(y_coordinates)

        # Store the current frame number corresponding to the click
        clicked_frames.append(int(anim.frame_seq.__next__()))

        # Calculate the distance between two consecutive clicks (if there are at least two clicks)
        if len(x_coordinates) >= 2:
            x1, y1 = x_coordinates[-2], y_coordinates[-2]  # Previous click coordinates
            x2, y2 = x_coordinates[-1], y_coordinates[-1]  # Current click coordinates
            distance = calculate_distance(x1, y1, x2, y2)
            distances.append(distance)
    elif event.button == 3:  # Right-click event
        anterior_foot_x.append(x)
        anterior_foot_y.append(y)


# This function is used to save the collected data to an Excel file
def save_data_to_excel(file_name):
    # Determine the maximum length among all lists
    max_length = max(len(clicked_frames), len(x_coordinates), len(y_coordinates), len(distances), len(anterior_foot_x), len(anterior_foot_y))

    # Create dictionaries for each list, filling with NaN values as needed
    clicked_dict = {'Frame': clicked_frames + [np.nan] * (max_length - len(clicked_frames))}
    x_coord_dict = {'X Coordinate': x_coordinates + [np.nan] * (max_length - len(x_coordinates))}
    y_coord_dict = {'Y Coordinate': y_coordinates + [np.nan] * (max_length - len(y_coordinates))}
    distance_dict = {'Distance': distances + [np.nan] * (max_length - len(distances))}
    anterior_x_dict = {'X Anterior Feet': anterior_foot_x + [np.nan] * (max_length - len(anterior_foot_x))}
    anterior_y_dict = {'Y Anterior Feet': anterior_foot_y + [np.nan] * (max_length - len(anterior_foot_y))}

    # Create separate DataFrames for each dictionary
    clicked_df = pd.DataFrame(clicked_dict)
    x_coord_df = pd.DataFrame(x_coord_dict)
    y_coord_df = pd.DataFrame(y_coord_dict)
    distance_df = pd.DataFrame(distance_dict)
    anterior_x_df = pd.DataFrame(anterior_x_dict)
    anterior_y_df = pd.DataFrame(anterior_y_dict)

    # Concatenate all DataFrames horizontally
    df = pd.concat([clicked_df, x_coord_df, y_coord_df, distance_df, anterior_x_df, anterior_y_df], axis=1)

    # Specify the output file path and folder in which you want to save the new file.
    output_folder = r"C:\Users\crist\OneDrive - University of Leeds\UoLeeds\Lab stuff\Video Track"
    output_file = output_folder + file_name
    # Save the data frame to an Excel file
    df.to_excel(output_file, index=False)
    print("Data saved to collected_data.xlsx")


# Connect the event handlers to the canvas
fig.canvas.mpl_connect('key_press_event', on_press)
fig.canvas.mpl_connect('button_press_event', on_pick)

# Create a button to save the collected data to Excel
ax_save = plt.axes([0.7, 0.02, 0.1, 0.05])
btn_save = plt.Button(ax_save, 'Save', color='lightgoldenrodyellow', hovercolor='0.975')
btn_save.on_clicked(lambda event: save_data_to_excel(file))

# Start the animation
anim = animation.FuncAnimation(fig, update_plot, frames=update_time, interval=1000, repeat=True)
anim.running = True
anim.direction = +1
plt.show()
