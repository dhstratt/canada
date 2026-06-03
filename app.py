import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import io
import pickle

# =====================================================================
# INITIAL SETUP & PAGE CONFIG
# =====================================================================
st.set_page_config(page_title="Market Segment & Landscape Builder", layout="wide")

st.title("🎯 Advanced Market Segment & Landscape Builder")
st.markdown("Upload your respondent-level Master File or a Saved Workspace to translate attitudes, build segments, and map the competitive landscape.")

# =====================================================================
# CODEBOOK DICTIONARY (Translates Q-Codes to Plain English)
# =====================================================================
PSYCHOGRAPHIC_MAP = {
    "Q19_r1": "I thrive at big parties and social occasions",
    "Q19_r2": "I think of myself as an intellectual",
    "Q19_r3": "Spending time with my family is my top priority",
    "Q19_r4": "I am interested in finding out how I can help the environment",
    "Q19_r5": "I am an optimist",
    "Q19_r6": "I seek out variety in my everyday life",
    "Q19_r7": "I make sure I take time for myself each day",
    "Q19_r8": "I like to learn about foreign cultures",
    "Q19_r9": "I’m perfectly happy with my standard of living",
    "Q20_r1": "I like to change brands often for the sake of variety and novelty",
    "Q20_r2": "I buy based on quality, not price",
    "Q20_r3": "Price is more important to me than brand names",
    "Q20_r4": "Generic or store brand products are as effective as brand-name products",
    "Q20_r5": "I enjoy wandering the store looking for new, interesting products",
    "Q20_r6": "I tend to make impulse purchases",
    "Q20_r7": "My children have significant impact on the brands I choose",
    "Q20_r8": "I buy brands that reflect my style",
    "Q20_r9": "I am influenced by what's hot and what's not",
    "Q21_r1": "I prefer foods cooked with bold flavors",
    "Q21_r2": "Nutritional value is the most important factor when I'm choosing which foods to eat",
    "Q21_r3": "I eat the foods I like regardless of calories",
    "Q21_r4": "I believe in a healthy lifestyle instead of traditional dieting",
    "Q21_r5": "Food is a comfort to me",
    "Q21_r6": "I indulge my cravings for foods I enjoy",
    "Q21_r7": "I am loyal to my food brands and stick with them",
    "Q21_r8": "Fast food is junk food",
    "Q21_r9": "I prefer to eat foods without artificial ingredients",
    "Q21_r10": "I try to eat a healthy breakfast every day",
    "Q22_r1": "I am generally more fit and active than other people my age",
    "Q22_r2": "I frequently look for new ways to change up my exercise routine",
    "Q22_r3": "I regularly look for ways to get a better night’s sleep",
    "Q22_r4": "Because of my busy lifestyle, I don’t take care of myself as well as I should",
    "Q22_r5": "The health claims/benefits on a product package often influence my decision to buy it",
    "Q22_r6": "Taking care of your mental health is a critical part of your overall wellness",
    "Q22_r7": "I always do what my doctor tells me to do",
    "Q22_r8": "I consider my diet to be very healthy"
}

ENGLISH_STATEMENTS = list(PSYCHOGRAPHIC_MAP.values())

# =====================================================================
# DATA PROCESSING FUNCTIONS
# =====================================================================
@st.cache_data
def load_and_prep_data(file):
    if file.name.endswith('.csv'):
        df = pd.read_csv(file)
    else:
        df = pd.read_excel(file)
        
    for q_code, english_stmt in PSYCHOGRAPHIC_MAP.items():
        if q_code in df.columns:
            df[english_stmt] = df[q_code]
    
    if "weight" not in df.columns.str.lower():
        df["Weight"] = 1.0
    else:
        weight_col = [c for c in df.columns if c.lower() == 'weight'][0]
        df.rename(columns={weight_col: 'Weight'}, inplace=True)
        
    return df

# =====================================================================
# SIDEBAR: UPLOAD & WORKSPACE MANAGEMENT
# =====================================================================
st.sidebar.header("1. Upload Data or Workspace")
uploaded_file = st.sidebar.file_uploader("Upload Master File (.csv/.xlsx) or Workspace (.pkl)", type=["csv", "xlsx", "pkl"])

if uploaded_file:
    # -----------------------------------------------------------------
    # WORKSPACE RESTORATION (.pkl)
    # -----------------------------------------------------------------
    if uploaded_file.name.endswith('.pkl'):
        if 'data_loaded' not in st.session_state or st.session_state.get('file_name') != uploaded_file.name:
            workspace = pickle.loads(uploaded_file.getvalue())
            st.session_state['df_working'] = workspace['df_working']
            st.session_state['created_segments'] = workspace['created_segments']
            st.session_state['data_loaded'] = True
            st.session_state['file_name'] = uploaded_file.name
            
        df_base = st.session_state['df_working']
        st.sidebar.success(f"Workspace Restored! Loaded {len(st.session_state['created_segments'])} Custom Segments.")
        
    # -----------------------------------------------------------------
    # NEW DATA INGESTION (.csv / .xlsx)
    # -----------------------------------------------------------------
    else:
        df_base = load_and_prep_data(uploaded_file)
        if 'data_loaded' not in st.session_state or st.session_state.get('file_name') != uploaded_file.name:
            st.session_state['df_working'] = df_base.copy()
            st.session_state['created_segments'] = []
            st.session_state['data_loaded'] = True
            st.session_state['file_name'] = uploaded_file.name
            
        st.sidebar.success(f"Loaded Master File: {len(df_base)} Respondents!")
    
    # -----------------------------------------------------------------
    # SIDEBAR: VARIABLE DEFINITIONS & SAVED SEGMENTS
    # -----------------------------------------------------------------
    st.sidebar.header("2. Define Your Variables")
    
    exclude_cols = ENGLISH_STATEMENTS + ["Weight"] + st.session_state.get('created_segments', [])
    brand_cols = st.sidebar.multiselect(
        "Select Brand Usage Columns:", 
        [col for col in df_base.columns if col not in exclude_cols and not col.startswith("Q")]
    )
    
    if st.session_state['created_segments']:
        st.sidebar.markdown("---")
        st.sidebar.subheader("💾 Stored Segments")
        
        # Adding Individual Delete Buttons
        for seg in st.session_state['created_segments']:
            col_name, col_del = st.sidebar.columns([4, 1])
            col_name.markdown(f"`{seg}`")
            if col_del.button("❌", key=f"del_{seg}", help=f"Delete {seg}"):
                st.session_state['df_working'] = st.session_state['df_working'].drop(columns=[seg])
                st.session_state['created_segments'].remove(seg)
                st.rerun()
                
        # Keep the global clear button just in case things get cluttered
        st.sidebar.markdown("---")
        if st.sidebar.button("🗑️ Clear All Segments", type="secondary"):
            st.session_state['df_working'] = st.session_state['df_working'].drop(columns=st.session_state['created_segments'])
            st.session_state['created_segments'] = []
            st.rerun()

    # -----------------------------------------------------------------
    # SIDEBAR: WORKSPACE DOWNLOADER
    # -----------------------------------------------------------------
    st.sidebar.markdown("---")
    st.sidebar.subheader("📦 Export Current Workspace")
    
    workspace_export = {
        'df_working': st.session_state['df_working'],
        'created_segments': st.session_state['created_segments']
    }
    pkl_bytes = pickle.dumps(workspace_export)
    
    st.sidebar.download_button(
        label="💾 Download Workspace (.pkl)",
        data=pkl_bytes,
        file_name="my_segment_workspace.pkl",
        mime="application/octet-stream",
        help="Download this snapshot to save your progress. Re-upload it later to restore all your custom segments instantly."
    )

    # =====================================================================
    # MAIN WORKSPACE: CUSTOM SEGMENT BUILDER
    # =====================================================================
    st.header("Step 1: Configure & Store Target Mindsets")
    st.markdown("Select statements, set logic, name your segment, and save it to your workspace.")
    
    selected_statements = st.multiselect(
        "Which attitude statements define this segment?", 
        options=ENGLISH_STATEMENTS
    )
    
    if selected_statements:
        st.markdown("### ⚙️ Fine-Tune Statement Logic")
        
        statement_logic = {}
        col_logic1, col_logic2 = st.columns(2)
        
        for i, stmt in enumerate(selected_statements):
            target_col = col_
