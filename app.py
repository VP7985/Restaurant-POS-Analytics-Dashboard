# app.py
# Main entry point to run the Streamlit application.

import streamlit as st
import os
import sys

# Add the project root to the Python path to allow for module imports
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Import the main function from your UI file
try:
    from ui.main_ui import main
except ImportError as e:
    st.error(f"Could not import the main UI. Please ensure 'ui/main_ui.py' exists. Error: {e}")
    st.stop()

if __name__ == "__main__":
    # Check if the required directories exist and create them if not
    for folder in ['utils', 'db', 'assets', 'data']:
        if not os.path.exists(folder):
            os.makedirs(folder)
            st.info(f"Created '{folder}/' directory.")
        
    main()

