import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
from datetime import datetime

st.set_page_config(page_title="My Private Keep", layout="wide")
st.title("📝 Permanent Poetry Repository")

# Establish connection to Google Sheets
conn = st.connection("gsheets", type=GSheetsConnection)

# Read existing data safely
try:
    df = conn.read(ttl="0d")  # ttl="0d" ensures it always fetches fresh data, no caching
except Exception:
    # If the sheet is completely empty, create a starter DataFrame
    df = pd.DataFrame(columns=["Date", "Title", "Content"])

# Sidebar for adding new poems
st.sidebar.header("Add New Entry")
title = st.sidebar.text_input("Title")
content = st.sidebar.text_area("Write or Paste here...", height=250)

if st.sidebar.button("Save Note"):
    if title and content:
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        # Create a new row of data
        new_row = pd.DataFrame([{"Date": timestamp, "Title": title, "Content": content}])
        
        # Combine the old data with the new row
        updated_df = pd.concat([df, new_row], ignore_index=True)
        
        # Save back to Google Sheets
        conn.update(data=updated_df)
        
        st.sidebar.success(f"Saved '{title}' successfully!")
        # Rerun the app to show the newly added item instantly
        st.rerun()
else:
    st.sidebar.error("Please fill out both Title and Content.")

# Main area: Display saved notes in a Google Keep-style grid
st.header("Saved Notes & Poetry")

if not df.empty:
    # Reverse the dataframe rows so the newest entries are displayed first
    reversed_df = df.iloc[::-1]
    
    # Display in a clean 3-column grid layout
    cols = st.columns(3)
    for i, row in enumerate(reversed_df.itertuples()):
        with cols[i % 3]:
            with st.container(border=True):
                st.subheader(row.Title)
                st.caption(f"Saved on: {row.Date}")
                # st.text preserves exact spaces and line breaks for poetry formatting
                st.text(row.Content)
else:
    st.info("No notes saved yet. Use the sidebar to add your first poem!")