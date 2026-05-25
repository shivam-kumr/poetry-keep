import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
from datetime import datetime

st.set_page_config(page_title="My Private Keep", layout="wide")
st.title("📝 Permanent Poetry Repository")

# Connect to our Google Sheet
conn = st.connection("gsheets", type=GSheetsConnection)

# Safely read existing poems
try:
    df = conn.read(ttl="0d")  # Forces fresh data every time
except Exception:
    df = pd.DataFrame(columns=["Date", "Title", "Content", "Author"])

# Sidebar layout for adding poems
st.sidebar.header("Add New Entry")
author = st.sidebar.text_input("Your Name / Pen Name")  # <-- NEW AUTHOR FIELD
title = st.sidebar.text_input("Poem Title")
content = st.sidebar.text_area("Write or Paste here...", height=250)

if st.sidebar.button("Save Note"):
    if author and title and content:
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        # Format the new entry row including Author
        new_row = pd.DataFrame([{"Date": timestamp, "Title": title, "Content": content, "Author": author}])
        updated_df = pd.concat([df, new_row], ignore_index=True)
        
        # Push back to Google Sheets
        conn.update(data=updated_df)
        
        st.sidebar.success(f"Saved '{title}' successfully!")
        st.rerun()
    else:
        st.sidebar.error("Please fill out Name, Title, and Content.")

# Main area layout: Displays the saved poems in a Google Keep-style grid
st.header("Saved Notes & Poetry")

if not df.empty:
    reversed_df = df.iloc[::-1] # Show newest entries first
    cols = st.columns(3) # Create a 3-column wide layout
    
    for i, row in enumerate(reversed_df.itertuples()):
        with cols[i % 3]:
            with st.container(border=True): # Creates a card layout
                st.subheader(row.Title)
                
                # Check if Author column exists and has a value, display it beautifully
                author_name = getattr(row, 'Author', 'Unknown Author')
                st.caption(f"By: {author_name} | Saved on: {row.Date}")
                
                st.text(row.Content) 
else:
    st.info("No notes saved yet. Use the sidebar to add your first poem!")
