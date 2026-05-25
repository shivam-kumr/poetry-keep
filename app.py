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

# ─── NEW POP-UP CARD FUNCTION ────────────────────────────────────────
@st.dialog("📖 Reading Poem")
def open_poem_modal(title, author, date, content):
    st.subheader(title)
    st.caption(f"By: {author} | Saved on: {date}")
    st.divider()
    # Displays the full poem inside the popup with intact line breaks
    st.text(content)
    if st.button("Close"):
        st.rerun()
# ──────────────────────────────────────────────────────────────────────

# Sidebar layout for adding poems
st.sidebar.header("Add New Entry")
author = st.sidebar.text_input("Your Name / Pen Name")
title = st.sidebar.text_input("Poem Title (Optional)", placeholder="Leave blank for Untitled")
content = st.sidebar.text_area("Write or Paste here...", height=250)

if st.sidebar.button("Save Note"):
    if author and content:
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        final_title = title.strip() if title.strip() else "Untitled"
        
        new_row = pd.DataFrame([{"Date": timestamp, "Title": final_title, "Content": content, "Author": author}])
        updated_df = pd.concat([df, new_row], ignore_index=True)
        
        conn.update(data=updated_df)
        st.sidebar.success(f"Saved successfully!")
        st.rerun()
    else:
        st.sidebar.error("Please fill out both Name and Content fields.")

# Main area layout: Displays the saved poems in a Google Keep-style grid
st.header("Saved Notes & Poetry")

if not df.empty:
    reversed_df = df.iloc[::-1] # Show newest entries first
    cols = st.columns(3) # Create a 3-column wide layout
    
    for i, row in enumerate(reversed_df.itertuples()):
        with cols[i % 3]:
            with st.container(border=True): # Creates the Google Keep Card outline
                card_title = getattr(row, 'Title', 'Untitled')
                st.subheader(card_title)
                
                author_name = getattr(row, 'Author', 'Unknown Author')
                st.caption(f"By: {author_name}")
                
                # Show a short preview (first 150 characters) so the grid stays neat
                poem_content = getattr(row, 'Content', '')
                preview_text = poem_content if len(poem_content) <= 150 else poem_content[:150] + "..."
                st.text(preview_text)
                
                # Elegant button that acts like "clicking the card"
                # A unique key string ensures Streamlit knows exactly which button was pushed
                if st.button("Expand Card 🔍", key=f"btn_{i}"):
                    open_poem_modal(card_title, author_name, getattr(row, 'Date', ''), poem_content)
else:
    st.info("No notes saved yet. Use the sidebar to add your first poem!")
