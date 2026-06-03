import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

# =====================================================================
# INITIAL SETUP & PAGE CONFIG
# =====================================================================
st.set_page_config(page_title="Market Segment & Landscape Builder", layout="wide")

st.title("🎯 Advanced Market Segment & Landscape Builder")
st.markdown("Upload your respondent-level Master File to translate attitudes, build custom segments, and map the competitive landscape.")

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

# =====================================================================
# DATA PROCESSING FUNCTIONS
# =====================================================================
@st.cache_data
def load_and_prep_data(file):
    if file.name.endswith('.csv'):
        df = pd.read_csv(file)
    else:
        df = pd.read_excel(file)
        
    # Translate columns but KEEP the original 1-4 scale for precision logic
    for q_code, english_stmt in PSYCHOGRAPHIC_MAP.items():
        if q_code in df.columns:
            df[english_stmt] = df[q_code]
    
    # Initialize unweighted standard if weight column is missing
    if "weight" not in df.columns.str.lower():
        df["Weight"] = 1.0
    else:
        # Standardize weight column name
        weight_col = [c for c in df.columns if c.lower() == 'weight'][0]
        df.rename(columns={weight_col: 'Weight'}, inplace=True)
        
    return df

# =====================================================================
# SIDEBAR: UPLOAD & MAP COLUMNS
# =====================================================================
st.sidebar.header("1. Upload Master Data")
uploaded_file = st.sidebar.file_uploader("Upload Respondent-Level File", type=["csv", "xlsx"])

if uploaded_file:
    df_master = load_and_prep_data(uploaded_file)
    st.sidebar.success(f"Loaded & Translated {len(df_master)} Respondents!")
    
    st.sidebar.header("2. Define Your Variables")
    brand_cols = st.sidebar.multiselect("Select Brand Usage Columns:", df_master.columns)
    demo_cols = st.sidebar.multiselect("Select Demographic Columns (e.g., Age, Region):", df_master.columns)
    
    # =====================================================================
    # MAIN WORKSPACE: CUSTOM SEGMENT BUILDER
    # =====================================================================
    st.header("Step 1: Configure Your Target Mindset Segment")
    st.markdown("Select statements to bundle together, set your exact agreement logic, and define your custom consumer archetype.")
    
    selected_statements = st.multiselect(
        "Which attitude statements define this target segment?", 
        options=list(PSYCHOGRAPHIC_MAP.values())
    )
    
    df_working = df_master.copy()
    segment_created = False
    
    if selected_statements:
        st.markdown("### ⚙️ Fine-Tune Statement Logic")
        st.markdown("*Specify exactly how a respondent must answer each statement to score a point.*")
        
        statement_logic = {}
        col_logic1, col_logic2 = st.columns(2)
        
        for i, stmt in enumerate(selected_statements):
            target_col = col_logic1 if i % 2 == 0 else col_logic2
            with target_col:
                statement_logic[stmt] = st.selectbox(
                    f"Match requirement for: {stmt[:40]}...",
                    options=[
                        "Any Agree (1 or 2)",
                        "Agree Completely (1 only)",
                        "Any Disagree (3 or 4)",
                        "Disagree Completely (4 only)"
                    ],
                    key=f"logic_{stmt}"
                )
        
        st.markdown("---")
        max_statements = len(selected_statements)
        threshold = st.slider(
            "Respondent must meet the requirements for at least how many of these statements?", 
            min_value=1, max_value=max_statements, value=max(1, int(max_statements * 0.7))
        )
        
        matches_df = pd.DataFrame(index=df_working.index)
        
        for stmt, logic in statement_logic.items():
            if logic == "Any Agree (1 or 2)":
                matches_df[stmt] = df_working[stmt].isin([1, 2]).astype(int)
            elif logic == "Agree Completely (1 only)":
                matches_df[stmt] = (df_working[stmt] == 1).astype(int)
            elif logic == "Any Disagree (3 or 4)":
                matches_df[stmt] = df_working[stmt].isin([3, 4]).astype(int)
            elif logic == "Disagree Completely (4 only)":
                matches_df[stmt] = (df_working[stmt] == 4).astype(int)
                
        df_working['agreement_count'] = matches_df.sum(axis=1)
        df_working['Custom_Segment'] = (df_working['agreement_count'] >= threshold).astype(int)
        
        raw_match = int(df_working['Custom_Segment'].sum())
        weighted_match = df_working[df_working['Custom_Segment'] == 1]['Weight'].sum()
        total_weighted = df_working['Weight'].sum()
        
        st.success(f"🧩 **Segment Active!** Identified {raw_match:,} respondents ({(weighted_match/total_weighted)*100:.1f}% of market).")
        segment_created = True

    st.markdown("---")
    
    # =====================================================================
    # OUTPUT TABS: PROFILER, CROSSTABS, & MAPS
    # =====================================================================
    if brand_cols or segment_created:
        tab1, tab2, tab3 = st.tabs(["🎯 Segment Profiler", "📊 On-Demand Crosstabs", "🗺️ Landscape Map"])
        
        # -------------------------------------------------------------
        # TAB 1: SEGMENT PROFILER (Brand Indexing)
        # -------------------------------------------------------------
        with tab1:
            st.subheader("Brand & Product Indexing")
            if not segment_created:
                st.info("Build a custom segment above to see what brands they over-index on.")
            elif not brand_cols:
                st.info("Select Brand columns in the sidebar to see indexing.")
            else:
                index_data = []
                for brand in brand_cols:
                    total_brand_buyers = df_working[df_working[brand] == 1]['Weight'].sum()
                    total_pop = df_working['Weight'].sum()
                    baseline_pct = total_brand_buyers / total_pop if total_pop > 0 else 0
                    
                    seg_pop = df_working[df_working['Custom_Segment'] == 1]['Weight'].sum()
                    seg_brand_buyers = df_working[(df_working['Custom_Segment'] == 1) & (df_working[brand] == 1)]['Weight'].sum()
                    seg_pct = seg_brand_buyers / seg_pop if seg_pop > 0 else 0
                    
                    idx_score = (seg_pct / baseline_pct * 100) if baseline_pct > 0 else 100
                    index_data.append({"Brand": brand, "Base %": baseline_pct*100, "Segment %": seg_pct*100, "Index Score": int(idx_score)})
                
                df_idx = pd.DataFrame(index_data).sort_values(by="Index Score", ascending=False)
                st.dataframe(df_idx.style.format({"Base %": "{:.1f}%", "Segment %": "{:.1f}%"}))
                
        # -------------------------------------------------------------
        # TAB 2: ON-DEMAND CROSSTABS (Now with Custom Segment Columns!)
        # -------------------------------------------------------------
        with tab2:
            st.subheader("Build a Custom Crosstab")
            
            # Default to all 36 psychographics for the rows
            ct_rows = st.multiselect(
                "Select Rows (e.g., Attitudes):", 
                list(PSYCHOGRAPHIC_MAP.values()), 
                default=list(PSYCHOGRAPHIC_MAP.values()), 
                key="ct_rows"
            )
            
            # Dynamically add the 'Custom_Segment' to the available columns
            available_cols = list(brand_cols)
            if segment_created:
                available_cols.insert(0, 'Custom_Segment')
                
            ct_cols = st.multiselect(
                "Select Columns (e.g., Brands or Custom Segment):", 
                available_cols, 
                default=['Custom_Segment'] if segment_created else [],
                key="ct_cols"
            )
            
            if ct_rows and ct_cols:
                matrix = []
                for r in ct_rows:
                    row_data = {"Statement (Any Agree)": r}
                    for c in ct_cols:
                        # Count weights where respondent matches the Row (Top-2 Box) AND the Column (Binary 1)
                        count = df_working[(df_working[r].isin([1, 2])) & (df_working[c] == 1)]['Weight'].sum()
                        row_data[c] = round(count)
                    matrix.append(row_data)
                
                df_ct = pd.DataFrame(matrix).set_index("Statement (Any Agree)")
                st.dataframe(df_ct)
                st.download_button("📥 Download Table as CSV", data=df_ct.to_csv().encode('utf-8'), file_name="custom_crosstab.csv", mime="text/csv")
                
        # -------------------------------------------------------------
        # TAB 3: LANDSCAPE MAP (Correspondence Analysis)
        # -------------------------------------------------------------
        with tab3:
            st.subheader("Competitive Landscape Map")
            st.markdown("Select core values to map the spatial relationship against your brands.")
            map_rows = st.multiselect("Select Core Values (Rows) to map:", list(PSYCHOGRAPHIC_MAP.values()), default=list(PSYCHOGRAPHIC_MAP.values())[:5])
            
            if st.button("🗺️ Generate Map") and map_rows and len(brand_cols) > 1:
                map_matrix = []
                for r in map_rows:
                    r_data = []
                    for c in brand_cols:
                        val = df_working[(df_working[r].isin([1, 2])) & (df_working[c] == 1)]['Weight'].sum()
                        r_data.append(val)
                    map_matrix.append(r_data)
                
                df_map = pd.DataFrame(map_matrix, index=map_rows, columns=brand_cols)
                df_map = df_map.loc[(df_map.sum(axis=1) > 0)] 
                
                if len(df_map) >= 2:
                    X = df_map.values.astype(float)
                    P = X / X.sum()
                    r_mass = P.sum(axis=1)
                    c_mass = P.sum(axis=0)
                    E = np.outer(r_mass, c_mass)
                    Z = (P - E) / np.sqrt(E)
                    U, D_sv, V_T = np.linalg.svd(Z, full_matrices=False)
                    
                    row_coords = np.diag(1.0 / np.sqrt(r_mass)) @ U @ np.diag(D_sv)
                    col_coords = np.diag(1.0 / np.sqrt(c_mass)) @ V_T.T @ np.diag(D_sv)
                    var_exp = (D_sv**2 / sum(D_sv**2)) * 100
                    
                    fig, ax = plt.subplots(figsize=(10, 8))
                    
                    ax.scatter(row_coords[:, 0], row_coords[:, 1], color='steelblue', s=60)
                    for i, txt in enumerate(df_map.index):
                        ax.annotate(txt[:25]+"...", (row_coords[i, 0], row_coords[i, 1] + 0.005), color='darkblue', fontsize=9)
                        
                    ax.scatter(col_coords[:, 0], col_coords[:, 1], color='crimson', marker='s', s=100)
                    for i, txt in enumerate(df_map.columns):
                        ax.annotate(txt, (col_coords[i, 0], col_coords[i, 1] - 0.015), color='darkred', fontsize=11, weight='bold')
                        
                    ax.axhline(0, color='black', linewidth=0.8)
                    ax.axvline(0, color='black', linewidth=0.8)
                    
                    max_val = max(np.abs(np.concatenate([row_coords[:, 0], col_coords[:, 0]])).max(), 
                                  np.abs(np.concatenate([row_coords[:, 1], col_coords[:, 1]])).max()) * 1.2
                    ax.set_xlim(-max_val, max_val)
                    ax.set_ylim(-max_val, max_val)
                    ax.set_xlabel(f"Dimension 1 ({var_exp[0]:.1f}%)")
                    ax.set_ylabel(f"Dimension 2 ({var_exp[1]:.1f}%)")
                    ax.grid(alpha=0.2)
                    st.pyplot(fig)
                else:
                    st.warning("Not enough data overlap to calculate dimensions. Select more variables.")
else:
    st.info("⬅️ Please upload the Master Data File (with Q-codes, demographics, and brands) in the sidebar to begin.")
