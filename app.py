import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
from datetime import datetime

st.set_page_config(page_title="Poetry Repository", layout="wide")

# Minimalist CSS to keep the buttons looking clean and professional
st.markdown("""
    <style>
    div.stButton > button {
        background-color: transparent !important;
        color: #5f6368 !important;
        border: 1px solid #dadce0 !important;
        padding: 4px 10px !important;
        height: auto !important;
        font-size: 12px !important;
        border-radius: 4px !important;
    }
    div.stButton > button:hover {
        background-color: #f8f9fa !important;
        border-color: #c0c0c0 !important;
        color: #202124 !important;
    }
    </style>
""", unsafe_allow_html=True)

st.title("📝 Poetry Repository")

# Connect to Google Sheets
conn = st.connection("gsheets", type=GSheetsConnection)

# Fetch fresh data from the Google Sheet
try:
    df = conn.read(ttl="0d")
    # Ensure all columns exist
    for col in ["Date", "Title", "Content", "Author"]:
        if col not in df.columns:
            df[col] = ""
except Exception:
    df = pd.DataFrame(columns=["Date", "Title", "Content", "Author"])

# ─── MODAL DIALOG: READ, EDIT & DIRECT DELETE ────────────────────────
@st.dialog("📖 Poetry Management")
def open_poem_modal(row_index, title, author, date, content, full_df):
    st.subheader(title)
    st.caption(f"By: {author} | Saved on: {date}")
    st.divider()
    
    # Clean tabs for user actions
    tab1, tab2, tab3 = st.tabs(["Read", "✏️ Edit Poem", "🗑️ Delete"])
    
    with tab1:
        st.text(content)
        
    with tab2:
        edit_author = st.text_input("Edit Author", value=author, key=f"edit_auth_{row_index}")
        edit_title = st.text_input("Edit Title", value=title, key=f"edit_title_{row_index}")
        edit_content = st.text_area("Edit Content", value=content, height=200, key=f"edit_cont_{row_index}")
        
        if st.button("Save Changes", key=f"save_mod_{row_index}"):
            if edit_author and edit_content:
                # Update the specific row inside the dataframe
                full_df.at[row_index, "Author"] = edit_author
                full_df.at[row_index, "Title"] = edit_title if edit_title.strip() else "Untitled"
                full_df.at[row_index, "Content"] = edit_content
                
                # Push back to Google Sheets
                conn.update(data=full_df)
                st.success("Poem updated successfully!")
                st.rerun()
            else:
                st.error("Name and Content cannot be blank.")
                
    with tab3:
        st.error("⚠️ Are you sure you want to permanently delete this poem?")
        st.write("This action will immediately remove it from the Google Sheet database.")
        
        # Simple, frictionless direct delete button
        if st.button("Yes, Delete Permanently", key=f"del_mod_{row_index}"):
            updated_df = full_df.drop(row_index)
            conn.update(data=updated_df)
            st.success("Poem deleted successfully!")
            st.rerun()

# ─── SIDEBAR: SUBMIT NEW POETRY ─────────────────────────────────────
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

# ─── MAIN APP: SEARCH AND GRID INTERFACE ──────────────────────────────
# Global Search Bar
search_query = st.text_input("🔍 Search poems by title, author, or keywords...", "").strip().lower()

if not df.empty:
    # Tracking original spreadsheet index row number so edits map to the right place
    df['_orig_idx'] = df.index
    
    # Filter the view if someone uses the search bar
    if search_query:
        filtered_df = df[
            df['Title'].astype(str).str.lower().str.contains(search_query) |
            df['Author'].astype(str).str.lower().str.contains(search_query) |
            df['Content'].astype(str).str.lower().str.contains(search_query)
        ]
    else:
        filtered_df = df

    if not filtered_df.empty:
        reversed_df = filtered_df.iloc[::-1] # Newest on top
        cols = st.columns(3)
        
        for i, row in enumerate(reversed_df.itertuples()):
            with cols[i % 3]:
                with st.container(border=True):
                    st.markdown(f"### {row.Title}")
                    st.markdown(f"<span style='color:gray; font-size:12px;'>By: {row.Author}</span>", unsafe_allow_html=True)
                    
                    # Clean snippet preview length
                    poem_content = getattr(row, 'Content', '')
                    preview_text = poem_content if len(poem_content) <= 120 else poem_content[:120] + "..."
                    st.text(preview_text)
                    
                    # Sleek link button trigger
                    if st.button("View / Manage", key=f"open_{row._orig_idx}"):
                        open_poem_modal(
                            row._orig_idx, 
                            row.Title, 
                            row.Author, 
                            getattr(row, 'Date', ''), 
                            poem_content, 
                            df.drop(columns=['_orig_idx']) # Clean out helper index before saving
                        )
    else:
        st.info("No matching poems found for your search query.")
else:
    st.info("No notes saved yet. Use the sidebar to add your first poem!")
