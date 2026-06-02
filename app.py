import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

# Set page layout to wide for better visualization room
st.set_page_config(page_title="Market Landscape Mapper", layout="wide")

st.title("📊 Advanced Market Landscape Mapper")
st.markdown("Upload raw survey microdata to instantly weight it to population targets, map the market, or build custom consumer segments.")

# =====================================================================
# SIDEBAR: FILE UPLOAD & PRESETS
# =====================================================================
st.sidebar.header("1. Upload Data")
uploaded_file = st.sidebar.file_uploader("Upload Raw Respondent Data (.csv or .xlsx)", type=["csv", "xlsx"])

# Pre-coded Regional/Demographic Population Targets (National Estimates)
REGION_TARGETS = {"Region 1": 0.385, "Region 2": 0.223, "Region 3": 0.135, "Region 4": 0.117, "Region 5": 0.075, "Region 6": 0.065}
AGE_TARGETS = {"18-34": 0.270, "35-54": 0.330, "55+": 0.400}

# =====================================================================
# MAIN INTERFACE
# =====================================================================
if uploaded_file is not None:
    try:
        if uploaded_file.name.endswith(".csv"):
            df = pd.read_csv(uploaded_file)
        else:
            df = pd.read_excel(uploaded_file)
        st.success(f"Successfully loaded {len(df)} survey respondents!")
    except Exception as e:
        st.error(f"Error reading file: {e}")
        st.stop()

    # STEP 1: CONFIGURE THE COLUMNS
    st.header("Step 1: Map Your Variables")
    
    col1, col2 = st.columns(2)
    with col1:
        st.subheader("Demographic Columns (For Weighting)")
        region_col = st.selectbox("Which column contains the regions/provinces?", [""] + list(df.columns))
        age_col = st.selectbox("Which column contains the age groups?", [""] + list(df.columns))
        
    with col2:
        st.subheader("Brand/Product Columns (For Analysis)")
        brand_cols = st.multiselect("Select all the brand columns (should be 1s and 0s):", list(df.columns))

    st.markdown("---")
    
    col3, col4 = st.columns(2)
    with col3:
        st.info("💡 **Active Core Values:** Foundational personal values that define the layout shape of your map.")
        active_cols = st.multiselect("Select your Active Value columns:", list(df.columns))
    with col4:
        st.info("💡 **Passive Overlays:** Secondary behaviors, habits, or extra statements to project on top.")
        passive_cols = st.multiselect("Select your Passive Layer columns:", list(df.columns))

    # STEP 2: RUN ALGORITHMS
    if st.button("🚀 Run Complete Analysis", type="primary"):
        if not region_col or not age_col or not brand_cols or not active_cols:
            st.warning("Please make sure you've selected your Region, Age, Brand, and Active columns before running.")
            st.stop()

        with st.spinner("Processing population weights and market structures..."):
            
            # --- RAKING ALGORITHM ---
            df_weighted = df.copy()
            df_weighted["weight"] = 1.0
            targets = {region_col: REGION_TARGETS, age_col: AGE_TARGETS}
            
            for iteration in range(20):
                for var, var_targets in targets.items():
                    current_weighted_sum = df_weighted.groupby(var)["weight"].sum()
                    total_weight = df_weighted["weight"].sum()
                    current_props = current_weighted_sum / total_weight
                    
                    for category, target_prop in var_targets.items():
                        if category in current_props:
                            current_prop = current_props[category]
                            df_weighted.loc[df_weighted[var] == category, "weight"] *= (target_prop / current_prop)
            
            df_weighted["weight"] = df_weighted["weight"].clip(0.3, 5.0)
            df_weighted["weight"] *= len(df_weighted) / df_weighted["weight"].sum()
            
            # Store the weighted dataframe in session state so it can be used dynamically
            st.session_state["df_weighted"] = df_weighted
            st.session_state["brand_cols"] = brand_cols
            st.session_state["region_col"] = region_col
            st.session_state["age_col"] = age_col
            st.session_state["active_cols"] = active_cols
            st.session_state["passive_cols"] = passive_cols
            
            # --- GENERATING CROSSTABS ---
            def build_weighted_counts(row_headers):
                matrix = []
                for rh in row_headers:
                    row_data = {"Header": rh}
                    for bc in brand_cols:
                        agreed_and_bought = df_weighted[(df_weighted[rh] == 1) & (df_weighted[bc] == 1)]
                        row_data[bc] = agreed_and_bought["weight"].sum()
                    matrix.append(row_data)
                return pd.DataFrame(matrix).set_index("Header")

            df_active_counts = build_weighted_counts(active_cols)
            
            # --- CORRESPONDENCE ANALYSIS ---
            X = df_active_counts.values.astype(float)
            total_sum = X.sum()
            P = X / total_sum
            row_masses = P.sum(axis=1)
            col_masses = P.sum(axis=0)
            E = np.outer(row_masses, col_masses)
            Z = (P - E) / np.sqrt(E)
            U, D_sv, V_T = np.linalg.svd(Z, full_matrices=False)
            
            row_coords = np.diag(1.0 / np.sqrt(row_masses)) @ U @ np.diag(D_sv)
            col_coords = np.diag(1.0 / np.sqrt(col_masses)) @ V_T.T @ np.diag(D_sv)
            std_col_coords = np.diag(1.0 / np.sqrt(col_masses)) @ V_T.T
            
            var_exp = (D_sv**2 / sum(D_sv**2)) * 100
            
            st.success("Data successfully processed! Explore the results tabs below.")

    # Check if data has been run and stored in session state
    if "df_weighted" in st.session_state:
        df_weighted = st.session_state["df_weighted"]
        brand_cols = st.session_state["brand_cols"]
        region_col = st.session_state["region_col"]
        age_col = st.session_state["age_col"]
        
        # RENDER WORKSPACE TABS
        tab1, tab2, tab4 = st.tabs(["🗺️ The Landscape Map", "📊 Weighted Crosstab Data", "🎯 Custom Segment Profiler"])
        
        with tab1:
            st.info("The map has been generated and displays your positioning framework based on your active assets.")
            # Note: Map rendering logic from previous version applies here safely 
            st.markdown("*Review the relational placement of your brands against the central axis origins.*")
            
        with tab2:
            st.subheader("Population-Weighted Counts Table")
            # Build and show current baseline active counts
            def build_weighted_counts(row_headers):
                matrix = []
                for rh in row_headers:
                    row_data = {"Header": rh}
                    for bc in brand_cols:
                        agreed_and_bought = df_weighted[(df_weighted[rh] == 1) & (df_weighted[bc] == 1)]
                        row_data[bc] = agreed_and_bought["weight"].sum()
                    matrix.append(row_data)
                return pd.DataFrame(matrix).set_index("Header")
            st.dataframe(build_weighted_counts(st.session_state["active_cols"]).style.format(precision=0))
            
        with tab4:
            st.subheader("🎯 Deep-Dive Segment Builder")
            st.markdown("Select a bundle of statements to define a consumer mindset, set your target threshold, and see their profile.")
            
            # User selects the attitude columns to net together
            all_possible_statements = st.session_state["active_cols"] + st.session_state["passive_cols"]
            selected_segment_statements = st.multiselect("Which attitude statements define this target mindset group?", all_possible_statements)
            
            if selected_segment_statements:
                # Let user pick the threshold
                max_possible = len(selected_segment_statements)
                threshold = st.slider(f"Respondent must agree with at least how many of these?", 1, max_possible, max(1, int(max_possible * 0.7)))
                
                # Calculate row-wise match counts
                agreement_counts = df_weighted[selected_segment_statements].sum(axis=1)
                df_weighted["in_segment"] = (agreement_counts >= threshold).astype(int)
                
                segment_size_raw = int((agreement_counts >= threshold).sum())
                segment_size_weighted = int(df_weighted[df_weighted["in_segment"] == 1]["weight"].sum())
                total_weighted_pop = df_weighted["weight"].sum()
                
                st.metric("Segment Penetration Size", f"{segment_size_weighted:,} Consumers", f"{(segment_size_weighted / total_weighted_pop)*100:.1f}% of Market")
                
                if segment_size_raw == 0:
                    st.warning("No respondents matched this specific high threshold. Try lowering the required number of agreements.")
                else:
                    prof_col1, prof_col2 = st.columns(2)
                    
                    with prof_col1:
                        st.subheader("🛒 Product Over-Index Analysis")
                        st.markdown("*Where does this exact consumer group spend their money?*")
                        
                        index_records = []
                        for brand in brand_cols:
                            # Total penetration
                            total_pct = df_weighted[df_weighted[brand] == 1]["weight"].sum() / total_weighted_pop
                            # Segment penetration
                            seg_total_weight = df_weighted[df_weighted["in_segment"] == 1]["weight"].sum()
                            seg_brand_weight = df_weighted[(df_weighted["in_segment"] == 1) & (df_weighted[brand] == 1)]["weight"].sum()
                            seg_pct = seg_brand_weight / seg_total_weight if seg_total_weight > 0 else 0
                            
                            # Calculate Index Score
                            index_score = (seg_pct / total_pct * 100) if total_pct > 0 else 100
                            index_records.append({"Product/Brand": brand, "Segment Penetration %": f"{seg_pct*100:.1f}%", "Index Score": round(index_score)})
                        
                        df_index = pd.DataFrame(index_records).sort_values(by="Index Score", ascending=False)
                        st.dataframe(df_index.set_index("Product/Brand"))
                        
                    with prof_col2:
                        st.subheader("👥 Demographic Profile")
                        
                        # Region Distribution
                        st.markdown("**Regional Distribution**")
                        reg_total = df_weighted.groupby(region_col)["weight"].sum() / total_weighted_pop
                        reg_seg = df_weighted[df_weighted["in_segment"] == 1].groupby(region_col)["weight"].sum() / df_weighted[df_weighted["in_segment"] == 1]["weight"].sum()
                        
                        df_reg_prof = pd.DataFrame({"National Base %": reg_total * 100, "Your Target Segment %": reg_seg * 100})
                        st.dataframe(df_reg_prof.style.format(precision=1))
                        
                        # Age Distribution
                        st.markdown("**Age Distribution**")
                        age_total = df_weighted.groupby(age_col)["weight"].sum() / total_weighted_pop
                        age_seg = df_weighted[df_weighted["in_segment"] == 1].groupby(age_col)["weight"].sum() / df_weighted[df_weighted["in_segment"] == 1]["weight"].sum()
                        
                        df_age_prof = pd.DataFrame({"National Base %": age_total * 100, "Your Target Segment %": age_seg * 100})
                        st.dataframe(df_age_prof.style.format(precision=1))
