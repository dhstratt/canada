import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import io
import pickle

# =====================================================================
# INITIAL SETUP & PAGE CONFIG
# =====================================================================
st.set_page_config(page_title="Universal Market Mapper", layout="wide")

st.title("🎯 Universal Market Segment & Landscape Builder")
st.markdown("Upload your raw survey data. Build custom segments and crosstabs using every question, attitude, brand, and demographic simultaneously.")

# =====================================================================
# THE MEGA-CODEBOOK DICTIONARIES
# =====================================================================
BRANDS = {1: "Simply", 2: "Minute Maid", 3: "Fruitopia", 4: "Five Alive", 5: "Honest Kids", 6: "Allen's", 7: "Compliments", 8: "Del Monte", 9: "Dole", 10: "Fruité", 11: "Great Value", 12: "Kiju", 13: "Kool-Aid", 14: "Natural One", 15: "Oasis", 16: "Ocean Spray", 17: "President's Choice", 18: "Rougemont", 19: "Rubicon Exotic", 20: "Sunny Delight", 21: "SunRype", 22: "Tradition", 23: "Tropicana", 24: "Irresistible", 25: "Western Family", 26: "Other"}
CHANNELS = {1: "Grocery store", 2: "Ethnic Grocery", 3: "Mass retailer", 4: "Club store", 5: "Convenience store", 6: "Drug store", 7: "Gas station", 8: "Coffee shop", 9: "Deli", 10: "Restaurant", 11: "Other"}
SIZES = {1: "Large carton", 2: "Single carton", 3: "Large plastic jug", 4: "Can", 5: "Single plastic bottle", 6: "Fountain cup", 7: "Other"}
WHY_CHOOSE = {1: "Price/Value", 2: "Coupon/Incentive", 3: "Brand Loyalty", 4: "Trial/New", 5: "HH Request", 6: "Availability", 7: "Health Benefit", 8: "Convenience", 9: "Other"}
WHO_DRINKS = {1: "Child <6", 2: "Child 6-12", 3: "Child 13-17", 4: "Other adult", 5: "Myself"}
WHEN_HOW = {1: "With breakfast", 2: "Morning snack", 3: "Morning alone", 4: "With lunch", 5: "Afternoon snack", 6: "Afternoon alone", 7: "With dinner", 8: "Evening snack", 9: "Evening alone", 10: "Special occasion/treat", 11: "During/after exercise", 12: "Parties/social"}
FREQUENCY = {1: "Multiple times/day", 2: "Once a day", 3: "3-5 times/week", 4: "1-2 times/week", 5: "2-3 times/month", 6: "Rarely/infrequently"}
REASONS = {1: "Hydration & Refreshment", 2: "Energy & Focus", 3: "Health & Wellness", 4: "Indulgence & Craving", 5: "Routine & Habit", 6: "Social & Relaxation", 7: "Family Needs"}
BRAND_ATTITUDES = {1: "Upset if went away", 2: "For someone like me", 3: "Fond memories", 4: "Brand I trust", 5: "Cares about people like me", 6: "Modern brand", 7: "Proud to purchase", 8: "Price feels fair", 9: "Tastes superior", 10: "Know exactly what to expect", 11: "Positive relationship", 12: "Always find it", 13: "Proudly Canadian", 14: "None of these"}
KIDS_ATTITUDES = {1: "Healthy option for children", 2: "Feel guilty giving to children", 3: "Kids handle sugar better", 4: "Sugar is inescapable for kids", 5: "Give kids what they want", 6: "Gets kids to consume fruits/veg", 7: "Provides necessary vitamins"}
BEV_ATTITUDES_1 = {1: "Pay premium for quality", 2: "Simple ingredients", 3: "Cool packaging", 4: "Highly convenient", 5: "Daily routine", 6: "Always next to me", 7: "Sweet drink over sweet food", 8: "Smaller portion of real juice"}
BEV_ATTITUDES_2 = {1: "Bold/tart kick", 2: "Functional health benefits", 3: "Change depending on season", 4: "Don't worry about sugar", 5: "Strictly avoid added sugars", 6: "Less worried if health benefits", 7: "Actively limit due to sugar", 8: "Only zero-sugar"}

PSYCHOGRAPHICS = {
    "Q19_r1": "I thrive at big parties and social occasions", "Q19_r2": "I think of myself as an intellectual", "Q19_r3": "Spending time with my family is my top priority", "Q19_r4": "I am interested in finding out how I can help the environment", "Q19_r5": "I am an optimist", "Q19_r6": "I seek out variety in my everyday life", "Q19_r7": "I make sure I take time for myself each day", "Q19_r8": "I like to learn about foreign cultures", "Q19_r9": "I’m perfectly happy with my standard of living", "Q20_r1": "I like to change brands often for the sake of variety and novelty", "Q20_r2": "I buy based on quality, not price", "Q20_r3": "Price is more important to me than brand names", "Q20_r4": "Generic or store brand products are as effective as brand-name products", "Q20_r5": "I enjoy wandering the store looking for new, interesting products", "Q20_r6": "I tend to make impulse purchases", "Q20_r7": "My children have significant impact on the brands I choose", "Q20_r8": "I buy brands that reflect my style", "Q20_r9": "I am influenced by what's hot and what's not", "Q21_r1": "I prefer foods cooked with bold flavors", "Q21_r2": "Nutritional value is the most important factor when I'm choosing which foods to eat", "Q21_r3": "I eat the foods I like regardless of calories", "Q21_r4": "I believe in a healthy lifestyle instead of traditional dieting", "Q21_r5": "Food is a comfort to me", "Q21_r6": "I indulge my cravings for foods I enjoy", "Q21_r7": "I am loyal to my food brands and stick with them", "Q21_r8": "Fast food is junk food", "Q21_r9": "I prefer to eat foods without artificial ingredients", "Q21_r10": "I try to eat a healthy breakfast every day", "Q22_r1": "I am generally more fit and active than other people my age", "Q22_r2": "I frequently look for new ways to change up my exercise routine", "Q22_r3": "I regularly look for ways to get a better night’s sleep", "Q22_r4": "Because of my busy lifestyle, I don’t take care of myself as well as I should", "Q22_r5": "The health claims/benefits on a product package often influence my decision to buy it", "Q22_r6": "Taking care of your mental health is a critical part of your overall wellness", "Q22_r7": "I always do what my doctor tells me to do", "Q22_r8": "I consider my diet to be very healthy"
}

DEMO_MAP = {
    "S2": {2: "Province: BC", 3: "Province: Manitoba", 4: "Province: New Brunswick", 9: "Province: Ontario", 11: "Province: Quebec"},
    "S3": {2: "Age: 18-24", 3: "Age: 25-34", 4: "Age: 35-44", 5: "Age: 45-54", 6: "Age: 55-65"},
    "S4": {1: "Kids in HH: Yes", 2: "Kids in HH: No"},
    "D1": {1: "Gender: Female", 2: "Gender: Male", 3: "Gender: Non-Binary"},
    "D3": {1: "Marital: Single", 2: "Marital: Married", 3: "Marital: Living with Partner", 4: "Marital: Divorced", 5: "Marital: Separated", 6: "Marital: Widowed"},
    "D5": {1: "Income: <$25k", 2: "Income: $25k-$50k", 3: "Income: $50k-$75k", 4: "Income: $75k-$100k", 5: "Income: $100k-$150k", 6: "Income: $150k-$200k", 7: "Income: $200k+"},
    "D8": {1: "Immigration: 1st Gen", 2: "Immigration: 1.5 Gen", 3: "Immigration: 2nd Gen", 4: "Immigration: 3rd Gen"},
    "D10": {1: "Edu: Bachelor's", 2: "Edu: High School", 3: "Edu: College Diploma", 4: "Edu: Master's", 8: "Edu: Doctorate"},
    "D11": {1: "Employ: Full Time", 2: "Employ: Part Time", 4: "Employ: Student", 5: "Employ: Homemaker", 7: "Employ: Retired"}
}

# Variable Type Lists for UI Organization
PSYCHO_VARS = list(PSYCHOGRAPHICS.values())
BRAND_VARS = list(BRANDS.values())
DEMO_VARS = [val for subdict in DEMO_MAP.values() for val in subdict.values()]

SCALE_OPTIONS = [
    "Exact Match / YES (Binary)",
    "Does Not Match / NO (Binary)",
    "Any Agree (1 or 2 combined)",
    "Agree Completely (1 only)",
    "Agree Somewhat (2 only)",
    "Disagree Somewhat (3 only)",
    "Disagree Completely (4 only)",
    "Any Disagree (3 or 4 combined)"
]

# =====================================================================
# DATA PROCESSING FUNCTIONS (DYNAMIC TRANSLATION ENGINE)
# =====================================================================
@st.cache_data
def load_and_prep_data(file):
    if file.name.endswith('.csv'): df = pd.read_csv(file)
    else: df = pd.read_excel(file)
        
    df_clean = pd.DataFrame()
    if 'Weight' in df.columns: df_clean['Weight'] = df['Weight']
    else: df_clean['Weight'] = 1.0

    # 1. Base Demographics
    for col, value_map in DEMO_MAP.items():
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors='coerce')
            for val, label in value_map.items():
                df_clean[f"[Demo] {label}"] = (df[col] == val).astype(int)

    # 2. Brands Purchased (Q1)
    for b_idx, b_name in BRANDS.items():
        col = f"Q1_{b_idx}"
        if col in df.columns:
            df_clean[f"[Brand] Purchased: {b_name}"] = pd.to_numeric(df[col], errors='coerce').fillna(0).astype(int)

    # 3. Channels (Q2: r=Channel, c=Brand)
    for c_idx, c_name in CHANNELS.items():
        for b_idx, b_name in BRANDS.items():
            col = f"Q2_r{c_idx}_c{b_idx}"
            if col in df.columns:
                df_clean[f"[Channel] {c_name} - {b_name}"] = pd.to_numeric(df[col], errors='coerce').fillna(0).astype(int)

    # 4. Sizes (Q3: r=Size, c=Brand)
    for s_idx, s_name in SIZES.items():
        for b_idx, b_name in BRANDS.items():
            col = f"Q3_r{s_idx}_c{b_idx}"
            if col in df.columns:
                df_clean[f"[Size] {s_name} - {b_name}"] = pd.to_numeric(df[col], errors='coerce').fillna(0).astype(int)

    # 5. Why Choose (Q6: _reason.brand)
    for w_idx, w_name in WHY_CHOOSE.items():
        for b_idx, b_name in BRANDS.items():
            col = f"Q6_{w_idx}.{b_idx}"
            if col in df.columns:
                df_clean[f"[Why Choose] {w_name} - {b_name}"] = pd.to_numeric(df[col], errors='coerce').fillna(0).astype(int)

    # 6. Who Drinks (Q9: r=Who, c=Brand)
    for w_idx, w_name in WHO_DRINKS.items():
        for b_idx, b_name in BRANDS.items():
            col = f"Q9_r{w_idx}_c{b_idx}"
            if col in df.columns:
                df_clean[f"[Who Drinks] {w_name} - {b_name}"] = pd.to_numeric(df[col], errors='coerce').fillna(0).astype(int)

    # 7. When/How (Q9a: r=When, c=Brand)
    for w_idx, w_name in WHEN_HOW.items():
        for b_idx, b_name in BRANDS.items():
            col = f"Q9a_r{w_idx}_c{b_idx}"
            if col in df.columns:
                df_clean[f"[When/How] {w_name} - {b_name}"] = pd.to_numeric(df[col], errors='coerce').fillna(0).astype(int)

    # 8. Frequency (Q9b_c{brand} contains 1-6)
    for b_idx, b_name in BRANDS.items():
        col = f"Q9b_c{b_idx}"
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors='coerce')
            for f_idx, f_name in FREQUENCY.items():
                df_clean[f"[Frequency] {f_name} - {b_name}"] = (df[col] == f_idx).astype(int)

    # 9. Reasons (Q14_c{brand} contains 1-7)
    for b_idx, b_name in BRANDS.items():
        col = f"Q14_c{b_idx}"
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors='coerce')
            for r_idx, r_name in REASONS.items():
                df_clean[f"[Reason] {r_name} - {b_name}"] = (df[col] == r_idx).astype(int)

    # 10. Kids Attitudes (Q13 - Retain 1-4 scale)
    for r_idx, r_name in KIDS_ATTITUDES.items():
        col = f"Q13_r{r_idx}"
        if col in df.columns:
            df_clean[f"[Kids Attitudes] {r_name}"] = pd.to_numeric(df[col], errors='coerce').fillna(0)

    # 11. Bev Attitudes (Q16 and Q16x2)
    for idx, name in BEV_ATTITUDES_1.items():
        col = f"Q16_{idx}"
        if col in df.columns: df_clean[f"[Bev Attitudes] {name}"] = pd.to_numeric(df[col], errors='coerce').fillna(0).astype(int)
    for idx, name in BEV_ATTITUDES_2.items():
        col = f"Q16x2_{idx}"
        if col in df.columns: df_clean[f"[Bev Attitudes] {name}"] = pd.to_numeric(df[col], errors='coerce').fillna(0).astype(int)

    # 12. Brand Attitudes (Q17: r=Statement, c=Brand)
    for r_idx, r_name in BRAND_ATTITUDES.items():
        for b_idx, b_name in BRANDS.items():
            col = f"Q17_r{r_idx}_c{b_idx}"
            if col in df.columns:
                df_clean[f"[Brand Attitude] {r_name} - {b_name}"] = pd.to_numeric(df[col], errors='coerce').fillna(0).astype(int)

    # 13. Psychographics (Q19-Q22 - Retain 1-4 Scale)
    for q_code, english_stmt in PSYCHOGRAPHICS.items():
        if q_code in df.columns:
            df_clean[f"[Psychographics] {english_stmt}"] = pd.to_numeric(df[q_code], errors='coerce').fillna(0)
            
    return df_clean

def get_scale_mask(dataframe, column_name, logic_string):
    if logic_string == "Exact Match / YES (Binary)": return dataframe[column_name] == 1
    elif logic_string == "Does Not Match / NO (Binary)": return dataframe[column_name] == 0
    elif logic_string == "Any Agree (1 or 2 combined)": return dataframe[column_name].isin([1, 2])
    elif logic_string == "Agree Completely (1 only)": return dataframe[column_name] == 1
    elif logic_string == "Agree Somewhat (2 only)": return dataframe[column_name] == 2
    elif logic_string == "Disagree Somewhat (3 only)": return dataframe[column_name] == 3
    elif logic_string == "Disagree Completely (4 only)": return dataframe[column_name] == 4
    elif logic_string == "Any Disagree (3 or 4 combined)": return dataframe[column_name].isin([3, 4])
    return dataframe[column_name] == 1 

# =====================================================================
# SIDEBAR: UPLOAD & WORKSPACE MANAGEMENT
# =====================================================================
st.sidebar.header("1. Upload Data or Workspace")
uploaded_file = st.sidebar.file_uploader("Upload Master File (.csv/.xlsx) or Workspace (.pkl)", type=["csv", "xlsx", "pkl"])

if uploaded_file:
    with st.spinner("Translating raw survey variables into plain English..."):
        if uploaded_file.name.endswith('.pkl'):
            if 'data_loaded' not in st.session_state or st.session_state.get('file_name') != uploaded_file.name:
                workspace = pickle.loads(uploaded_file.getvalue())
                st.session_state['df_working'] = workspace['df_working']
                st.session_state['created_segments'] = workspace['created_segments']
                st.session_state['data_loaded'] = True
                st.session_state['file_name'] = uploaded_file.name
            st.sidebar.success(f"Workspace Restored! Loaded {len(st.session_state['created_segments'])} Custom Segments.")
        else:
            df_base = load_and_prep_data(uploaded_file)
            is_legacy_state = False
            if 'df_working' in st.session_state:
                if not any(c.startswith('[Demo]') for c in st.session_state['df_working'].columns):
                    is_legacy_state = True
            
            if 'data_loaded' not in st.session_state or st.session_state.get('file_name') != uploaded_file.name or is_legacy_state:
                st.session_state['df_working'] = df_base.copy()
                st.session_state['created_segments'] = []
                st.session_state['data_loaded'] = True
                st.session_state['file_name'] = uploaded_file.name
            st.sidebar.success(f"Loaded Master File: {len(df_base)} Respondents!")
    
    all_cols = [c for c in st.session_state['df_working'].columns if c != "Weight" and c not in st.session_state['created_segments']]
    CAT_DEMOS = [c for c in all_cols if c.startswith("[Demo]")]
    CAT_BRANDS = [c for c in all_cols if c.startswith("[Brand]") or c.startswith("[Size]")]
    CAT_CHANNELS = [c for c in all_cols if c.startswith("[Channel]") or c.startswith("[When/How]") or c.startswith("[Frequency]") or c.startswith("[Who Drinks]")]
    CAT_REASONS = [c for c in all_cols if c.startswith("[Why Choose]") or c.startswith("[Reason]")]
    CAT_ATTITUDES = [c for c in all_cols if c.startswith("[Psychographics]") or c.startswith("[Kids Attitudes]") or c.startswith("[Bev Attitudes]")]
    CAT_PERCEPTIONS = [c for c in all_cols if c.startswith("[Brand Attitude]")]
    
    if st.session_state['created_segments']:
        st.sidebar.markdown("---")
        st.sidebar.subheader("💾 Stored Segments")
        for seg in st.session_state['created_segments']:
            col_name, col_del = st.sidebar.columns([4, 1])
            col_name.markdown(f"`{seg}`")
            if col_del.button("❌", key=f"del_{seg}"):
                st.session_state['df_working'] = st.session_state['df_working'].drop(columns=[seg])
                st.session_state['created_segments'].remove(seg)
                st.rerun()
                
        st.sidebar.markdown("---")
        if st.sidebar.button("🗑️ Clear All Segments", type="secondary"):
            st.session_state['df_working'] = st.session_state['df_working'].drop(columns=st.session_state['created_segments'])
            st.session_state['created_segments'] = []
            st.rerun()

    st.sidebar.markdown("---")
    st.sidebar.subheader("📦 Export Current Workspace")
    workspace_export = {
        'df_working': st.session_state['df_working'],
        'created_segments': st.session_state['created_segments']
    }
    st.sidebar.download_button(
        label="💾 Download Workspace (.pkl)",
        data=pickle.dumps(workspace_export),
        file_name="my_segment_workspace.pkl",
        mime="application/octet-stream"
    )
    
    st.sidebar.markdown("---")
    if st.sidebar.button("🔄 Hard Reset App", type="secondary"):
        st.session_state.clear()
        st.rerun()

    # =====================================================================
    # MAIN WORKSPACE TABS
    # =====================================================================
    tab1, tab2, tab3 = st.tabs(["🛠️ Segment Builder & Sizing", "📊 Universal Crosstabs", "🗺️ Landscape Map"])
    
    # -------------------------------------------------------------
    # TAB 1: SEGMENT BUILDER & SIZING
    # -------------------------------------------------------------
    with tab1:
        st.subheader("Create a Custom Segment")
        st.markdown("Combine any variables from the survey into a custom mindset or behavioral segment.")
        
        col_pool, col_mand = st.columns(2)
        with col_pool:
            st.markdown("**A. Threshold Statement Pool**")
            threshold_statements = st.multiselect("Select variables for the 'Count' requirement:", options=all_cols)
            
        with col_mand:
            st.markdown("**B. Mandatory 'AND' Statements**")
            mandatory_statements = st.multiselect("Select variables that MUST be met (Optional):", options=[s for s in all_cols if s not in threshold_statements])
        
        all_selected = list(set(threshold_statements + mandatory_statements))
        
        if all_selected:
            st.markdown("---")
            st.markdown("### ⚙️ Fine-Tune Logic")
            
            statement_logic = {}
            col_logic1, col_logic2 = st.columns(2)
            
            for i, stmt in enumerate(all_selected):
                target_col = col_logic1 if i % 2 == 0 else col_logic2
                with target_col:
                    role_label = "(Threshold Pool)" if stmt in threshold_statements else "(Mandatory Rule)"
                    is_scale = ("[Psychographics]" in stmt) or ("[Kids Attitudes]" in stmt)
                    if is_scale: statement_logic[stmt] = st.selectbox(f"Match requirement for: {stmt[:35]}... {role_label}", options=SCALE_OPTIONS[2:], index=0, key=f"logic_{stmt}")
                    else:
                        st.info(f"✔️ **{stmt[:45]}...** (Auto-Matched as YES/NO)")
                        statement_logic[stmt] = "Exact Match / YES (Binary)"
            
            st.markdown("---")
            col_thresh, col_save = st.columns([2, 1])
            with col_thresh:
                if threshold_statements:
                    max_statements = len(threshold_statements)
                    threshold = st.slider("Must meet requirements for at least how many of the Threshold Statements?", min_value=1, max_value=max_statements, value=max(1, int(max_statements * 0.7)))
                else:
                    threshold = 0
                    st.caption("No Threshold pool selected. Evaluating Mandatory statements only.")
                
            matches_df = pd.DataFrame(index=st.session_state['df_working'].index)
            for stmt, logic in statement_logic.items():
                matches_df[stmt] = get_scale_mask(st.session_state['df_working'], stmt, logic).astype(bool)
                    
            if threshold_statements: meets_threshold = matches_df[threshold_statements].sum(axis=1) >= threshold
            else: meets_threshold = pd.Series(True, index=matches_df.index)
                
            if mandatory_statements: meets_mandatory = matches_df[mandatory_statements].all(axis=1)
            else: meets_mandatory = pd.Series(True, index=matches_df.index)
                
            temp_segment = (meets_threshold & meets_mandatory).astype(int)
            raw_match = int(temp_segment.sum())
            total_weighted = st.session_state['df_working']['Weight'].sum()
            weighted_match = st.session_state['df_working'][temp_segment == 1]['Weight'].sum()
            
            st.success(f"📊 **Dynamic Preview:** This configuration currently captures **{raw_match:,}** respondents ({(weighted_match/total_weighted)*100:.1f}% of total market).")
            
            with col_save:
                segment_name = st.text_input("Name your Segment:", value="New Segment 1")
                if st.button("💾 Save Segment to Workspace", type="primary"):
                    if segment_name in st.session_state['created_segments'] or segment_name in all_cols: st.error("A segment with this name already exists.")
                    else:
                        st.session_state['df_working'][segment_name] = temp_segment
                        st.session_state['created_segments'].append(segment_name)
                        st.rerun()

        st.markdown("---")
        st.subheader("📏 Saved Segments Sizing")
        if st.session_state['created_segments']:
            sizing_data = []
            total_pop = st.session_state['df_working']['Weight'].sum()
            for seg in st.session_state['created_segments']:
                seg_wgt = st.session_state['df_working'][st.session_state['df_working'][seg] == 1]['Weight'].sum()
                seg_unw = len(st.session_state['df_working'][st.session_state['df_working'][seg] == 1])
                sizing_data.append({"Segment Name": seg, "Unweighted Count": seg_unw, "Weighted Count": int(seg_wgt), "% of Total Market": (seg_wgt / total_pop) if total_pop > 0 else 0})
            st.dataframe(pd.DataFrame(sizing_data).style.format({"% of Total Market": "{:.1%}", "Unweighted Count": "{:,}", "Weighted Count": "{:,}"}), use_container_width=True)
        else:
            st.info("No segments have been created yet. Build and save a segment above to see its sizing here.")

    # -------------------------------------------------------------
    # TAB 2: UNIVERSAL CROSSTABS
    # -------------------------------------------------------------
    with tab2:
        st.subheader("Build a Custom Crosstab")
        
        with st.expander("⚡ Quick Combiner (AND / OR Logic)", expanded=False):
            st.markdown("Instantly combine variables to use in your crosstabs without leaving this tab. *(Note: Any 1-4 scale Attitudes selected here will automatically be evaluated as 'Any Agree').*")
            qc_cols = st.columns([3, 1, 2])
            with qc_cols[0]: qc_vars = st.multiselect("Select Variables to Combine:", all_cols, key="qc_vars")
            with qc_cols[1]: qc_logic = st.radio("Combine Using:", ["AND (Must meet ALL)", "OR (Must meet ANY)"], key="qc_logic")
            with qc_cols[2]:
                qc_name = st.text_input("Name this Combination:", "New Combined Var", key="qc_name")
                if st.button("➕ Add to Crosstab Buckets", use_container_width=True):
                    if qc_name in st.session_state['created_segments'] or qc_name in all_cols: st.error("Name already exists!")
                    elif len(qc_vars) < 2: st.warning("Please select at least 2 variables to combine.")
                    else:
                        qc_mask = pd.Series(True, index=st.session_state['df_working'].index) if "AND" in qc_logic else pd.Series(False, index=st.session_state['df_working'].index)
                        for v in qc_vars:
                            is_scale = ("[Psychographics]" in v) or ("[Kids Attitudes]" in v)
                            v_mask = st.session_state['df_working'][v].isin([1, 2]) if is_scale else st.session_state['df_working'][v] == 1
                            if "AND" in qc_logic: qc_mask = qc_mask & v_mask
                            else: qc_mask = qc_mask | v_mask
                                
                        st.session_state['df_working'][qc_name] = qc_mask.astype(int)
                        st.session_state['created_segments'].append(qc_name)
                        st.success(f"✅ {qc_name} added to Saved Segments!")
                        st.rerun()

        st.markdown("---")
        st.markdown("##### ➡️ Select Rows")
        r_col1, r_col2, r_col3, r_col4 = st.columns(4)
        with r_col1: row_demos = st.multiselect("Demographics", CAT_DEMOS, key="r_demo")
        with r_col2: row_brands = st.multiselect("Brands & Products", CAT_BRANDS, key="r_brand")
        with r_col3: row_psycho = st.multiselect("Attitudes", CAT_ATTITUDES, key="r_psycho")
        with r_col4: row_segs = st.multiselect("Saved Segments", st.session_state['created_segments'], key="r_segs")
        
        with st.expander("➕ View More Row Categories", expanded=False):
            ex_r1, ex_r2, ex_r3 = st.columns(3)
            with ex_r1: row_chan = st.multiselect("Channels & Occasions", CAT_CHANNELS, key="r_chan")
            with ex_r2: row_reas = st.multiselect("Drivers & Reasons", CAT_REASONS, key="r_reas")
            with ex_r3: row_perc = st.multiselect("Brand Perceptions", CAT_PERCEPTIONS, key="r_perc")
            
        ct_rows = row_demos + row_brands + row_psycho + row_segs + row_chan + row_reas + row_perc
        
        st.markdown("---")
        st.markdown("##### ⬇️ Select Columns")
        c_col1, c_col2, c_col3, c_col4 = st.columns(4)
        with c_col1: col_demos = st.multiselect("Demographics ", CAT_DEMOS, key="c_demo")
        with c_col2: col_brands = st.multiselect("Brands & Products ", CAT_BRANDS, key="c_brand")
        with c_col3: col_psycho = st.multiselect("Attitudes ", CAT_ATTITUDES, key="c_psycho")
        with c_col4: col_segs = st.multiselect("Saved Segments ", st.session_state['created_segments'], default=st.session_state['created_segments'], key="c_segs")
        
        with st.expander("➕ View More Column Categories", expanded=False):
            ex_c1, ex_c2, ex_c3 = st.columns(3)
            with ex_c1: col_chan = st.multiselect("Channels & Occasions ", CAT_CHANNELS, key="c_chan")
            with ex_c2: col_reas = st.multiselect("Drivers & Reasons ", CAT_REASONS, key="c_reas")
            with ex_c3: col_perc = st.multiselect("Brand Perceptions ", CAT_PERCEPTIONS, key="c_perc")

        ct_cols = col_demos + col_brands + col_psycho + col_segs + col_chan + col_reas + col_perc
        
        # --- NEW: UNIVERSAL LOGIC FINE-TUNER FOR BOTH ROWS AND COLUMNS ---
        if ct_rows and ct_cols:
            scale_vars_in_ct = [v for v in set(ct_rows + ct_cols) if ("[Psychographics]" in v) or ("[Kids Attitudes]" in v)]
            ct_logic_dict = {}
            if scale_vars_in_ct:
                with st.expander("⚙️ Fine-Tune Attitude Scales for Rows & Columns (Defaults to Any Agree)", expanded=False):
                    col_rl1, col_rl2 = st.columns(2)
                    for i, v in enumerate(scale_vars_in_ct):
                        t_col = col_rl1 if i % 2 == 0 else col_rl2
                        with t_col:
                            ct_logic_dict[v] = st.selectbox(f"{v[:40]}...", options=SCALE_OPTIONS[2:], index=0, key=f"ct_logic_all_{v}")

            total_unweighted = len(st.session_state['df_working'])
            total_weighted = st.session_state['df_working']['Weight'].sum()
            
            export_data = []
            universe_row = ["Study Universe", total_unweighted, 1.00, 1.00, 100]
            
            col_baselines = {}
            for c in ct_cols:
                is_scale = ("[Psychographics]" in c) or ("[Kids Attitudes]" in c)
                if is_scale:
                    logic = ct_logic_dict.get(c, "Any Agree (1 or 2 combined)")
                    col_mask = get_scale_mask(st.session_state['df_working'], c, logic)
                    short_suffix = logic.split(" (")[0]
                    c_label = f"{c} ({short_suffix})"
                else:
                    col_mask = st.session_state['df_working'][c] == 1
                    c_label = c
                    
                col_unweighted = len(st.session_state['df_working'][col_mask])
                col_weighted = st.session_state['df_working'][col_mask]['Weight'].sum()
                col_baselines[c] = {"unw": col_unweighted, "wgt": col_weighted, "mask": col_mask, "label": c_label}
                universe_row.extend([col_unweighted, 1.00, (col_weighted / total_weighted) if total_weighted > 0 else 0, 100])
                
            export_data.append(universe_row)
            
            for r in ct_rows:
                is_scale = ("[Psychographics]" in r) or ("[Kids Attitudes]" in r)
                if is_scale:
                    logic = ct_logic_dict.get(r, "Any Agree (1 or 2 combined)")
                    r_mask = get_scale_mask(st.session_state['df_working'], r, logic)
                    short_suffix = logic.split(" (")[0]
                    r_label = f"{r} ({short_suffix})"
                else:
                    r_mask = st.session_state['df_working'][r] == 1
                    r_label = r
                
                stmt_unweighted = len(st.session_state['df_working'][r_mask])
                stmt_weighted = st.session_state['df_working'][r_mask]['Weight'].sum()
                stmt_vert_pct = (stmt_weighted / total_weighted) if total_weighted > 0 else 0
                
                r_data = [r_label, stmt_unweighted, stmt_vert_pct, 1.00, 100]
                
                for c in ct_cols:
                    c_mask = col_baselines[c]["mask"]
                    cross_unweighted = len(st.session_state['df_working'][r_mask & c_mask])
                    cross_weighted = st.session_state['df_working'][r_mask & c_mask]['Weight'].sum()
                    
                    col_wgt_base = col_baselines[c]["wgt"]
                    vert_pct = (cross_weighted / col_wgt_base) if col_wgt_base > 0 else 0
                    horz_pct = (cross_weighted / stmt_weighted) if stmt_weighted > 0 else 0
                    idx_score = (vert_pct / stmt_vert_pct * 100) if stmt_vert_pct > 0 else 0
                    
                    r_data.extend([cross_unweighted, vert_pct, horz_pct, int(round(idx_score, 0))])
                    
                export_data.append(r_data)
            
            preview_headers = ["Statement"]
            metrics = ["Unweighted", "Vertical(%)", "Horizontal(%)", "Index"]
            for m in metrics: preview_headers.append(f"Study Universe - {m}")
            for c in ct_cols:
                c_display = col_baselines[c]["label"]
                for m in metrics: preview_headers.append(f"{c_display} - {m}")
                    
            df_preview = pd.DataFrame(export_data, columns=preview_headers).set_index("Statement")
            
            st.markdown("---")
            st.markdown("**Preview (First 10 Rows):**")
            format_dict = {}
            for col in df_preview.columns:
                if "Vertical" in col or "Horizontal" in col: format_dict[col] = "{:.1%}" 
                elif "Unweighted" in col: format_dict[col] = "{:,.0f}"
                elif "Index" in col: format_dict[col] = "{:.0f}"
            st.dataframe(df_preview.head(10).style.format(format_dict))
            
            excel_headers = ["Statement", "Study Universe", "", "", ""] 
            excel_sub_headers = ["", "Unweighted", "Vertical(%)", "Horizontal(%)", "Index"]
            for c in ct_cols:
                c_display = col_baselines[c]["label"]
                excel_headers.extend([c_display, "", "", ""])
                excel_sub_headers.extend(["Unweighted", "Vertical(%)", "Horizontal(%)", "Index"])
                
            df_excel = pd.DataFrame(export_data).set_index(0)
            df_excel.index.name = "Statement"
            df_excel.columns = pd.MultiIndex.from_tuples(zip(excel_headers[1:], excel_sub_headers[1:]))
            
            output = io.BytesIO()
            with pd.ExcelWriter(output, engine='openpyxl') as writer:
                pd.DataFrame([["CROSSTAB TITLE : Universal Crosstabs"], ["STUDY NAME : Advanced Market Mapper"], ["WEIGHT TYPE : Unweighted / Population"], ["SELECTED BASE : Study Universe"]]).to_excel(writer, index=False, header=False, sheet_name='Crosstab', startrow=0)
                df_excel.to_excel(writer, index=True, sheet_name='Crosstab', startrow=9)
                
                worksheet = writer.sheets['Crosstab']
                for row in worksheet.iter_rows(min_row=12, max_row=worksheet.max_row):
                    for cell in row:
                        if cell.column == 1: continue  
                        col_mod = (cell.column - 1) % 4
                        if col_mod in [2, 3]: cell.number_format = '0.1%'
                        elif col_mod == 1: cell.number_format = '#,##0'
                        elif col_mod == 0: cell.number_format = '0'
                            
            output.seek(0)
            st.download_button(label="📥 Download MRI-Formatted Excel Crosstab", data=output, file_name="Universal_Crosstab.xlsx", mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet", type="primary")
            
    # -------------------------------------------------------------
    # TAB 3: LANDSCAPE MAP
    # -------------------------------------------------------------
    with tab3:
        st.subheader("Competitive Landscape Map")
        map_rows = st.multiselect("Select Core Values (Rows) to map:", CAT_ATTITUDES + CAT_DEMOS, default=CAT_ATTITUDES[:5])
        map_cols = st.multiselect("Select Columns (Brands/Segments) to map:", CAT_BRANDS + st.session_state['created_segments'], default=CAT_BRANDS[:3])
        
        # --- NEW: TAB 3 SCALE FINE TUNER ---
        if map_rows and map_cols:
            scale_vars_map = [v for v in set(map_rows + map_cols) if ("[Psychographics]" in v) or ("[Kids Attitudes]" in v)]
            map_logic_dict = {}
            if scale_vars_map:
                with st.expander("⚙️ Fine-Tune Attitude Scales (Defaults to Any Agree)", expanded=False):
                    col_ml1, col_ml2 = st.columns(2)
                    for i, v in enumerate(scale_vars_map):
                        m_col = col_ml1 if i % 2 == 0 else col_ml2
                        with m_col:
                            map_logic_dict[v] = st.selectbox(f"{v[:40]}...", options=SCALE_OPTIONS[2:], index=0, key=f"map_logic_{v}")
        
        if st.button("🗺️ Generate Map") and map_rows and len(map_cols) > 1:
            map_matrix = []
            for r in map_rows:
                r_data = []
                is_scale_r = ("[Psychographics]" in r) or ("[Kids Attitudes]" in r)
                if is_scale_r:
                    logic = map_logic_dict.get(r, "Any Agree (1 or 2 combined)")
                    r_mask = get_scale_mask(st.session_state['df_working'], r, logic)
                else: 
                    r_mask = st.session_state['df_working'][r] == 1
                    
                for c in map_cols:
                    is_scale_c = ("[Psychographics]" in c) or ("[Kids Attitudes]" in c)
                    if is_scale_c:
                        logic = map_logic_dict.get(c, "Any Agree (1 or 2 combined)")
                        c_mask = get_scale_mask(st.session_state['df_working'], c, logic)
                    else: 
                        c_mask = st.session_state['df_working'][c] == 1
                        
                    val = st.session_state['df_working'][r_mask & c_mask]['Weight'].sum()
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
                for i, txt in enumerate(df_map.index): ax.annotate(txt[:25]+"...", (row_coords[i, 0], row_coords[i, 1] + 0.005), color='darkblue', fontsize=9)
                ax.scatter(col_coords[:, 0], col_coords[:, 1], color='crimson', marker='s', s=100)
                for i, txt in enumerate(df_map.columns): ax.annotate(txt, (col_coords[i, 0], col_coords[i, 1] - 0.015), color='darkred', fontsize=11, weight='bold')
                ax.axhline(0, color='black', linewidth=0.8)
                ax.axvline(0, color='black', linewidth=0.8)
                st.pyplot(fig)
            else:
                st.warning("Not enough data overlap to calculate dimensions.")
else:
    st.info("⬅️ Please upload the Master Data File in the sidebar to begin.")
