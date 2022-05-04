# Imports
import streamlit as st
import enrich
import extract
import pyautogui

# List all pages
PAGES = {
    'CSV Enrichment': enrich,
    'HTML Extraction': extract
}

# Create sidebar
# Set title of sidebar
st.sidebar.title('App Navigation')

# List out pages to choose from
selection = st.sidebar.selectbox("Where we're heading captain", list(PAGES.keys()))

# First in the list is displayed by default
page = PAGES[selection]

# Set refresh label
st.sidebar.title('Refresh Selection')

# Create reset button
if st.sidebar.button('Reset / Restart'):
    pyautogui.hotkey('f5')

# Set expandable guide label
st.sidebar.title('Folder Guide')

# Create expander
expander = st.sidebar.expander("See explanation")

expander.write("""
    The chosen folder should have subfolders named after each campaign.
    Inside each subfolder are the related CSV or HTML for that campaign.
""")

expander.image("images\subfolder.png", caption='Subfolders in chosen folder', use_column_width='auto')
expander.image("images\csv.png", caption='CSV in subfolder', use_column_width='auto')
expander.image("images\html.png", caption='HTML in subfolder', use_column_width='auto')

# Set output guide label
st.sidebar.title('Output location')

# Create expander
expander = st.sidebar.expander("Find out where")

expander.write("""
    For CSV, the output is within each campaign subfolder.
""")

expander.image("images\output_csv.png", caption='Output for CSV', use_column_width='auto')

expander.write("""
    For HTML, the output is located in the chosen folder itself.
""")

expander.image("images\output_html.png", caption='Output for HTML', use_column_width='auto')

# Run the selected page
page.app()