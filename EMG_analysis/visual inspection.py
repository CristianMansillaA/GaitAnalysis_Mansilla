import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from scipy import signal
from scipy.signal import butter, lfilter, filtfilt

#%%
#This section is to use the post fatigue data, unlock it when necessary only
st = "post" #set if the data is pre or post fatigue (all the data need to be in the same folder
n_t = 1 # Number of the participant
n_mus = 1 #Muscle to evaluate individually in the next 
user = "crist"
#dt = pd.read_csv(r"C:\\Users\\crist\\OneDrive - University of Leeds\\UoLeeds\Lab stuff\\Abbys - Aneeka's proyect\\"+ st +"-fatigue test "+ str(n_t)+ " emg.txt", header= 4, delimiter="\t")
#dt = pd.read_csv(r"C:\Users\bs22cama\Downloads\Pre fatigue walking2.0.txt", header= 4, delimiter="\t")
dt = pd.read_csv(r"C:\Users\crist\OneDrive - University of Leeds\UoLeeds\Lab stuff\Exeter protocol testing\Post fatigue.txt", header = 4, delimiter = "\t" )
s_f=1500
#Cut of the signal to erase the holding phase
#data = dt[(dt["Time,s"] <= 38) & (dt["Time,s"] >= 0)]
time = dt["Time,s"]
#muscles = ["LT TIB.ANT.,uV","LT LAT. GASTRO,uV","LT BICEPS FEM.,uV","RT TIB.ANT.,uV","RT LAT. GASTRO,uV","RT BICEPS FEM.,uV","LT MED. GASTRO,uV","RT MED. GASTRO,uV"]
muscles = ["RT RECTUS FEM.,uV","RT BICEPS FEM.,uV","RT LAT. GASTRO,uV","LT RECTUS FEM.,uV","LT TIB.ANT.,uV","LT BICEPS FEM.,uV","LT LAT. GASTRO,uV", "RT TIB.ANT.,uV"]
timeEMG=np.linspace(0, len(dt["Time,s"])/s_f, num=len(dt["Time,s"]))
freq = 1/np.mean(np.diff(timeEMG))
bb_no = dt[muscles[n_mus]]
bb= np.absolute(bb_no)

print(time)
#%%
r_RF = dt[muscles[0]]
r_BF = dt[muscles[1]]
r_LG = dt[muscles[2]]
l_RF = dt[muscles[3]]
l_TA = dt[muscles[4]]
l_BF = dt[muscles[5]]
l_LG = dt[muscles[6]]
r_TA = dt[muscles[7]] 

#dic_mus = [l_TA, r_TA, l_GL, r_GL, l_GM, r_GM, l_BF, r_BF]


print(len(time))


#%%

def emg_filter_for_TKEO(emg_signal):
    emg = emg_signal
    #Filtering the raw data
    b, a = butter(2, ([10, 150]/(freq/2)), btype='bandpass')
    dataf_pre = filtfilt(b,a,emg)
    absSignal_pre = np.absolute(dataf_pre)

    #Creating a mask to obtain the use the TKEO
    lowp = 8
    sfreq = s_f
    low_pass = lowp/sfreq
    b, a = butter(2, low_pass, btype='lowpass')
    mask_emg_filtered = filtfilt(b, a, absSignal_pre)
    return mask_emg_filtered

def emg_filter_rectified(emg_signal):
    emg = emg_signal
    #Filtering the raw data
    b, a = butter(2, ([10, 150]/(freq/2)), btype='bandpass')
    dataf_pre = filtfilt(b,a,emg)
    emg_final = np.absolute(dataf_pre)
    return emg_final


#%%

# Generate sample EMG signal
fs = 1500  # Hz
duration = len(time) / fs  # seconds
t = time
emg_raw = l_TA  #Choose the targeted muscle
emg = emg_filter_rectified(emg_raw)
emg_TKEO = emg_filter_for_TKEO(emg_raw)

emg_raw2 = l_LG  #Choose the targeted muscle
emg2 = emg_filter_rectified(emg_raw2)
emg_TKEO2 = emg_filter_for_TKEO(emg_raw2)


# Create figure with two subplots
fig, axs = plt.subplots(nrows=4, sharex=True)

# Set initial time window to display
t_start = 0
t_end = 2

# Create EMG subplot
emg_line, = axs[0].plot(t, emg, color='blue')
axs[0].set_ylabel('EMG (uV)')

# Create EMG subplot
emg_line, = axs[2].plot(t, emg2, color='green')
axs[2].set_ylabel('EMG (uV)')

# Create TKEO subplot
filtered_tkeo_emg = np.square(emg_TKEO[1:-1]) - emg_TKEO[:-2] * emg_TKEO[2:]
filtered_tkeo_emg = np.concatenate(([0], filtered_tkeo_emg, [0]))  # Add two zeros
tkeo_line, = axs[1].plot(t, filtered_tkeo_emg, color='blue')  # Adjusted TKEO length
axs[1].set_ylabel('TKEO')

filtered_tkeo_emg = np.square(emg_TKEO2[1:-1]) - emg_TKEO2[:-2] * emg_TKEO2[2:]
filtered_tkeo_emg = np.concatenate(([0], filtered_tkeo_emg, [0]))  # Add two zeros
tkeo_line, = axs[3].plot(t, filtered_tkeo_emg, color='green')  # Adjusted TKEO length
axs[3].set_ylabel('TKEO')

# Set x limits of subplots to initial time window
axs[0].set_xlim(t_start, t_end)
axs[2].set_xlim(t_start, t_end)
#axs[1].set_ylim(-0.05,0.06)

# Initialize onset and offset variables
onset = []
offset = []

# Define function to handle mouse clicks on EMG subplot
def onclick(event):
    global onset, offset
    if event.button == 3:  # right click for onset
        onset.append(event.xdata)
        axs[0].axvline(event.xdata, color='red', linestyle='--')
    elif event.button == 1:  # left click for offset
        offset.append(event.xdata)
        axs[0].axvline(event.xdata, color='black', linestyle='--')
    fig.canvas.draw()

# Attach onclick function to figure
fig.canvas.mpl_connect('button_press_event', onclick)

# Define function to handle keyboard events
def onkey(event):
    global t_start, t_end
    if event.key == 'right':  # move time window forward by 2 seconds
        t_start += 2
        t_end += 2
    elif event.key == 'left':  # move time window backward by 2 seconds
        t_start -= 2
        t_end -= 2

    # Update x limits
    axs[0].set_xlim(t_start, t_end)
    axs[1].set_xlim(t_start, t_end)
    axs[2].set_xlim(t_start, t_end)
    axs[3].set_xlim(t_start, t_end)

    # Update EMG data within the window
    emg_window = emg[(t >= t_start) & (t <= t_end)]
    emg_line.set_data(t[(t >= t_start) & (t <= t_end)], emg_window)
    
    # Update EMG data within the window
    emg_window2 = emg2[(t >= t_start) & (t <= t_end)]
    emg_line.set_data(t[(t >= t_start) & (t <= t_end)], emg_window2)

    # Update TKEO data within the window
    filtered_tkeo_emg_window = filtered_tkeo_emg[(t >= t_start) & (t <= t_end)]
    tkeo_line.set_data(t[(t >= t_start) & (t <= t_end)], filtered_tkeo_emg_window)

    fig.canvas.draw()

# Attach onkey function to figure
fig.canvas.mpl_connect('key_press_event', onkey)

# Show plot
plt.show()
