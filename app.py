import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
from datetime import datetime

# Page Configuration
st.set_page_config(
    page_title="Our Poetry", 
    layout="centered", 
    initial_sidebar_state="collapsed" # Starts collapsed for a clean look, can be opened via the top-left '>'
)

# Custom Styling Overrides for Premium Aesthetic
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600&display=swap');
    
    html, body, [data-testid="stAppViewContainer"] {
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif !important;
    }
    
    /* Clean Title Formatting */
    .main-title {
        font-size: 2.25rem !important;
        font-weight: 600 !important;
        letter-spacing: -0.02em !important;
        margin-bottom: 1.5rem !important;
    }
    
    /* Elegant Bordered Poetry Cards for Homepage Separation */
    div[data-testid="stContainer"] {
        background-color: transparent;
        border: 1px solid rgba(128, 128, 128, 0.2) !important;
        border-radius: 12px !important;
        padding: 20px !important;
        box-shadow: 0 4px 12px rgba(0,0,0,0.01) !important;
        transition: all 0.25s ease !important;
    }
    
    div[data-testid="stContainer"]:hover {
        transform: translateY(-1px);
        box-shadow: 0 8px 16px rgba(0,0,0,0.04) !important;
        border-color: rgba(128, 128, 128, 0.35) !important;
    }
    
    /* Card Elements */
    .card-title {
        font-size: 1.25rem !important;
        font-weight: 600 !important;
        margin-bottom: 2px !important;
    }
    
    .card-author {
        font-size: 0.8rem !important;
        font-weight: 500 !important;
        color: #86868b !important;
        text-transform: uppercase;
        letter-spacing: 0.05em;
        margin-bottom: 12px !important;
    }
    
    /* Clean Sans-Serif Preview Text matching the homepage vibe */
    .card-preview {
        font-size: 0.95rem !important;
        line-height: 1.6 !important;
        opacity: 0.85;
        margin-bottom: 16px !important;
        white-space: pre-wrap !important;
    }

    /* Minimalist Underline Action Link Buttons */
    div.stButton > button {
        background-color: transparent !important;
        color: var(--text-color) !important;
        border: none !important;
        padding: 0px !important;
        font-size: 0.85rem !important;
        font-weight: 500 !important;
        text-decoration: underline !important;
        text-underline-offset: 4px !important;
        opacity: 0.7;
    }
    div.stButton > button:hover {
        opacity: 1 !important;
        color: var(--text-color) !important;
    }

    /* Fixed Premium Sans-Serif Reader Layout (Highly Readable) */
    .poetry-reader-viewport {
        font-size: 1.05rem !important;
        line-height: 1.75 !important;
        font-weight: 400 !important;
        padding: 5px 0px !important;
        white-space: pre-wrap !important;
        opacity: 0.95;
    }
    
    /* Search Bar Styling */
    div[data-testid="stTextInput"] input {
        border-radius: 10px !important;
        padding: 10px 14px !important;
        border: 1px solid rgba(128, 128, 128, 0.2) !important;
    }
    </style>
""", unsafe_allow_html=True)

# Application Header - Renamed directly to "Our Poetry"
st.markdown("<div class='main-title'>Our Poetry</div>", unsafe_allow_html=True)

# Connect to Google Sheets Pipeline
conn = st.connection("gsheets", type=GSheetsConnection)

try:
    df = conn.read(ttl="0d")
    for col in ["Date", "Title", "Content", "Author"]:
        if col not in df.columns:
            df[col] = ""
    df = df.astype(object)
except Exception:
    df = pd.DataFrame(columns=["Date", "Title", "Content", "Author"])

# ─── IMMERSIVE POPUP VIEWPORT (FIXED READABLE FONT) ───────────────────
@st.dialog("📖 Reading Room")
def open_poem_modal(row_index, title, author, date, content, full_df):
    st.markdown(f"<h3 style='font-size:1.6rem; font-weight:600; margin-bottom: 2px;'>{title}</h3>", unsafe_allow_html=True)
    st.markdown(f"<p style='color:#86868b; font-size:0.8rem; text-transform:uppercase; letter-spacing:0.05em; margin-bottom:20px;'>By {author} • {date}</p>", unsafe_allow_html=True)
    
    tab1, tab2, tab3 = st.tabs(["Read", "✏️ Edit Draft", "🗑️ Remove"])
    
    with tab1:
        # Replaced blurry cursive/serif with crisp, legible sans-serif structure matching homepage
        st.markdown(f'<div class="poetry-reader-viewport">{content}</div>', unsafe_allow_html=True)
        st.write("")
        
    with tab2:
        meta_col1, meta_col2 = st.columns(2)
        with meta_col1:
            edit_title = st.text_input("Title", value=str(title), key=f"edit_title_{row_index}")
        with meta_col2:
            edit_author = st.text_input("Author signature", value=str(author), key=f"edit_auth_{row_index}")
            
        number_of_lines = len(content.split('\n'))
        dynamic_height = min(max(number_of_lines * 24, 250), 500)
        edit_content = st.text_area("Body", value=str(content), height=dynamic_height, key=f"edit_cont_{row_index}")
        
        st.write("")
        if st.button("Save Revision", key=f"save_mod_{row_index}"):
            if edit_author.strip() and edit_content.strip():
                full_df.at[row_index, "Author"] = edit_author.strip()
                full_df.at[row_index, "Title"] = edit_title.strip() if edit_title.strip() else "Untitled"
                full_df.at[row_index, "Content"] = edit_content
                
                conn.update(data=full_df)
                st.rerun()
            else:
                st.error("Signature and Body are required.")
                
    with tab3:
        st.write("")
        st.markdown("<p style='color:#ff4b4b; font-weight:500;'>Remove this piece permanently?</p>", unsafe_allow_html=True)
        if st.button("Confirm Deletion", key=f"del_mod_{row_index}"):
            updated_df = full_df.drop(row_index)
            conn.update(data=updated_df)
            st.rerun()

# ─── IMPROVEMENT 1: SUBMISSION CONTAINER MOVED TO LEFT SIDEBAR ───────
with st.sidebar:
    st.markdown("<h3 style='font-weight:600; margin-top:10px;'>🖋️ Add New Poem</h3>", unsafe_allow_html=True)
    st.write("Write or paste a new piece into the collective collection below.")
    st.write("")
    
    author = st.text_input("Your Name / Pen Name", placeholder="e.g., Anonymous")
    title = st.text_input("Poem Title (Optional)", placeholder="Leave blank for Untitled")
    content = st.text_area("Write or Paste here...", height=280)
    
    st.write("")
    if st.button("Publish Poem Link", use_container_width=True):
        if author and content:
            timestamp = datetime.now().strftime("%B %d, %Y")
            final_title = title.strip() if title.strip() else "Untitled"
            
            new_row = pd.DataFrame([{"Date": timestamp, "Title": final_title, "Content": content, "Author": author}])
            updated_df = pd.concat([df, new_row], ignore_index=True)
            
            conn.update(data=updated_df)
            st.rerun()
        else:
            st.error("Signature name and poem body text are required.")

# ─── HOME INTERFACE: ARCHIVE LIST & GRID SEARCH ───────────────────────
search_query = st.text_input("🔍 Search collection...", placeholder="Search titles, authors, keywords...").strip().lower()
st.write("")

if not df.empty:
    df['orig_idx'] = df.index
    
    if search_query:
        filtered_df = df[
            df['Title'].astype(str).str.lower().str.contains(search_query) |
            df['Author'].astype(str).str.lower().str.contains(search_query) |
            df['Content'].astype(str).str.lower().str.contains(search_query)
        ]
    else:
        filtered_df = df

    if not filtered_df.empty:
        reversed_df = filtered_df.iloc[::-1]
        
        # Clean 2-column layout with explicit container isolation cards
        grid_cols = st.columns(2)
        for i, row in enumerate(reversed_df.itertuples()):
            with grid_cols[i % 2]:
                with st.container(): # Generates the sleek individual boundary box
                    st.markdown(f'<div class="card-title">{row.Title}</div>', unsafe_allow_html=True)
                    st.markdown(f'<div class="card-author">By {row.Author}</div>', unsafe_allow_html=True)
                    
                    raw_content = getattr(row, 'Content', '')
                    snippet = raw_content if len(raw_content) <= 100 else raw_content[:100] + "..."
                    st.markdown(f'<div class="card-preview">{snippet}</div>', unsafe_allow_html=True)
                    
                    if st.button("Read Piece →", key=f"open_{row.orig_idx}"):
                        open_poem_modal(
                            row.orig_idx, 
                            row.Title, 
                            row.Author, 
                            getattr(row, 'Date', ''), 
                            raw_content, 
                            df.drop(columns=['orig_idx'])
                        )
    else:
        st.markdown("<p style='color:gray; font-style:italic;'>No archives match your search criteria.</p>", unsafe_allow_html=True)
else:
    st.markdown("<p style='color:gray; font-style:italic; text-align:center; padding: 40px 0;'>The collection is empty. Open the sidebar menu from the top-left to log the first piece.</p>", unsafe_allow_html=True)
