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
        
        for seg in st.session_state['created_segments']:
            col_name, col_del = st.sidebar.columns([4, 1])
            col_name.markdown(f"`{seg}`")
            if col_del.button("❌", key=f"del_{seg}", help=f"Delete {seg}"):
                st.session_state['df_working'] = st.session_state['df_working'].drop(columns=[seg])
                st.session_state['created_segments'].remove(seg)
                st.rerun()
                
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
    st.markdown("Define the pool of statements for your sliding threshold, and/or assign statements that act as mandatory 'AND' rules.")
    
    col_pool, col_mand = st.columns(2)
    
    with col_pool:
        st.subheader("A. Threshold Statement Pool")
        threshold_statements = st.multiselect(
            "Select statements for the 'Count' requirement:", 
            options=ENGLISH_STATEMENTS,
            help="These statements are tied to the threshold slider (e.g., Must meet 3 out of these 5)."
        )
        
    with col_mand:
        st.subheader("B. Mandatory 'AND' Statements")
        mandatory_statements = st.multiselect(
            "Select statements that MUST be met (Optional):", 
            options=[s for s in ENGLISH_STATEMENTS if s not in threshold_statements],
            help="Any statement added here operates as a strict YES/NO. The respondent MUST meet this rule regardless of their threshold score."
        )
    
    all_selected = list(set(threshold_statements + mandatory_statements))
    
    if all_selected:
        st.markdown("---")
        st.markdown("### ⚙️ Fine-Tune Statement Logic")
        
        statement_logic = {}
        col_logic1, col_logic2 = st.columns(2)
        
        for i, stmt in enumerate(all_selected):
            target_col = col_logic1 if i % 2 == 0 else col_logic2
            with target_col:
                role_label = "(Threshold Pool)" if stmt in threshold_statements else "(Mandatory Rule)"
                statement_logic[stmt] = st.selectbox(
                    f"Match requirement for: {stmt[:30]}... {role_label}",
                    options=["Any Agree (1 or 2)", "Agree Completely (1 only)", "Any Disagree (3 or 4)", "Disagree Completely (4 only)"],
                    key=f"logic_{stmt}"
                )
        
        st.markdown("---")
        
        col_thresh, col_save = st.columns([2, 1])
        with col_thresh:
            if threshold_statements:
                max_statements = len(threshold_statements)
                threshold = st.slider(
                    "Respondent must meet requirements for at least how many of the Threshold Statements?", 
                    min_value=1, max_value=max_statements, value=max(1, int(max_statements * 0.7))
                )
            else:
                threshold = 0
                st.info("No Threshold pool selected. Evaluating Mandatory statements only.")
            
        # =====================================================================
        # DYNAMIC PREVIEW SIZING CALCULATION (Threshold + AND Logic)
        # =====================================================================
        matches_df = pd.DataFrame(index=st.session_state['df_working'].index)
        
        for stmt, logic in statement_logic.items():
            if logic == "Any Agree (1 or 2)":
                matches_df[stmt] = st.session_state['df_working'][stmt].isin([1, 2]).astype(bool)
            elif logic == "Agree Completely (1 only)":
                matches_df[stmt] = (st.session_state['df_working'][stmt] == 1).astype(bool)
            elif logic == "Any Disagree (3 or 4)":
                matches_df[stmt] = st.session_state['df_working'][stmt].isin([3, 4]).astype(bool)
            elif logic == "Disagree Completely (4 only)":
                matches_df[stmt] = (st.session_state['df_working'][stmt] == 4).astype(bool)
                
        if threshold_statements:
            meets_threshold = matches_df[threshold_statements].sum(axis=1) >= threshold
        else:
            meets_threshold = pd.Series(True, index=matches_df.index)
            
        if mandatory_statements:
            meets_mandatory = matches_df[mandatory_statements].all(axis=1)
        else:
            meets_mandatory = pd.Series(True, index=matches_df.index)
            
        temp_segment = (meets_threshold & meets_mandatory).astype(int)
        
        raw_match = int(temp_segment.sum())
        total_weighted = st.session_state['df_working']['Weight'].sum()
        weighted_match = st.session_state['df_working'][temp_segment == 1]['Weight'].sum()
        
        st.info(f"📊 **Dynamic Preview:** This configuration currently captures **{raw_match:,}** respondents ({(weighted_match/total_weighted)*100:.1f}% of total market).")
        
        with col_save:
            segment_name = st.text_input("Name your Segment:", value="New Segment 1")
            
            if st.button("💾 Save Segment to Workspace", type="primary"):
                if segment_name in st.session_state['created_segments']:
                    st.error("A segment with this name already exists. Please choose a different name.")
                else:
                    st.session_state['df_working'][segment_name] = temp_segment
                    st.session_state['created_segments'].append(segment_name)
                    st.success(f"✅ '{segment_name}' successfully added to workspace!")
                    st.rerun()

    st.markdown("---")
    
    # =====================================================================
    # OUTPUT TABS: PROFILER, CROSSTABS, & MAPS
    # =====================================================================
    if brand_cols or st.session_state['created_segments']:
        tab1, tab2, tab3 = st.tabs(["🎯 Segment Profiler", "📊 On-Demand Crosstabs", "🗺️ Landscape Map"])
        
        # -------------------------------------------------------------
        # TAB 1: SEGMENT PROFILER
        # -------------------------------------------------------------
        with tab1:
            st.subheader("Brand & Product Indexing")
            if not st.session_state['created_segments']:
                st.info("Save a custom segment above to see what brands they over-index on.")
            elif not brand_cols:
                st.info("Select Brand columns in the sidebar to see indexing.")
            else:
                target_segment = st.selectbox("Select Stored Segment to Profile:", st.session_state['created_segments'])
                
                index_data = []
                for brand in brand_cols:
                    total_brand_buyers = st.session_state['df_working'][st.session_state['df_working'][brand] == 1]['Weight'].sum()
                    total_pop = st.session_state['df_working']['Weight'].sum()
                    baseline_pct = total_brand_buyers / total_pop if total_pop > 0 else 0
                    
                    seg_pop = st.session_state['df_working'][st.session_state['df_working'][target_segment] == 1]['Weight'].sum()
                    seg_brand_buyers = st.session_state['df_working'][(st.session_state['df_working'][target_segment] == 1) & (st.session_state['df_working'][brand] == 1)]['Weight'].sum()
                    seg_pct = seg_brand_buyers / seg_pop if seg_pop > 0 else 0
                    
                    idx_score = (seg_pct / baseline_pct * 100) if baseline_pct > 0 else 100
                    index_data.append({"Brand": brand, "Base %": baseline_pct*100, "Segment %": seg_pct*100, "Index Score": int(idx_score)})
                
                df_idx = pd.DataFrame(index_data).sort_values(by="Index Score", ascending=False)
                
                st.metric("Total Size of Segment", f"{int(seg_pop):,}", f"{(seg_pop/total_pop)*100:.1f}% of Market")
                st.dataframe(df_idx.style.format({"Base %": "{:.1f}%", "Segment %": "{:.1f}%"}))
                
        # -------------------------------------------------------------
        # TAB 2: ON-DEMAND CROSSTABS (Unweighted Layout)
        # -------------------------------------------------------------
        with tab2:
            st.subheader("Build a Custom Crosstab")
            
            ct_rows = st.multiselect(
                "Select Rows (e.g., Attitudes):", 
                ENGLISH_STATEMENTS, 
                default=ENGLISH_STATEMENTS[:5], 
                key="ct_rows"
            )
            
            available_cols = list(brand_cols) + st.session_state['created_segments']
                
            ct_cols = st.multiselect(
                "Select Columns (e.g., Brands or Stored Segments):", 
                available_cols, 
                default=st.session_state['created_segments'] if st.session_state['created_segments'] else (available_cols[:1] if available_cols else []),
                key="ct_cols"
            )
            
            if ct_rows and ct_cols:
                total_unweighted = len(st.session_state['df_working'])
                total_weighted = st.session_state['df_working']['Weight'].sum()
                
                export_data = []
                # Remove "Weighted" column logic, just Unw, Vert%, Horz%, Index
                universe_row = ["Study Universe", total_unweighted, 1.00, 1.00, 100]
                
                col_baselines = {}
                for c in ct_cols:
                    col_unweighted = len(st.session_state['df_working'][st.session_state['df_working'][c] == 1])
                    col_weighted = st.session_state['df_working'][st.session_state['df_working'][c] == 1]['Weight'].sum()
                    col_baselines[c] = {"unw": col_unweighted, "wgt": col_weighted}
                    
                    universe_row.extend([
                        col_unweighted,
                        1.00, 
                        (col_weighted / total_weighted) if total_weighted > 0 else 0, 
                        100 
                    ])
                    
                export_data.append(universe_row)
                
                for r in ct_rows:
                    stmt_unweighted = len(st.session_state['df_working'][st.session_state['df_working'][r].isin([1, 2])])
                    stmt_weighted = st.session_state['df_working'][st.session_state['df_working'][r].isin([1, 2])]['Weight'].sum()
                    stmt_vert_pct = (stmt_weighted / total_weighted) if total_weighted > 0 else 0
                    
                    r_data = [r, stmt_unweighted, stmt_vert_pct, 1.00, 100]
                    
                    for c in ct_cols:
                        cross_unweighted = len(st.session_state['df_working'][(st.session_state['df_working'][r].isin([1, 2])) & (st.session_state['df_working'][c] == 1)])
                        cross_weighted = st.session_state['df_working'][(st.session_state['df_working'][r].isin([1, 2])) & (st.session_state['df_working'][c] == 1)]['Weight'].sum()
                        
                        col_wgt_base = col_baselines[c]["wgt"]
                        
                        vert_pct = (cross_weighted / col_wgt_base) if col_wgt_base > 0 else 0
                        horz_pct = (cross_weighted / stmt_weighted) if stmt_weighted > 0 else 0
                        idx_score = (vert_pct / stmt_vert_pct * 100) if stmt_vert_pct > 0 else 0
                        
                        r_data.extend([
                            cross_unweighted,
                            vert_pct,
                            horz_pct,
                            int(round(idx_score, 0))
                        ])
                        
                    export_data.append(r_data)
                
                # 1. FLAT STRUCTURE FOR STREAMLIT PREVIEW
                preview_headers = ["Statement"]
                metrics = ["Unweighted", "Vertical(%)", "Horizontal(%)", "Index"]
                
                for m in metrics:
                    preview_headers.append(f"Study Universe - {m}")
                for c in ct_cols:
                    for m in metrics:
                        preview_headers.append(f"{c} - {m}")
                        
                df_preview = pd.DataFrame(export_data, columns=preview_headers).set_index("Statement")
                
                st.markdown("**Preview (First 10 Rows):**")
                
                format_dict = {}
                for col in df_preview.columns:
                    if "Vertical" in col or "Horizontal" in col:
                        format_dict[col] = "{:.1%}" 
                    elif "Unweighted" in col:
                        format_dict[col] = "{:,.0f}"
                    elif "Index" in col:
                        format_dict[col] = "{:.0f}"
                
                st.dataframe(df_preview.head(10).style.format(format_dict))
                
                # 2. MULTI-INDEX STRUCTURE FOR EXCEL EXPORT
                excel_headers = ["Statement", "Study Universe", "", "", ""] # 4 total columns for base
                excel_sub_headers = ["", "Unweighted", "Vertical(%)", "Horizontal(%)", "Index"]
                
                for c in ct_cols:
                    excel_headers.extend([c, "", "", ""])
                    excel_sub_headers.extend(["Unweighted", "Vertical(%)", "Horizontal(%)", "Index"])
                    
                df_excel = pd.DataFrame(export_data)
                df_excel.columns = pd.MultiIndex.from_tuples(zip(excel_headers, excel_sub_headers))
                
                df_excel = df_excel.set_index(("Statement", ""))
                
                output = io.BytesIO()
                with pd.ExcelWriter(output, engine='openpyxl') as writer:
                    meta_data = pd.DataFrame([
                        ["CROSSTAB TITLE : Custom Segment Profiles"],
                        ["STUDY NAME : Advanced Market Mapper"],
                        ["WEIGHT TYPE : Unweighted / Population"],
                        ["DATE EXECUTED : Auto-Generated"],
                        [""],
                        ["SELECTED BASE : Study Universe"],
                        [""]
                    ])
                    meta_data.to_excel(writer, index=False, header=False, sheet_name='Crosstab', startrow=0)
                    
                    df_excel.to_excel(writer, index=True, sheet_name='Crosstab', startrow=9)
                    
                    # 3. NATIVE EXCEL FORMATTING VIA OPENPYXL (Updated for 4-column blocks)
                    workbook = writer.book
                    worksheet = writer.sheets['Crosstab']
                    
                    for row in worksheet.iter_rows(min_row=12, max_row=worksheet.max_row):
                        for cell in row:
                            if cell.column == 1:
                                continue  # Skip Statement text
                            
                            col_mod = (cell.column - 1) % 4
                            
                            if col_mod in [2, 3]:   # Vertical(%) and Horizontal(%)
                                cell.number_format = '0.1%'
                            elif col_mod == 1:      # Unweighted Count
                                cell.number_format = '#,##0'
                            elif col_mod == 0:      # Index Score
                                cell.number_format = '0'
                                
                output.seek(0)
                
                st.download_button(
                    label="📥 Download MRI-Formatted Excel Crosstab",
                    data=output,
                    file_name="MRI_Format_Crosstab.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                    type="primary"
                )
                
        # -------------------------------------------------------------
        # TAB 3: LANDSCAPE MAP
        # -------------------------------------------------------------
        with tab3:
            st.subheader("Competitive Landscape Map")
            map_rows = st.multiselect("Select Core Values (Rows) to map:", ENGLISH_STATEMENTS, default=ENGLISH_STATEMENTS[:5])
            map_cols = st.multiselect("Select Columns (Brands/Segments) to map:", available_cols, default=brand_cols[:5] if brand_cols else available_cols[:3])
            
            if st.button("🗺️ Generate Map") and map_rows and len(map_cols) > 1:
                map_matrix = []
                for r in map_rows:
                    r_data = []
                    for c in map_cols:
                        val = st.session_state['df_working'][(st.session_state['df_working'][r].isin([1, 2])) & (st.session_state['df_working'][c] == 1)]['Weight'].sum()
                        r_data.append(val)
                    map_matrix.append(r_data)
                
                df_map = pd.DataFrame(map_matrix, index=map_rows, columns=map_cols)
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
    st.info("⬅️ Please upload the Master Data File in the sidebar to begin.")
