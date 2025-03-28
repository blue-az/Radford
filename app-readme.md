# Autocross Data Dashboard (Streamlit)

This Streamlit web application provides an interactive dashboard for visualizing autocross track layouts and analyzing corresponding lap time data.

It combines a static visualization of the track (oriented correctly to match the original simulation) with interactive charts and summary statistics for lap time analysis.

## Features

*   **Web-Based GUI:** Accessible via a web browser, built with Streamlit.
*   **Static Track Visualization:** Displays the defined track layout using Matplotlib, including the main course and connector path, correctly oriented.
*   **Interactive Lap Time Chart:** Plots lap times versus run number for selected drivers and races.
*   **Summary Statistics Table:** Calculates and displays key performance metrics (Runs, Best, Worst, Average, Standard Deviation) for selected drivers.
*   **Race & Driver Selection:** Allows users to filter the displayed data by race configuration and select multiple drivers for comparison via sidebar controls.

<!-- Add a screenshot of the Streamlit dashboard here -->
<!-- ![Dashboard Screenshot](path/to/screenshot.png) -->

## Requirements

*   **Python:** Version 3.7 or higher recommended.
*   **Libraries:**
    *   streamlit
    *   matplotlib
    *   pandas

## Installation

1.  **Ensure Python is installed.** You can download it from [python.org](https://www.python.org/).
2.  **Create a project directory** and navigate into it in your terminal.
3.  **Save the application code** as `streamlit_app.py` in your project directory.
4.  **Create a `requirements.txt` file** in the same directory with the following content:
    ```txt
    streamlit
    matplotlib
    pandas
    ```
5.  **Install the required libraries:**
    ```bash
    pip install -r requirements.txt
    ```
    *(It's often recommended to do this within a Python virtual environment).*

## Running the App

1.  **Navigate to the project directory** in your terminal.
2.  **Run the Streamlit application:**
    ```bash
    streamlit run streamlit_app.py
    ```
3.  Streamlit will start a local web server and typically open the application automatically in your default web browser. If not, the terminal will provide the URL (usually `http://localhost:8501`).
4.  **Interact with the Dashboard:** Use the radio buttons and multi-select boxes in the sidebar to choose the race and drivers you want to analyze. The track layout, chart, and statistics will update automatically.

## Data Format

The lap time and track data are currently **hardcoded** within the `streamlit_app.py` script.

*   **Lap Times:** Located in the `race_data` dictionary. Modify the `times` lists within each driver's entry to use your own data. Times should be in seconds (float).
*   **Track Layout:** Defined by the `all_raw_points` list. These represent the control points for the spline curves, with `(0,0)` as a relative center and the Y-axis increasing downwards (matching Pygame convention). Modify these `(x, y)` tuples to change the track shape.

If analyzing different data frequently, consider modifying the script to load data from an external file (like a CSV or JSON).
