# streamlit_app.py
import streamlit as st
import matplotlib.pyplot as plt
import math
import statistics
import pandas as pd # For nice table display

# --- Data (Hardcoded) ---
def time_str_to_seconds(time_str):
    """Converts M:SS.ss or SS.ss string to seconds."""
    if ':' in time_str:
        try:
            minutes, seconds = map(float, time_str.split(':'))
            return minutes * 60 + seconds
        except ValueError: return math.inf
    else:
        try: return float(time_str)
        except ValueError: return math.inf

race_data = {
    'Race 1': { 'metadata': {'laps': 1, 'description': 'Single Lap Course'}, 'drivers': {
            'Shaun': {'car': 23, 'times': [26.60, 27.06, 26.93, 27.18, 25.67, 26.17]},
            'Erik': {'car': 56, 'times': [29.58, 27.82, 27.18, 27.14, 27.06, 26.13]},
            'Siavash': {'car': 54, 'times': [27.06, 26.93, 26.17, 26.39, 26.26, 26.60]},
            'Will': {'car': 41, 'times': [26.21, 25.88, 25.74, 26.18, 26.05, 26.18]}, }},
    'Race 2': { 'metadata': {'laps': 2, 'description': 'Double Lap with Connector'}, 'drivers': {
            'Will': {'car': 41, 'times': [62.51, 62.13, 59.73, 61.55, 60.07, 60.66, 60.45, 60.75]},
            'Shaun': {'car': 23, 'times': [64.21, 60.50, 61.28, 60.02, 61.86, 60.94, 61.51, 61.13]},
            'Siavash': {'car': 54, 'times': [64.33, 64.12, 64.37, 64.19, 63.48, 62.09, 62.31, 61.89]},
            'Erik': {'car': 56, 'times': [67.84, 63.96, 63.50, 63.43, 62.47, 62.34, 61.78, 62.13]}, }}
}
all_drivers = list(race_data['Race 1']['drivers'].keys())
# Use a consistent color map for drivers across plots
driver_colors_map = {name: color for name, color in zip(all_drivers, plt.cm.get_cmap('tab10').colors)}

# --- Track Processing & Spline Functions ---
# Track points definition (relative coordinates, Y increases downwards implicitly)
all_raw_points = [
    (100, -70), (40, -90), (10, -70), (15, -40), (60, -20), (70, 20), (30, 35),
    (-20, 35), (-40, 0), (0, -15), (-50, -30), (-90, -30), (-100, 20), (-100, 90),
    (-40, 100), (70, 110)
]
MAIN_COURSE_START_INDEX, MAIN_COURSE_FINISH_INDEX = 0, 13
CONNECTOR_POINT_14_INDEX, CONNECTOR_POINT_15_INDEX = 14, 15
main_course_control_indices = list(range(MAIN_COURSE_FINISH_INDEX + 1))
connector_control_indices = [ MAIN_COURSE_FINISH_INDEX, CONNECTOR_POINT_14_INDEX, CONNECTOR_POINT_15_INDEX, MAIN_COURSE_START_INDEX ]

# --- Spline Generation Functions ---
def catmull_rom_point(p0, p1, p2, p3, t):
    t2=t*t; t3=t2*t
    x = 0.5*((2*p1[0])+(-p0[0]+p2[0])*t+(2*p0[0]-5*p1[0]+4*p2[0]-p3[0])*t2+(-p0[0]+3*p1[0]-3*p2[0]+p3[0])*t3)
    y = 0.5*((2*p1[1])+(-p0[1]+p2[1])*t+(2*p0[1]-5*p1[1]+4*p2[1]-p3[1])*t2+(-p0[1]+3*p1[1]-3*p2[1]+p3[1])*t3)
    return x, y

def generate_spline_points(control_points, segments_per_curve=16):
    dense_points = []
    num_control = len(control_points)
    if num_control < 2: return control_points
    if control_points: dense_points.append(control_points[0])
    for i in range(num_control - 1):
        p0=control_points[max(0,i-1)]; p1=control_points[i]; p2=control_points[i+1]; p3=control_points[min(num_control-1,i+2)]
        for j in range(1, segments_per_curve + 1):
            t = j / segments_per_curve
            point_on_curve = catmull_rom_point(p0, p1, p2, p3, t)
            if not dense_points or point_on_curve != dense_points[-1]: dense_points.append(point_on_curve)
    return dense_points

# --- Track Point Processing (No scaling/centering needed here) ---
# Note: Control points derived directly from raw points for spline generation.
# Reflection/Inversion handled separately for plotting below.

def get_control_points_for_indices(indices_list, source_points):
    """Gets control points from the source list using indices."""
    return [source_points[i] for i in indices_list if 0 <= i < len(source_points)]

# Get the original-orientation control points
main_course_control_points = get_control_points_for_indices(main_course_control_indices, all_raw_points)
connector_control_points = get_control_points_for_indices(connector_control_indices, all_raw_points)

# Generate the original-orientation dense points
SEGMENTS_PER_CURVE = 16
main_course_dense_points = generate_spline_points(main_course_control_points, SEGMENTS_PER_CURVE)
connector_dense_points = generate_spline_points(connector_control_points, SEGMENTS_PER_CURVE)

# --- Analysis Functions ---
def get_valid_times(race_name, driver_name):
    try:
        times = race_data[race_name]['drivers'][driver_name]['times']
        return [t for t in times if t is not None and t != math.inf]
    except KeyError: return []

def calculate_stats(times):
    stats = {"count": len(times), "best": None, "worst": None, "average": None, "stdev": None}
    if not times: return stats
    stats["best"]=min(times); stats["worst"]=max(times); stats["average"]=sum(times)/stats["count"]
    if stats["count"] > 1:
        try: stats["stdev"] = statistics.stdev(times)
        except statistics.StatisticsError: stats["stdev"] = 0.0
    else: stats["stdev"] = 0.0
    return stats

# --- Streamlit App Layout ---
st.set_page_config(layout="wide")
st.title("Autocross Simulation & Analysis")

# --- Sidebar ---
with st.sidebar:
    st.header("Controls")
    selected_race = st.radio("Select Race", list(race_data.keys()), key="race_select")
    selected_drivers = st.multiselect(
        "Select Drivers",
        options=all_drivers,
        default=all_drivers[:1], # Default to selecting the first driver
        key="driver_select"
    )

# --- Main Area Layout ---
col1, col2 = st.columns([0.45, 0.55]) # Give analysis slightly more space

# --- Column 1: Track Visualization ---
with col1:
    st.header("🗺️ Track Layout")
    st.caption(f"Displaying layout for: {selected_race}")

    fig_track, ax_track = plt.subplots(figsize=(5.5, 5.5)) # Slightly larger figure maybe

    # --- Plot original spline points directly ---

    # Plot main course spline (using original orientation points)
    if main_course_dense_points:
        plot_main_x = [p[0] for p in main_course_dense_points]
        plot_main_y = [p[1] for p in main_course_dense_points]
        ax_track.plot(plot_main_x, plot_main_y, color='gray', linewidth=2, label='Main Course')

    # Plot connector spline (using original orientation points)
    if connector_dense_points:
        plot_conn_x = [p[0] for p in connector_dense_points]
        plot_conn_y = [p[1] for p in connector_dense_points]
        ax_track.plot(plot_conn_x, plot_conn_y, color='orange', linestyle='--', linewidth=1.5, label='Connector')

    # Plot Start/Finish markers using original control points
    if main_course_control_points:
        # Get original coordinates
        start_x_orig, start_y_orig = main_course_control_points[0]
        finish_x_orig, finish_y_orig = main_course_control_points[-1]

        # Plot markers at the original positions
        ax_track.plot(start_x_orig, start_y_orig, 'go', markersize=8, label='Start')
        ax_track.plot(finish_x_orig, finish_y_orig, 'ro', markersize=8, label='Finish')

        # Add text labels near the original points
        # Adjust text offsets based on expected final visual (after axis inversion)
        ax_track.text(start_x_orig + 5, start_y_orig - 5 , 'Start', fontsize=9, ha='left', va='bottom')
        ax_track.text(finish_x_orig - 5, finish_y_orig + 5, 'Finish', fontsize=9, ha='right', va='top')


    # --- Formatting for Correct Orientation ---
    ax_track.set_aspect('equal', adjustable='box') # Maintain aspect ratio
    ax_track.invert_yaxis() # Crucial: Flip display axis (Y increases downwards)
    ax_track.set_xticks([]) # Hide axis values
    ax_track.set_yticks([])
    ax_track.legend(fontsize='small', loc='best')
    fig_track.tight_layout()
    st.pyplot(fig_track)
    st.caption("Static visualization of the track layout.")

# --- End of code segment for column 1 ---

# --- Column 2: Lap Time Analysis ---
with col2:
    st.header("Lap Time Analysis")
    st.caption(f"Showing data for: {selected_race}")

    # --- Lap Time Plot ---
    fig_analysis, ax_analysis = plt.subplots(figsize=(7, 4))

    if selected_drivers:
        max_runs = 0
        for driver in selected_drivers:
            times = get_valid_times(selected_race, driver)
            if times:
                run_numbers = range(1, len(times) + 1)
                max_runs = max(max_runs, len(times))
                ax_analysis.plot(run_numbers, times, marker='o', linestyle='-',
                                 label=driver, color=driver_colors_map.get(driver, 'black'))
        if max_runs > 0:
            ax_analysis.set_xlabel("Run Number")
            ax_analysis.set_ylabel("Time (seconds)")
            ax_analysis.set_title("Lap Times per Run")
            ax_analysis.legend(fontsize='small')
            ax_analysis.grid(True, linestyle='--', linewidth=0.5)
            ax_analysis.set_xticks(range(1, max_runs + 1))
        else:
             ax_analysis.text(0.5, 0.5, "No valid lap times found.", ha='center', va='center')
             ax_analysis.set_xticks([])
             ax_analysis.set_yticks([])
    else:
        ax_analysis.text(0.5, 0.5, "Select drivers\nto plot times.", ha='center', va='center')
        ax_analysis.set_xticks([])
        ax_analysis.set_yticks([])

    fig_analysis.tight_layout()
    st.pyplot(fig_analysis)

    # --- Statistics Table ---
    st.subheader("Summary Statistics")
    stats_data = []
    if selected_drivers:
        for driver in selected_drivers:
            times = get_valid_times(selected_race, driver)
            stats = calculate_stats(times)
            if stats['count'] > 0:
                stats_data.append({
                    "Driver": driver, "Runs": stats['count'],
                    "Best (s)": f"{stats['best']:.2f}", "Worst (s)": f"{stats['worst']:.2f}",
                    "Average (s)": f"{stats['average']:.2f}", "StdDev (s)": f"{stats['stdev']:.3f}"
                })
            else:
                stats_data.append({"Driver": driver, "Runs": 0, "Best (s)": "N/A", "Worst (s)": "N/A", "Average (s)": "N/A", "StdDev (s)": "N/A"})
        st.markdown("---")
        stats_df = pd.DataFrame(stats_data)
        st.dataframe(stats_df.set_index('Driver')) # Display stats in a table
    else:
        st.info("Select drivers using the sidebar to view analysis.")
