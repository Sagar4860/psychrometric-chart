import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
import streamlit as st

st.set_page_config(
    page_title="Psychrometric Chart Tool",
    layout="wide",
    menu_items={
        "Get help": None,
        "Report a bug": None,
        "About": None
    }
)
st.markdown(
    """
    <style>
        #MainMenu {visibility: hidden;}
        footer {visibility: hidden;}
        header {visibility: hidden;}
    </style>
    """,
    unsafe_allow_html=True
)
st.markdown(
    """
    <div style="
        position: fixed;
        bottom: 10px;
        right: 15px;
        font-size: 12px;
        color: gray;">
        Internal HVAC Tool – Prototype
    </div>
    """,
    unsafe_allow_html=True
)

# ===============================
# CONSTANTS
# ===============================
P_ATM = 101.325
T_MIN, T_MAX = -10, 50
W_MAX = 30

# ===============================
# PSYCHROMETRIC FUNCTIONS
# ===============================

def saturation_pressure(T):
    return 0.61078 * np.exp((17.27 * T) / (T + 237.3))

def humidity_ratio(T, RH):
    Pw = RH * saturation_pressure(T)
    return 0.622 * Pw / (P_ATM - Pw)

def humidity_ratio_saturation(T):
    return humidity_ratio(T, 1.0)

def enthalpy(T, W):
    return 1.006 * T + W * (2501 + 1.86 * T)

def humidity_ratio_from_enthalpy(h, T):
    return (h - 1.006 * T) / (2501 + 1.86 * T)

# ===============================
# PROCESS PLOTTING (UNCHANGED)
# ===============================

def plot_straight_process(ax, T1, RH1, T2, RH2, color, mode_text):
    W1 = humidity_ratio(T1, RH1) * 1000
    W2 = humidity_ratio(T2, RH2) * 1000

    ax.plot([T1, T2], [W1, W2], color=color, linewidth=3)
    ax.scatter([T1, T2], [W1, W2], color=color, s=90, zorder=5)

    ax.vlines([T1, T2], ymin=0, ymax=[W1, W2],
              colors=color, linestyles='dotted', linewidth=1)
    ax.hlines([W1, W2], xmin=T_MIN, xmax=[T1, T2],
              colors=color, linestyles='dotted', linewidth=1)

    ax.text(T1 + 0.4, W1 + 0.4,
            f"({T1:.1f}°C, {RH1*100:.1f}%)",
            fontsize=10, color=color)

    ax.text(T2 + 0.4, W2 + 0.4,
            f"({T2:.1f}°C, {RH2*100:.1f}%)",
            fontsize=10, color=color)

    ax.text((T1 + T2)/2 + 0.5, (W1 + W2)/2,
            mode_text, fontsize=12,
            fontweight='bold', color=color)

# ===============================
# STREAMLIT UI
# ===============================

st.set_page_config(layout="wide")
st.title("🌡️ Psychrometric Chart – Multi-Process HVAC Tool")

num_processes = st.number_input(
    "Number of processes to plot",
    min_value=1, max_value=10, value=1
)

processes = []

for p in range(num_processes):
    st.markdown(f"## 🔹 Process {p+1}")

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("### Point 1")
        n1 = st.slider("Number of readings", 1, 10, 3, key=f"n1_{p}")
        T1_vals = [st.number_input(f"T1-{i+1} (°C)", key=f"T1_{p}_{i}") for i in range(n1)]
        RH1_vals = [
            st.number_input(
                f"RH1-{i+1} (%)",
                min_value=0.0,
                max_value=100.0,
                value=50.0,
                step=0.1,
                key=f"RH1_{p}_{i}"
            )
            for i in range(n1)
        ]


    with col2:
        st.markdown("### Point 2")
        n2 = st.slider("Number of readings ", 1, 10, 3, key=f"n2_{p}")
        T2_vals = [st.number_input(f"T2-{i+1} (°C)", key=f"T2_{p}_{i}") for i in range(n2)]
        RH2_vals = [
            st.number_input(
                f"RH2-{i+1} (%)",
                min_value=0.0,
                max_value=100.0,
                value=50.0,
                step=0.1,
                key=f"RH2_{p}_{i}"
            )
            for i in range(n2)
        ]


    mode = st.selectbox("Mode", ["DEC", "IEC", "DX", "Custom"], key=f"mode_{p}")
    color = st.color_picker("Color", "#FF0000", key=f"color_{p}")

    processes.append({
        "T1": np.mean(T1_vals),
        "RH1": np.mean(RH1_vals) / 100.0,
        "T2": np.mean(T2_vals),
        "RH2": np.mean(RH2_vals) / 100.0,
        "mode": mode,
        "color": color
    })

# ===============================
# PLOT BUTTON
# ===============================

if st.button("📈 Plot Chart"):
    fig, ax = plt.subplots(figsize=(14, 9))

    # ======== CHART CODE (UNCHANGED) ========
    T = np.linspace(T_MIN, T_MAX, 700)
    W_sat = humidity_ratio_saturation(T) * 1000

    ax.plot(T, W_sat, color='black', linewidth=2)

    for RH in np.arange(0.1, 1.0, 0.1):
        W = humidity_ratio(T, RH) * 1000
        ax.plot(T, W, color='brown', linewidth=1)
        idx = np.argmin(np.abs(T - 30))
        ax.text(T[idx] + 0.5, W[idx], f"{int(RH*100)}%",
                fontsize=9, color='brown')

    for W in range(0, W_MAX + 1, 2):
        ax.hlines(W, xmin=T_MIN, xmax=T_MAX,
                  colors='gray', linewidth=0.6)
        ax.text(T_MAX + 0.5, W, f"{W}", va='center', fontsize=9)

    for Tdb in range(T_MIN, T_MAX + 1, 5):
        ax.vlines(Tdb, ymin=0, ymax=W_MAX,
                  colors='lightgray', linewidth=0.5)

    for h in range(10, 130, 5):
        W_h = humidity_ratio_from_enthalpy(h, T)
        W_sat_kg = humidity_ratio_saturation(T)
        mask = (W_h >= 0) & (W_h <= W_sat_kg)
        ax.plot(T[mask], W_h[mask] * 1000,
                color='green', linewidth=1)

    for h in range(10, 130, 5):
        for Ti in T:
            Wi = humidity_ratio_saturation(Ti)
            hi = enthalpy(Ti, Wi)
            if abs(hi - h) < 0.3:
                ax.text(Ti - 3, Wi * 1000,
                        f"{h-5}", color='green', fontsize=9)
                break

    # ======== MULTIPLE PROCESSES ========
    for proc in processes:
        plot_straight_process(
            ax,
            proc["T1"], proc["RH1"],
            proc["T2"], proc["RH2"],
            proc["color"], proc["mode"]
        )

    ax.set_xlim(T_MIN, T_MAX)
    ax.set_ylim(0, W_MAX)
    ax.set_xlabel("Dry Bulb Temperature (°C)")
    ax.set_ylabel("Humidity Ratio (g/kg dry air)")
    ax.set_title(
        "Psychrometric Chart (101325 Pa)\n"
        "Annotated Points, Projections & Multiple Modes"
    )

    ax.grid(False)
    plt.tight_layout()
    st.pyplot(fig)
