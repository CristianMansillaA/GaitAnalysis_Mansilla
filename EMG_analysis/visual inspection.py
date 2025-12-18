"""
Interactive EMG viewer with rectified EMG and TKEO
--------------------------------------------------
Controls:
- Right click: mark onset
- Left click: mark offset
- Left arrow: move window backward
- Right arrow: move window forward
"""

from pathlib import Path
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from scipy.signal import butter, filtfilt

# ============================================================
# -------------------- CONFIGURATION --------------------------
# ============================================================

FS = 1500  # Sampling frequency (Hz)
WINDOW_STEP = 2  # seconds

DATA_DIR = Path("data")
FILE_NAME = "Post_fatigue.txt"

MUSCLES = [
    "RT RECTUS FEM.,uV",
    "RT BICEPS FEM.,uV",
    "RT LAT. GASTRO,uV",
    "LT RECTUS FEM.,uV",
    "LT TIB.ANT.,uV",
    "LT BICEPS FEM.,uV",
    "LT LAT. GASTRO,uV",
    "RT TIB.ANT.,uV",
]

TARGET_MUSCLE_1 = 4  # LT TIB.ANT
TARGET_MUSCLE_2 = 6  # LT LAT. GASTRO

# ============================================================
# -------------------- DATA LOADING ---------------------------
# ============================================================

def load_emg(file_path: Path) -> pd.DataFrame:
    """Load EMG txt file."""
    return pd.read_csv(file_path, header=4, delimiter="\t")


# ============================================================
# -------------------- SIGNAL PROCESSING ----------------------
# ============================================================

def bandpass_filter(signal, fs, low=10, high=150, order=2):
    b, a = butter(order, [low, high], btype="bandpass", fs=fs)
    return filtfilt(b, a, signal)


def emg_filter_rectified(signal, fs):
    filtered = bandpass_filter(signal, fs)
    return np.abs(filtered)


def emg_filter_for_tkeo(signal, fs):
    filtered = bandpass_filter(signal, fs)
    rectified = np.abs(filtered)

    # Low-pass for TKEO mask
    lowpass = 8
    b, a = butter(2, lowpass, btype="lowpass", fs=fs)
    return filtfilt(b, a, rectified)


def compute_tkeo(signal):
    """Teager–Kaiser Energy Operator."""
    tkeo = np.square(signal[1:-1]) - signal[:-2] * signal[2:]
    return np.concatenate(([0], tkeo, [0]))


# ============================================================
# -------------------- MAIN SCRIPT ----------------------------
# ============================================================

def main():

    # Load data
    dt = load_emg(DATA_DIR / FILE_NAME)
    time = dt["Time,s"].to_numpy()

    # Select muscles
    emg_raw1 = dt[MUSCLES[TARGET_MUSCLE_1]].to_numpy()
    emg_raw2 = dt[MUSCLES[TARGET_MUSCLE_2]].to_numpy()

    # Process EMG
    emg1 = emg_filter_rectified(emg_raw1, FS)
    emg2 = emg_filter_rectified(emg_raw2, FS)

    tkeo1 = compute_tkeo(emg_filter_for_tkeo(emg_raw1, FS))
    tkeo2 = compute_tkeo(emg_filter_for_tkeo(emg_raw2, FS))

    # ========================================================
    # -------------------- PLOTTING --------------------------
    # ========================================================

    fig, axs = plt.subplots(4, 1, sharex=True, figsize=(10, 8))

    t_start, t_end = 0, WINDOW_STEP

    emg_line1, = axs[0].plot(time, emg1, color="blue")
    axs[0].set_ylabel("EMG (uV)")

    tkeo_line1, = axs[1].plot(time, tkeo1, color="blue")
    axs[1].set_ylabel("TKEO")

    emg_line2, = axs[2].plot(time, emg2, color="green")
    axs[2].set_ylabel("EMG (uV)")

    tkeo_line2, = axs[3].plot(time, tkeo2, color="green")
    axs[3].set_ylabel("TKEO")
    axs[3].set_xlabel("Time (s)")

    for ax in axs:
        ax.set_xlim(t_start, t_end)

    onset, offset = [], []

    # ========================================================
    # -------------------- INTERACTION -----------------------
    # ========================================================

    def onclick(event):
        if event.inaxes != axs[0]:
            return
        if event.button == 3:
            onset.append(event.xdata)
            axs[0].axvline(event.xdata, color="red", linestyle="--")
        elif event.button == 1:
            offset.append(event.xdata)
            axs[0].axvline(event.xdata, color="black", linestyle="--")
        fig.canvas.draw_idle()

    def onkey(event):
        nonlocal t_start, t_end

        if event.key == "right":
            t_start += WINDOW_STEP
            t_end += WINDOW_STEP
        elif event.key == "left":
            t_start -= WINDOW_STEP
            t_end -= WINDOW_STEP
        else:
            return

        for ax in axs:
            ax.set_xlim(t_start, t_end)

        fig.canvas.draw_idle()

    fig.canvas.mpl_connect("button_press_event", onclick)
    fig.canvas.mpl_connect("key_press_event", onkey)

    print("""
Controls:
- Right click: mark onset
- Left click: mark offset
- Left arrow: move window backward
- Right arrow: move window forward
""")

    plt.tight_layout()
    plt.show()


# ============================================================
# -------------------- ENTRY POINT ----------------------------
# ============================================================

if __name__ == "__main__":
    main()

