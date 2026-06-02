import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import re

# Set page layout to wide for better visualization room
st.set_page_config(page_title="Coke Canada Market Mapper", layout="wide")

st.title("🥤 Coca-Cola Canada Market Mapper")
st.markdown("Upload raw survey microdata to instantly weight it to Statistics Canada population targets and view your competitive landscape.")

# =====================================================================
# SIDEBAR: FILE UPLOAD & PRESETS
# =====================================================================
st.sidebar.header("1. Upload Data")
uploaded_file = st.sidebar.file_uploader("Upload Raw Respondent Data (.csv or .xlsx)", type=["csv", "xlsx"])

# Pre-coded Statistics Canada Population Targets (2026 Estimates)
STATCAN_REGIONS = {"Ontario": 0.385, "Quebec": 0.223, "British Columbia": 0.135, "Alberta": 0.117, "Prairies": 0.075, "Atlantic": 0.065}
STATCAN_AGE = {"18-34": 0.270, "35-54": 0.330, "55+": 0.400}

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
    st.header("Step 1: Tell the App Where Your Data Is")
    
    col1, col2 = st.columns(2)
    with col1:
        st.subheader("Demographic Columns (For Weighting)")
        region_col = st.selectbox("Which column contains the regions/provinces?", [""] + list(df.columns))
        age_col = st.selectbox("Which column contains the age groups?", [""] + list(df.columns))
        
    with col2:
        st.subheader("Brand Columns (For the Cross-Tab)")
        brand_cols = st.multiselect("Select all the brand columns (should be 1s and 0s):", list(df.columns))

    st.markdown("---")
    
    col3, col4 = st.columns(2)
    with col3:
        st.info("💡 **Active Core Values:** These are the foundational personal values (like family priority or thriftiness) that will define the shape of your map.")
        active_cols = st.multiselect("Select your Active Value columns:", list(df.columns))
    with col4:
        st.info("💡 **Passive Overlays:** These are things like shopping habits or sub-brand options. They layer on top without distorting the layout.")
        passive_cols = st.multiselect("Select your Passive Layer columns:", list(df.columns))

    # STEP 2: RUN ALGORITHMS
    if st.button("🚀 Run Analysis & Generate Map", type="primary"):
        if not region_col or not age_col or not brand_cols or not active_cols:
            st.warning("Please make sure you've selected your Region, Age, Brand, and Active columns before running.")
            st.stop()

        with st.spinner("Calculating population weights and mapping dimensions..."):
            
            # --- RAKING ALGORITHM ---
            df_weighted = df.copy()
            df_weighted["weight"] = 1.0
            targets = {region_col: STATCAN_REGIONS, age_col: STATCAN_AGE}
            
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
            
            # --- RENDERING OUTPUT RESULTS IN TABS ---
            st.success("Analysis Complete!")
            tab1, tab2, tab3 = st.tabs(["🗺️ The Landscape Map", "📊 Weighted Crosstab Data", "🧠 Plain English Strategy"])
            
            with tab1:
                st.subheader("Your Population-Weighted Competitive Space")
                fig, ax = plt.subplots(figsize=(12, 10))
                
                # Active Rows
                ax.scatter(row_coords[:, 0], row_coords[:, 1], color='steelblue', marker='o', s=60, label='Core Attitudes')
                for i, txt in enumerate(df_active_counts.index):
                    ax.annotate(txt[:25]+'...', (row_coords[i, 0], row_coords[i, 1] + 0.005), color='darkblue', fontsize=9, ha='center')
                    
                # Passive Rows Projection
                if passive_cols:
                    df_passive_counts = build_weighted_counts(passive_cols)
                    Y_pass = df_passive_counts.values.astype(float)
                    R_sup_centered = (Y_pass / Y_pass.sum(axis=1, keepdims=True)) - col_masses
                    sup_coords = R_sup_centered @ std_col_coords
                    
                    ax.scatter(sup_coords[:, 0], sup_coords[:, 1], color='forestgreen', marker='^', s=80, label='Passive Overlays')
                    for i, txt in enumerate(df_passive_counts.index):
                        ax.annotate(txt[:25]+'...', (sup_coords[i, 0], sup_coords[i, 1] - 0.012), color='darkgreen', fontsize=9, ha='center')
                
                # Brand Columns
                ax.scatter(col_coords[:, 0], col_coords[:, 1], color='crimson', marker='s', s=90, label='Brands')
                for i, txt in enumerate(brand_cols):
                    ax.annotate(txt, (col_coords[i, 0], col_coords[i, 1] - 0.012), color='darkred', fontsize=11, weight='bold', ha='center')
                
                # Symmetrical boundaries
                all_x = np.concatenate([row_coords[:, 0], col_coords[:, 0]])
                all_y = np.concatenate([row_coords[:, 1], col_coords[:, 1]])
                max_val = max(np.abs(all_x).max(), np.abs(all_y).max()) * 1.2
                ax.set_xlim(-max_val, max_val)
                ax.set_ylim(-max_val, max_val)
                
                ax.axhline(0, color='black', linestyle='-', linewidth=1)
                ax.axvline(0, color='black', linestyle='-', linewidth=1)
                ax.set_xlabel(f"Dimension 1 ({var_exp[0]:.1f}% Variance Explained)")
                ax.set_ylabel(f"Dimension 2 ({var_exp[1]:.1f}% Variance Explained)")
                ax.legend(loc="upper right")
                ax.grid(alpha=0.3, linestyle='--')
                
                st.pyplot(fig)
                
            with tab2:
                st.subheader("Population-Weighted Counts Table")
                st.dataframe(df_active_counts.style.format(precision=0))
                csv_data = df_active_counts.to_csv().encode('utf-8')
                st.download_button("📥 Download Weighted Counts as CSV", data=csv_data, file_name="weighted_counts_crosstab.csv", mime="text/csv")
                
            with tab3:
                st.subheader("How to Interpret Your Results")
                st.markdown("""
                *   **Look for Clustered Items:** Brands sitting very close to specific attitudes are over-indexing among those consumers. That is your brand's unique mental ownership space.
                *   **The Dead Center (0,0):** Items near the absolute intersection of the crosshairs represent the national mainstream average. Brands placed here appeal to everyone generally, but don't hold a distinct identity advantage over one another.
                *   **The Outliers:** Elements pushed far out toward the edges are your niche opportunities or specialized market segments.
                """)
else:
    st.info("◀️ Please upload your raw survey respondent dataset file in the sidebar to begin.")
