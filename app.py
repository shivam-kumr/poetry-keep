import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
from datetime import datetime

# 1. Page Configuration & Aesthetic Foundations
st.set_page_config(
    page_title="Anthology — Private Poetry Space", 
    layout="centered", 
    initial_sidebar_state="collapsed"
)

# 2. Premium Apple/Editorial Custom Design Injection
st.markdown("""
    <style>
    /* Global Background and Typography Overrides */
    @import url('https://fonts.googleapis.com/css2?family=Playfair+Display:ital,wght@0,400;0,600;1,400&family=Inter:wght@300;400;500&display=swap');
    
    html, body, [data-testid="stAppViewContainer"] {
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif !important;
        background-color: transparent;
    }
    
    /* Clean Minimalist Typography */
    h1 {
        font-family: 'Playfair Display', serif !important;
        font-weight: 600 !important;
        font-size: 2.85rem !important;
        letter-spacing: -0.03em !important;
        margin-bottom: 0.2rem !important;
    }
    
    .app-subtitle {
        font-family: 'Inter', sans-serif;
        font-weight: 300;
        color: #86868b;
        font-size: 1.1rem;
        margin-bottom: 2.5rem;
    }
    
    /* Premium Borderless Poetry Cards */
    div[data-testid="stContainer"] {
        background-color: var(--background-color);
        border: 1px solid rgba(128, 128, 128, 0.15) !important;
        border-radius: 14px !important;
        padding: 24px !important;
        box-shadow: 0 4px 12px rgba(0,0,0,0.02) !important;
        transition: all 0.3s cubic-bezier(0.16, 1, 0.3, 1) !important;
    }
    
    div[data-testid="stContainer"]:hover {
        transform: translateY(-2px);
        box-shadow: 0 12px 24px rgba(0,0,0,0.06) !important;
        border-color: rgba(128, 128, 128, 0.3) !important;
    }
    
    /* Card Text Structure */
    .card-title {
        font-family: 'Playfair Display', serif !important;
        font-weight: 600 !important;
        font-size: 1.4rem !important;
        margin-bottom: 4px !important;
    }
    
    .card-author {
        font-size: 0.85rem !important;
        font-weight: 400 !important;
        color: #86868b !important;
        text-transform: uppercase;
        letter-spacing: 0.08em;
        margin-bottom: 16px !important;
    }
    
    .card-preview {
        font-family: 'Georgia', serif !important;
        font-size: 0.95rem !important;
        line-height: 1.6 !important;
        color: var(--text-color);
        opacity: 0.85;
        margin-bottom: 20px !important;
        white-space: pre-wrap !important;
    }

    /* Elegant Text-Link Style Action Buttons */
    div.stButton > button {
        background-color: transparent !important;
        color: var(--text-color) !important;
        border: none !important;
        padding: 0px !important;
        font-size: 0.9rem !important;
        font-weight: 500 !important;
        text-decoration: underline !important;
        text-underline-offset: 4px !important;
        transition: opacity 0.2s ease !important;
        opacity: 0.65;
    }
    div.stButton > button:hover {
        opacity: 1 !important;
        background-color: transparent !important;
        color: var(--text-color) !important;
    }
    div.stButton > button:active {
        background-color: transparent !important;
    }

    /* Editorial Mode Poetry Viewport */
    .poetry-editorial-viewport {
        font-family: 'Playfair Display', serif !important;
        font-size: 1.25rem !important;
        line-height: 1.9 !important;
        font-style: italic;
        padding: 15px 10px !important;
        white-space: pre-wrap !important;
        border-left: 2px solid rgba(128,128,128,0.2);
        padding-left: 24px !important;
        margin: 20px 0 !important;
    }
    
    /* Search Bar Styling Enhancement */
    div[data-testid="stTextInput"] input {
        border-radius: 10px !important;
        padding: 12px 16px !important;
        border: 1px solid rgba(128, 128, 128, 0.2) !important;
        background-color: rgba(128, 128, 128, 0.03) !important;
    }
    
    /* Clean Tab Design */
    div[data-testid="stTabs"] button {
        font-size: 0.9rem !important;
        letter-spacing: 0.02em;
    }
    </style>
""", unsafe_allow_html=True)

# 3. App Header Block
st.markdown("<h1>Anthology</h1>", unsafe_allow_html=True)
st.markdown("<p class='app-subtitle'>A quiet workspace for collective writing & observation.</p>", unsafe_allow_html=True)

# 4. Database Stream Pipeline
conn = st.connection("gsheets", type=GSheetsConnection)

try:
    df = conn.read(ttl="0d")
    for col in ["Date", "Title", "Content", "Author"]:
        if col not in df.columns:
            df[col] = ""
    df = df.astype(object)
except Exception:
    df = pd.DataFrame(columns=["Date", "Title", "Content", "Author"])

# 5. Immersive Modal Interface — Pure Typography
@st.dialog("📖 Reading Room")
def open_poem_modal(row_index, title, author, date, content, full_df):
    st.markdown(f"<h2 style='font-family:\"Playfair Display\", serif; font-size:2rem;'>{title}</h2>", unsafe_allow_html=True)
    st.markdown(f"<p style='color:#86868b; font-size:0.85rem; text-transform:uppercase; letter-spacing:0.05em; margin-top:-10px;'>Written by {author} • {date}</p>", unsafe_allow_html=True)
    
    tab1, tab2, tab3 = st.tabs(["Read", "✏️ Edit Draft", "🗑️ Remove"])
    
    with tab1:
        # High-end typographic wrapper for text rendering
        st.markdown(f'<div class="poetry-editorial-viewport">{content}</div>', unsafe_allow_html=True)
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
        st.markdown("<p style='color:#ff4b4b; font-weight:500;'>Are you sure you want to delete this piece?</p>", unsafe_allow_html=True)
        st.write("This will instantly sync and remove it permanently from the central anthology ledger.")
        if st.button("Confirm Deletion", key=f"del_mod_{row_index}"):
            updated_df = full_df.drop(row_index)
            conn.update(data=updated_df)
            st.rerun()

# 6. Creator Canvas Component (The Hidden Expander Drawer)
with st.expander("🖋️ Open Entry Canvas", expanded=False):
    st.write("")
    col_input1, col_input2 = st.columns([1, 2])
    with col_input1:
        author = st.text_input("Signature / Pen Name", placeholder="e.g., Anonymous")
    with col_input2:
        title = st.text_input("Title (Optional)", placeholder="Untitled")
        
    content = st.text_area("Compose or Paste lines...", height=220)
    st.write("")
    
    if st.button("Commit to Anthology"):
        if author and content:
            timestamp = datetime.now().strftime("%B %d, %Y") # Clean editorial date structure (e.g., May 25, 2026)
            final_title = title.strip() if title.strip() else "Untitled"
            
            new_row = pd.DataFrame([{"Date": timestamp, "Title": final_title, "Content": content, "Author": author}])
            updated_df = pd.concat([df, new_row], ignore_index=True)
            
            conn.update(data=updated_df)
            st.rerun()
        else:
            st.error("Please provide both a signature name and your content lines.")

st.markdown("<hr style='margin: 2.2rem 0; opacity:0.1;'>", unsafe_allow_html=True)

# 7. Editorial Filtering System
search_query = st.text_input("🔍 Search collection...", placeholder="Search titles, authors, fragments...").strip().lower()
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
        
        # Clean 2-column balanced grid architecture
        grid_cols = st.columns(2)
        for i, row in enumerate(reversed_df.itertuples()):
            with grid_cols[i % 2]:
                with st.container():
                    # Rendering custom typography injection mapping straight to our CSS classes
                    st.markdown(f'<div class="card-title">{row.Title}</div>', unsafe_allow_html=True)
                    st.markdown(f'<div class="card-author">By {row.Author}</div>', unsafe_allow_html=True)
                    
                    raw_content = getattr(row, 'Content', '')
                    # Limit preview text cleanly
                    snippet = raw_content if len(raw_content) <= 90 else raw_content[:90] + "..."
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
    st.markdown("<p style='color:gray; font-style:italic; text-align:center; padding: 40px 0;'>The anthology repository is currently blank. Open the Entry Canvas above to document the first collection.</p>", unsafe_allow_html=True)
