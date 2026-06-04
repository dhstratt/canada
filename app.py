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
# THE MEGA-CODEBOOK DICTIONARIES (COMPLETE)
# =====================================================================
CATEGORIES = {"OJxBuyersQuota": "Orange Juice", "ADExBuyersQuota": "Lemonade & Ades", "OtherJuicexBuyersQuota": "Other Fruit Juices/Blends", "LightxBuyersQuota": "Zero/Light/Lower Sugar"}
P3M_CATS = {1: "Soda/Pop/Cola", 2: "Tea", 3: "Coffee", 4: "Kombucha", 5: "Juice/Lemonade", 6: "Milk", 7: "Flavored water/seltzer", 8: "Sports drinks", 9: "Energy drinks", 10: "Nectars"}
BRANDS = {1: "Simply", 2: "Minute Maid", 3: "Fruitopia", 4: "Five Alive", 5: "Honest Kids", 6: "Allen's", 7: "Compliments", 8: "Del Monte", 9: "Dole", 10: "Fruité", 11: "Great Value", 12: "Kiju", 13: "Kool-Aid", 14: "Natural One", 15: "Oasis", 16: "Ocean Spray", 17: "President's Choice", 18: "Rougemont", 19: "Rubicon Exotic", 20: "Sunny Delight", 21: "SunRype", 22: "Tradition", 23: "Tropicana", 24: "Irresistible", 25: "Western Family", 26: "None/Other"}
CHANNELS = {1: "Grocery store", 2: "Ethnic Grocery", 3: "Mass retailer", 4: "Club store", 5: "Convenience store", 6: "Drug store", 7: "Gas station", 8: "Coffee shop", 9: "Deli", 10: "Restaurant", 11: "Other"}
SIZES = {1: "Large carton", 2: "Single carton", 3: "Large plastic jug", 4: "Can", 5: "Single plastic bottle", 6: "Fountain cup", 7: "Other"}
WHY_CHOOSE = {1: "Price/Value", 2: "Coupon/Incentive", 3: "Brand Loyalty", 4: "Trial/New", 5: "HH Request", 6: "Availability", 7: "Health Benefit", 8: "Convenience", 9: "Other"}
WHO_DRINKS = {1: "Child <6", 2: "Child 6-12", 3: "Child 13-17", 4: "Other adult", 5: "Myself"}
OTHER_ADULT_AGES = {1: "18-24", 2: "25-34", 3: "35-49", 4: "50-64", 5: "65+"}
WHEN_HOW = {1: "With breakfast", 2: "Morning snack", 3: "Morning alone", 4: "With lunch", 5: "Afternoon snack", 6: "Afternoon alone", 7: "With dinner", 8: "Evening snack", 9: "Evening alone", 10: "Special occasion/treat", 11: "During/after exercise", 12: "Parties/social"}
FREQUENCY = {1: "Multiple times/day", 2: "Once a day", 3: "3-5 times/week", 4: "1-2 times/week", 5: "2-3 times/month", 6: "Rarely/infrequently"}
REASONS = {1: "Hydration & Refreshment", 2: "Energy & Focus", 3: "Health & Wellness", 4: "Indulgence & Craving", 5: "Routine & Habit", 6: "Social & Relaxation", 7: "Family Needs"}
BRAND_ATTITUDES = {1: "Upset if went away", 2: "For someone like me", 3: "Fond memories", 4: "Brand I trust", 5: "Cares about people like me", 6: "Modern brand", 7: "Proud to purchase", 8: "Price feels fair", 9: "Tastes superior", 10: "Know exactly what to expect", 11: "Positive relationship", 12: "Always find it", 13: "Proudly Canadian", 14: "None of these"}
KIDS_ATTITUDES = {1: "Healthy option for children", 2: "Feel guilty giving to children", 3: "Kids handle sugar better", 4: "Sugar is inescapable for kids", 5: "Give kids what they want", 6: "Gets kids to consume fruits/veg", 7: "Provides necessary vitamins"}
BEV_ATTITUDES_1 = {1: "Pay premium for quality", 2: "Simple ingredients", 3: "Cool packaging", 4: "Highly convenient", 5: "Daily routine", 6: "Always next to me", 7: "Sweet drink over sweet food", 8: "Smaller portion of real juice"}
BEV_ATTITUDES_2 = {1: "Bold/tart kick", 2: "Functional health benefits", 3: "Change depending on season", 4: "Don't worry about sugar", 5: "Strictly avoid added sugars", 6: "Less worried if health benefits", 7: "Actively limit due to sugar", 8: "Only zero-sugar"}

MRI_VALUES = {1: "Wealth", 2: "Adventure", 3: "Ambition", 4: "Thrift", 5: "Social responsibility", 6: "Excitement", 7: "Simplicity", 8: "Curiosity", 9: "Creativity", 10: "Enjoying life", 11: "Working hard", 12: "Duty"}
LOYALTY_APPROACH = {1: "Loyal to one brand", 2: "Choose between familiar brands", 3: "Always exploring new brands", 4: "Choose least expensive", 5: "None of the above"}
PURCHASE_DRIVERS = {1: "Taste", 2: "Added nutritional benefits", 3: "Brand", 4: "Low sugar content", 5: "No sugar added", 6: "Total Price", 7: "Price per mL/ounce", 8: "Added functional benefits", 9: "Largest-size container", 10: "Smallest-size container", 11: "Medium-size container", 12: "Easy to pour", 13: "Low calorie content", 14: "Level of pulp / Flavor", 15: "Fun packaging / Natural ingredients", 16: "No high sugar warning", 17: "Not from Concentrate", 18: "Other"}
RECENT_PURCHASE = {1: "Within last week", 2: "1-2 weeks ago", 3: "2-4 weeks ago", 4: "1-2 months ago", 5: "More than 2 months ago"}
CONSUMPTION_CHANGE = {1: "Drinking more than a year ago", 2: "Drinking less (changed this year)", 3: "Drinking less (gradual change)", 4: "Stayed about the same"}

PSYCHOGRAPHICS = {
    "Q19_r1": "I thrive at big parties and social occasions", "Q19_r2": "I think of myself as an intellectual", "Q19_r3": "Spending time with my family is my top priority", "Q19_r4": "I am interested in finding out how I can help the environment", "Q19_r5": "I am an optimist", "Q19_r6": "I seek out variety in my everyday life", "Q19_r7": "I make sure I take time for myself each day", "Q19_r8": "I like to learn about foreign cultures", "Q19_r9": "I’m perfectly happy with my standard of living", "Q20_r1": "I like to change brands often for the sake of variety and novelty", "Q20_r2": "I buy based on quality, not price", "Q20_r3": "Price is more important to me than brand names", "Q20_r4": "Generic or store brand products are as effective as brand-name products", "Q20_r5": "I enjoy wandering the store looking for new, interesting products", "Q20_r6": "I tend to make impulse purchases", "Q20_r7": "My children have significant impact on the brands I choose", "Q20_r8": "I buy brands that reflect my style", "Q20_r9": "I am influenced by what's hot and what's not", "Q21_r1": "I prefer foods cooked with bold flavors", "Q21_r2": "Nutritional value is the most important factor when I'm choosing which foods to eat", "Q21_r3": "I eat the foods I like regardless of calories", "Q21_r4": "I believe in a healthy lifestyle instead of traditional dieting", "Q21_r5": "Food is a comfort to me", "Q21_r6": "I indulge my cravings for foods I enjoy", "Q21_r7": "I am loyal to my food brands and stick with them", "Q21_r8": "Fast food is junk food", "Q21_r9": "I prefer to eat foods without artificial ingredients", "Q21_r10": "I try to eat a healthy breakfast every day", "Q22_r1": "I am generally more fit and active than other people my age", "Q22_r2": "I frequently look for new ways to change up my exercise routine", "Q22_r3": "I regularly look for ways to get a better night’s sleep", "Q22_r4": "Because of my busy lifestyle, I don’t take care of myself as well as I should", "Q22_r5": "The health claims/benefits on a product package often influence my decision to buy it", "Q22_r6": "Taking care of your mental health is a critical part of your overall wellness", "Q22_r7": "I always do what my doctor tells me to do", "Q22_r8": "I consider my diet to be very healthy"
}

ETHNICITIES = {1: "Asian", 2: "Arab", 3: "Black", 4: "Caucasian/White", 5: "Latin American", 6: "Jewish", 7: "Indigenous Peoples", 8: "Other", 9: "Do not wish to reply"}

DEMO_MAP = {
    "S2": {2: "Province: BC", 3: "Province: Manitoba", 4: "Province: New Brunswick", 9: "Province: Ontario", 11: "Province: Quebec"},
    "S3": {2: "Age: 18-24", 3: "Age: 25-34", 4: "Age: 35-44", 5: "Age: 45-54", 6: "Age: 55-65"},
    "S4": {1: "Kids in HH: Yes", 2: "Kids in HH: No"},
    "D1": {1: "Gender: Female", 2: "Gender: Male", 3: "Gender: Non-Binary"},
    "D3": {1: "Marital: Single", 2: "Marital: Married", 3: "Marital: Living with Partner", 4: "Marital: Divorced", 5: "Marital: Separated", 6: "Marital: Widowed"},
    "D5": {1: "Income: <$25k", 2: "Income: $25k-$50k", 3: "Income: $50k-$75k", 4: "Income: $75k-$100k", 5: "Income: $100k-$150k", 6: "Income: $150k-$200k", 7: "Income: $200k+"},
    "D7": {1: "Asian Background: Chinese", 2: "Asian Background: Filipino", 3: "Asian Background: Japanese", 4: "Asian Background: Korean", 5: "Asian Background: South Asian", 6: "Asian Background: Southeast Asian", 7: "Asian Background: Other"},
    "D8": {1: "Immigration: 1st Gen", 2: "Immigration: 1.5 Gen", 3: "Immigration: 2nd Gen", 4: "Immigration: 3rd Gen"},
    "D9": {1: "Immigration Length: 0-5 years", 2: "Immigration Length: 6-10 years", 3: "Immigration Length: 11-20 years", 4: "Immigration Length: 21+ years"},
    "D10": {1: "Edu: Bachelor's", 2: "Edu: High School", 3: "Edu: College Diploma", 4: "Edu: Master's", 8: "Edu: Doctorate"},
    "D11": {1: "Employ: Full Time", 2: "Employ: Part Time", 4: "Employ: Student", 5: "Employ: Homemaker", 7: "Employ: Retired"}
}

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
                
    # 1B. Ethnicities (D6 is a Multi-Select)
    for e_idx, e_name in ETHNICITIES.items():
        if f"D6_{e_idx}" in df.columns:
            df_clean[f"[Demo] Ethnicity: {e_name}"] = pd.to_numeric(df[f"D6_{e_idx}"], errors='coerce').fillna(0).astype(int)
                
    # 1C. Household Size (D2) and Children Ages (D4)
    if 'D2' in df.columns:
        df['D2'] = pd.to_numeric(df['D2'], errors='coerce').fillna(0)
        df_clean["[Demo] HH Size: 1 Person"] = (df['D2'] == 1).astype(int)
        df_clean["[Demo] HH Size: 2 People"] = (df['D2'] == 2).astype(int)
        df_clean["[Demo] HH Size: 3-4 People"] = ((df['D2'] >= 3) & (df['D2'] <= 4)).astype(int)
        df_clean["[Demo] HH Size: 5+ People"] = (df['D2'] >= 5).astype(int)

    d4_cols = [c for c in df.columns if c.startswith('D4_')]
    if d4_cols:
        has_u6 = pd.Series(False, index=df.index)
        has_6_12 = pd.Series(False, index=df.index)
        has_13_17 = pd.Series(False, index=df.index)
        for c in d4_cols:
            age_s = pd.to_numeric(df[c], errors='coerce')
            has_u6 = has_u6 | (age_s < 6)
            has_6_12 = has_6_12 | ((age_s >= 6) & (age_s <= 12))
            has_13_17 = has_13_17 | ((age_s >= 13) & (age_s <= 17))
        df_clean["[Demo] Has Child <6"] = has_u6.astype(int)
        df_clean["[Demo] Has Child 6-12"] = has_6_12.astype(int)
        df_clean["[Demo] Has Child 13-17"] = has_13_17.astype(int)

    # 2. Categories (Quotas & P3M)
    for q_code, label in CATEGORIES.items():
        if q_code in df.columns: df_clean[f"[Category] Buyer: {label}"] = pd.to_numeric(df[q_code], errors='coerce').fillna(0).astype(int)
    for c_idx, c_name in P3M_CATS.items():
        col = f"S6_r{c_idx}_c1" # c1 = Self
        if col in df.columns: df_clean[f"[Category] P3M Self: {c_name}"] = pd.to_numeric(df[col], errors='coerce').fillna(0).astype(int)

    # 3. Brands (Q1, Q4, Q5, Q7 Rejectors)
    for b_idx, b_name in BRANDS.items():
        if f"Q1_{b_idx}" in df.columns: df_clean[f"[Brand] Purchased: {b_name}"] = pd.to_numeric(df[f"Q1_{b_idx}"], errors='coerce').fillna(0).astype(int)
        if f"Q4_{b_idx}" in df.columns: df_clean[f"[Rejectors/Favs] HH Favorite: {b_name}"] = pd.to_numeric(df[f"Q4_{b_idx}"], errors='coerce').fillna(0).astype(int)
        if f"Q5_{b_idx}" in df.columns: df_clean[f"[Brand] Most Recent Purch: {b_name}"] = pd.to_numeric(df[f"Q5_{b_idx}"], errors='coerce').fillna(0).astype(int)
        if f"Q7_{b_idx}" in df.columns: df_clean[f"[Rejectors/Favs] Never Consider: {b_name}"] = pd.to_numeric(df[f"Q7_{b_idx}"], errors='coerce').fillna(0).astype(int)

    # 4. Brand Varieties (Q8)
    q8_cols = [c for c in df.columns if c.startswith('Q8_')]
    for col in q8_cols:
        parts = col.replace('Q8_', '').split('.')
        if len(parts) == 2 and parts[1].isdigit():
            b_idx = int(parts[1])
            b_name = BRANDS.get(b_idx, "Unknown")
            df_clean[f"[Brand] Variety code {parts[0]} - {b_name}"] = pd.to_numeric(df[col], errors='coerce').fillna(0).astype(int)

    # 5. Channels (Q2)
    for c_idx, c_name in CHANNELS.items():
        for b_idx, b_name in BRANDS.items():
            if f"Q2_r{c_idx}_c{b_idx}" in df.columns: df_clean[f"[Channel] {c_name} - {b_name}"] = pd.to_numeric(df[f"Q2_r{c_idx}_c{b_idx}"], errors='coerce').fillna(0).astype(int)

    # 6. Sizes (Q3)
    for s_idx, s_name in SIZES.items():
        for b_idx, b_name in BRANDS.items():
            if f"Q3_r{s_idx}_c{b_idx}" in df.columns: df_clean[f"[Size] {s_name} - {b_name}"] = pd.to_numeric(df[f"Q3_r{s_idx}_c{b_idx}"], errors='coerce').fillna(0).astype(int)

    # 7. Why Choose (Q6)
    for w_idx, w_name in WHY_CHOOSE.items():
        for b_idx, b_name in BRANDS.items():
            if f"Q6_{w_idx}.{b_idx}" in df.columns: df_clean[f"[Why Choose] {w_name} - {b_name}"] = pd.to_numeric(df[f"Q6_{w_idx}.{b_idx}"], errors='coerce').fillna(0).astype(int)

    # 8. Who/When/Freq/Reason (Q9, Q9a, Q9b, Q14)
    for w_idx, w_name in WHO_DRINKS.items():
        for b_idx, b_name in BRANDS.items():
            if f"Q9_r{w_idx}_c{b_idx}" in df.columns: df_clean[f"[Who Drinks] {w_name} - {b_name}"] = pd.to_numeric(df[f"Q9_r{w_idx}_c{b_idx}"], errors='coerce').fillna(0).astype(int)
    
    # 8B. Other Adult Ages (Q9aa)
    for a_idx, a_name in OTHER_ADULT_AGES.items():
        for b_idx, b_name in BRANDS.items():
            if f"Q9aa_{a_idx}.{b_idx}" in df.columns: df_clean[f"[Who Drinks] Other Adult ({a_name}) - {b_name}"] = pd.to_numeric(df[f"Q9aa_{a_idx}.{b_idx}"], errors='coerce').fillna(0).astype(int)

    for w_idx, w_name in WHEN_HOW.items():
        for b_idx, b_name in BRANDS.items():
            if f"Q9a_r{w_idx}_c{b_idx}" in df.columns: df_clean[f"[When/How] {w_name} - {b_name}"] = pd.to_numeric(df[f"Q9a_r{w_idx}_c{b_idx}"], errors='coerce').fillna(0).astype(int)
    for b_idx, b_name in BRANDS.items():
        if f"Q9b_c{b_idx}" in df.columns:
            df[f"Q9b_c{b_idx}"] = pd.to_numeric(df[f"Q9b_c{b_idx}"], errors='coerce')
            for f_idx, f_name in FREQUENCY.items(): df_clean[f"[Frequency] {f_name} - {b_name}"] = (df[f"Q9b_c{b_idx}"] == f_idx).astype(int)
        if f"Q14_c{b_idx}" in df.columns:
            df[f"Q14_c{b_idx}"] = pd.to_numeric(df[f"Q14_c{b_idx}"], errors='coerce')
            for r_idx, r_name in REASONS.items(): df_clean[f"[Reason] {r_name} - {b_name}"] = (df[f"Q14_c{b_idx}"] == r_idx).astype(int)

    # 9. Buying Styles (Q5a, Q10-Q12, Q15)
    for r_idx, r_name in RECENT_PURCHASE.items():
        cols = [c for c in df.columns if c.startswith('Q5a')]
        if cols:
            df_clean[f"[Buying Styles] Recent Purch: {r_name}"] = (pd.to_numeric(df[cols[0]], errors='coerce') == r_idx).astype(int)
    if 'Q15' in df.columns:
        for r_idx, r_name in CONSUMPTION_CHANGE.items():
            df_clean[f"[Buying Styles] Consumption: {r_name}"] = (pd.to_numeric(df['Q15'], errors='coerce') == r_idx).astype(int)
            
    q_map = {'Q10': 'OJ', 'Q11': 'Lemonade', 'Q12': 'Other Juice'}
    for q_code, q_label in q_map.items():
        if q_code in df.columns:
            for l_idx, l_name in LOYALTY_APPROACH.items(): df_clean[f"[Buying Styles] Approach to {q_label}: {l_name}"] = (pd.to_numeric(df[q_code], errors='coerce') == l_idx).astype(int)
        for p_idx, p_name in PURCHASE_DRIVERS.items():
            if f"{q_code}a_{p_idx}" in df.columns: df_clean[f"[Buying Styles] Adult Driver ({q_label}): {p_name}"] = pd.to_numeric(df[f"{q_code}a_{p_idx}"], errors='coerce').fillna(0).astype(int)
            if f"{q_code}b_{p_idx}" in df.columns: df_clean[f"[Buying Styles] Kids Driver ({q_label}): {p_name}"] = pd.to_numeric(df[f"{q_code}b_{p_idx}"], errors='coerce').fillna(0).astype(int)

    # 10. Core MRI Values (Q18)
    for v_idx, v_name in MRI_VALUES.items():
        if f"Q18_{v_idx}" in df.columns: df_clean[f"[Psychographics] Core Value: {v_name}"] = pd.to_numeric(df[f"Q18_{v_idx}"], errors='coerce').fillna(0).astype(int)

    # 11. Scales & Attitudes (Q13, Q16, Q17, Q19-Q22)
    for r_idx, r_name in KIDS_ATTITUDES.items():
        if f"Q13_r{r_idx}" in df.columns: df_clean[f"[Kids Attitudes] {r_name}"] = pd.to_numeric(df[f"Q13_r{r_idx}"], errors='coerce').fillna(0)
    for idx, name in BEV_ATTITUDES_1.items():
        if f"Q16_{idx}" in df.columns: df_clean[f"[Bev Attitudes] {name}"] = pd.to_numeric(df[f"Q16_{idx}"], errors='coerce').fillna(0).astype(int)
    for idx, name in BEV_ATTITUDES_2.items():
        if f"Q16x2_{idx}" in df.columns: df_clean[f"[Bev Attitudes] {name}"] = pd.to_numeric(df[f"Q16x2_{idx}"], errors='coerce').fillna(0).astype(int)
    for r_idx, r_name in BRAND_ATTITUDES.items():
        for b_idx, b_name in BRANDS.items():
            if f"Q17_r{r_idx}_c{b_idx}" in df.columns: df_clean[f"[Brand Attitude] {r_name} - {b_name}"] = pd.to_numeric(df[f"Q17_r{r_idx}_c{b_idx}"], errors='coerce').fillna(0).astype(int)
    for q_code, english_stmt in PSYCHOGRAPHICS.items():
        if q_code in df.columns: df_clean[f"[Psychographics] {english_stmt}"] = pd.to_numeric(df[q_code], errors='coerce').fillna(0)

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
                if not any('Ethnicity: Caucasian' in c for c in st.session_state['df_working'].columns):
                    is_legacy_state = True
            
            if 'data_loaded' not in st.session_state or st.session_state.get('file_name') != uploaded_file.name or is_legacy_state:
                st.session_state['df_working'] = df_base.copy()
                st.session_state['created_segments'] = []
                st.session_state['data_loaded'] = True
                st.session_state['file_name'] = uploaded_file.name
            st.sidebar.success(f"Loaded Master File: {len(df_base)} Respondents!")
    
    all_cols = [c for c in st.session_state['df_working'].columns if c != "Weight" and c not in st.session_state['created_segments']]
    
    # UI Categories
    CAT_DEMOS = [c for c in all_cols if c.startswith("[Demo]")]
    CAT_CATEGORIES = [c for c in all_cols if c.startswith("[Category]")]
    CAT_BRANDS = [c for c in all_cols if c.startswith("[Brand]") or c.startswith("[Size]")]
    CAT_BUYING = [c for c in all_cols if c.startswith("[Buying Styles]")]
    CAT_FAVS = [c for c in all_cols if c.startswith("[Rejectors/Favs]")]
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
    st.sidebar.download_button("💾 Download Workspace (.pkl)", data=pickle.dumps(workspace_export), file_name="my_segment_workspace.pkl", mime="application/octet-stream")
    
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
        
        search_query_t1 = st.text_input("🔍 Search to quickly find a variable for your segment (e.g., 'White', 'Simply'):", key="t1_search")
        if search_query_t1:
            matched_vars_t1 = [c for c in all_cols if search_query_t1.lower() in c.lower()]
            if matched_vars_t1: st.info(f"Matches found: {', '.join(matched_vars_t1[:5])}...")
            else: st.warning("No matches found.")
        
        col_pool, col_mand = st.columns(2)
        with col_pool:
            st.markdown("### A. Threshold Statement Pool")
            st.markdown("Select the core attitudes and behaviors that make up this mindset. Respondents must meet a minimum count of these.")
            pool_psycho = st.multiselect("🧠 Select Attitudes & Psychographics:", options=CAT_ATTITUDES)
            pool_other = st.multiselect("🛒 Select Brands, Demos, or Behaviors:", options=[c for c in all_cols if c not in CAT_ATTITUDES])
            threshold_statements = pool_psycho + pool_other
            
        with col_mand:
            st.markdown("### B. Mandatory 'AND' Rules")
            st.markdown("Select strict rules that the respondent MUST meet (e.g., Must be Female, Must drink Minute Maid).")
            mand_psycho = st.multiselect("🧠 Mandatory Attitudes:", options=[c for c in CAT_ATTITUDES if c not in threshold_statements])
            mand_other = st.multiselect("🛒 Mandatory Brands/Demos/Behaviors:", options=[c for c in all_cols if c not in CAT_ATTITUDES and c not in threshold_statements])
            mandatory_statements = mand_psycho + mand_other
        
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
                    is_scale = (("[Psychographics]" in stmt) and ("Core Value" not in stmt)) or ("[Kids Attitudes]" in stmt)
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
        
        st.markdown("### 🔍 Global Search")
        search_query = st.text_input("Type a keyword to instantly find any variable (e.g., 'Orange Juice', 'Walmart', 'Optimist'):", key="ct_search")
        
        row_search_res = []
        col_search_res = []
        if search_query:
            matched_vars = [c for c in all_cols + st.session_state['created_segments'] if search_query.lower() in c.lower()]
            if matched_vars:
                st.success(f"Found {len(matched_vars)} matching variables for '{search_query}'")
                s_col1, s_col2 = st.columns(2)
                with s_col1: row_search_res = st.multiselect("➕ Add matches to Rows:", matched_vars, key="r_search")
                with s_col2: col_search_res = st.multiselect("➕ Add matches to Columns:", matched_vars, key="c_search")
            else:
                st.warning("No variables found matching your search.")

        st.markdown("---")
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
                            is_scale = (("[Psychographics]" in v) and ("Core Value" not in v)) or ("[Kids Attitudes]" in v)
                            v_mask = st.session_state['df_working'][v].isin([1, 2]) if is_scale else st.session_state['df_working'][v] == 1
                            if "AND" in qc_logic: qc_mask = qc_mask & v_mask
                            else: qc_mask = qc_mask | v_mask
                                
                        st.session_state['df_working'][qc_name] = qc_mask.astype(int)
                        st.session_state['created_segments'].append(qc_name)
                        st.success(f"✅ {qc_name} added to Saved Segments!")
                        st.rerun()

        st.markdown("---")
        st.markdown("### 📂 Or Select From Categories")
        st.markdown("##### ➡️ Select Rows")
        r_col1, r_col2, r_col3, r_col4 = st.columns(4)
        with r_col1: row_demos = st.multiselect("Demographics", CAT_DEMOS, key="r_demo")
        with r_col2: row_cats = st.multiselect("Beverage Categories", CAT_CATEGORIES, key="r_cats")
        with r_col3: row_brands = st.multiselect("Brands & Products", CAT_BRANDS, key="r_brand")
        with r_col4: row_psycho = st.multiselect("Attitudes", CAT_ATTITUDES, key="r_psycho")
        
        with st.expander("➕ View More Row Categories", expanded=False):
            ex_r1, ex_r2, ex_r3, ex_r4 = st.columns(4)
            with ex_r1: row_buy = st.multiselect("Buying Styles", CAT_BUYING, key="r_buy")
            with ex_r2: row_favs = st.multiselect("Rejectors & Favs", CAT_FAVS, key="r_favs")
            with ex_r3: row_chan = st.multiselect("Channels & Occasions", CAT_CHANNELS, key="r_chan")
            with ex_r4: row_reas = st.multiselect("Drivers & Perceptions", CAT_REASONS + CAT_PERCEPTIONS, key="r_reas")
            
        raw_ct_rows = row_demos + row_cats + row_brands + row_psycho + row_buy + row_favs + row_chan + row_reas + st.session_state['created_segments'] + row_search_res
        ct_rows = list(dict.fromkeys([x for x in raw_ct_rows if x]))
        
        st.markdown("---")
        st.markdown("##### ⬇️ Select Columns")
        c_col1, c_col2, c_col3, c_col4 = st.columns(4)
        with c_col1: col_demos = st.multiselect("Demographics ", CAT_DEMOS, key="c_demo")
        with c_col2: col_cats = st.multiselect("Beverage Categories ", CAT_CATEGORIES, key="c_cats")
        with c_col3: col_brands = st.multiselect("Brands & Products ", CAT_BRANDS, key="c_brand")
        with c_col4: col_psycho = st.multiselect("Attitudes ", CAT_ATTITUDES, key="c_psycho")
        
        with st.expander("➕ View More Column Categories", expanded=False):
            ex_c1, ex_c2, ex_c3, ex_c4 = st.columns(4)
            with ex_c1: col_buy = st.multiselect("Buying Styles ", CAT_BUYING, key="c_buy")
            with ex_c2: col_favs = st.multiselect("Rejectors & Favs ", CAT_FAVS, key="c_favs")
            with ex_c3: col_chan = st.multiselect("Channels & Occasions ", CAT_CHANNELS, key="c_chan")
            with ex_c4: col_reas = st.multiselect("Drivers & Perceptions ", CAT_REASONS + CAT_PERCEPTIONS, key="c_reas")

        raw_ct_cols = col_demos + col_cats + col_brands + col_psycho + col_buy + col_favs + col_chan + col_reas + st.session_state['created_segments'] + col_search_res
        ct_cols = list(dict.fromkeys([x for x in raw_ct_cols if x]))
        
        if ct_rows and ct_cols:
            scale_vars_in_ct = [v for v in set(ct_rows + ct_cols) if (("[Psychographics]" in v) and ("Core Value" not in v)) or ("[Kids Attitudes]" in v)]
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
                is_scale = (("[Psychographics]" in c) and ("Core Value" not in c)) or ("[Kids Attitudes]" in c)
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
                is_scale = (("[Psychographics]" in r) and ("Core Value" not in r)) or ("[Kids Attitudes]" in r)
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
        
        if map_rows and map_cols:
            scale_vars_map = [v for v in set(map_rows + map_cols) if (("[Psychographics]" in v) and ("Core Value" not in v)) or ("[Kids Attitudes]" in v)]
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
                is_scale_r = (("[Psychographics]" in r) and ("Core Value" not in r)) or ("[Kids Attitudes]" in r)
                if is_scale_r:
                    logic = map_logic_dict.get(r, "Any Agree (1 or 2 combined)")
                    r_mask = get_scale_mask(st.session_state['df_working'], r, logic)
                else: 
                    r_mask = st.session_state['df_working'][r] == 1
                    
                for c in map_cols:
                    is_scale_c = (("[Psychographics]" in c) and ("Core Value" not in c)) or ("[Kids Attitudes]" in c)
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
