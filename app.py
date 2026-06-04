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
st.markdown("Upload your raw survey data. **Use the dropdown boxes to search by Question Number (e.g., type 'Q19' or 'D5')** to instantly find what you need.")

# =====================================================================
# THE MEGA-CODEBOOK DICTIONARIES (COMPLETE & ACCURATE TO SPEC)
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
CONSUMPTION_CHANGE = {1: "Drinking more than a year ago", 2: "Drinking less (changed this year)", 3: "Drinking less (gradual change)", 4: "Stayed about the same"}

# Fully split and integrated parameters matching the survey blueprint
RECENT_PURCHASE = {1: "Within last week", 2: "1-2 weeks ago", 3: "2-4 weeks ago", 4: "1-2 months ago", 5: "More than 2 months ago"}
ADULT_PURCHASE_DRIVERS = {1: "Taste", 2: "Added nutritional benefits", 3: "Brand", 4: "Low sugar content", 5: "No sugar added", 6: "Total Price", 7: "Price per mL/ounce", 8: "Added functional benefits", 9: "Largest-size container", 10: "Smallest-size container", 11: "Medium-size container", 12: "Easy to pour", 13: "Low calorie content", 14: "Level of pulp / Flavor", 15: "Natural ingredients", 16: "No high sugar warning", 17: "Not from Concentrate", 18: "Other"}
KIDS_PURCHASE_DRIVERS = {1: "Taste", 2: "Added nutritional benefits", 3: "Brand", 4: "Low sugar content", 5: "No sugar added", 6: "Total Price", 7: "Price per mL/ounce", 8: "Added functional benefits", 9: "Largest-size container", 10: "Smallest-size container", 11: "Medium-size container", 12: "Easy to pour", 13: "Low calorie content", 14: "Flavor", 15: "Has fun packaging", 16: "Does not have characters", 17: "No high sugar warning", 18: "Not from Concentrate", 19: "Natural ingredients", 20: "Other"}
LAST_TIME_INFLUENCE = {1: "Child asked for it", 2: "Healthy / nutritious option", 3: "Indulgent choice / treat", 4: "Other (Q10d only)", 5: "Haven't purchased for child in 3M"}

PSYCHOGRAPHICS = {
    "Q19_r1": "I thrive at big parties and social occasions", "Q19_r2": "I think of myself as an intellectual", "Q19_r3": "Spending time with my family is my top priority", "Q19_r4": "I am interested in finding out how I can help the environment", "Q19_r5": "I am an optimist", "Q19_r6": "I seek out variety in my everyday life", "Q19_r7": "I make sure I take time for myself each day", "Q19_r8": "I like to learn about foreign cultures", "Q19_r9": "I’m perfectly happy with my standard of living", "Q20_r1": "I like to change brands often for the sake of variety and novelty", "Q20_r2": "I buy based on quality, not price", "Q20_r3": "Price is more important to me than brand names", "Q20_r4": "Generic or store brand products are as effective as brand-name products", "Q20_r5": "I enjoy wandering the store looking for new, interesting products", "Q20_r6": "I tend to make impulse purchases", "Q20_r7": "My children have significant impact on the brands I choose", "Q20_r8": "I buy brands that reflect my style", "Q20_r9": "I am influenced by what's hot and what's not", "Q21_r1": "I prefer foods cooked with bold flavors", "Q21_r2": "Nutritional value is the most important factor when I'm choosing which foods to eat", "Q21_r3": "I eat the foods I like regardless of calories", "Q21_r4": "I believe in a healthy lifestyle instead of traditional dieting", "Q21_r5": "Food is a comfort to me", "Q21_r6": "I indulge my cravings for foods I enjoy", "Q21_r7": "I am loyal to my food brands and stick with them", "Q21_r8": "Fast food is junk food", "Q21_r9": "I prefer to eat foods without artificial ingredients", "Q21_r10": "I try to eat a healthy breakfast every day", "Q22_r1": "I am generally more fit and active than other people my age", "Q22_r2": "I frequently look for new ways to change up my exercise routine", "Q22_r3": "I regularly look for ways to get a better night’s sleep", "Q22_r4": "Because of my busy lifestyle, I don’t take care of myself as well as I should", "Q22_r5": "The health claims/benefits on a product package often influence my decision to buy it", "Q22_r6": "Taking care of your mental health is a critical part of your overall wellness", "Q22_r7": "I always do what my doctor tells me to do", "Q22_r8": "I consider my diet to be very healthy"
}

ETHNICITIES = {1: "Asian", 2: "Arab", 3: "Black", 4: "Caucasian/White", 5: "Latin American", 6: "Jewish", 7: "Indigenous Peoples", 8: "Other", 9: "Do not wish to reply"}

DEMO_MAP = {
    "S1": {1: "Language: French", 2: "Language: English"},
    "S2": {1: "Province: AB", 2: "Province: BC", 3: "Province: MB", 4: "Province: NB", 5: "Province: NL", 7: "Province: NS", 8: "Province: NU", 9: "Province: ON", 10: "Province: PEI", 11: "Province: QC", 12: "Province: SK", 13: "Province: YT"},
    "S3": {2: "Age: 18-24", 3: "Age: 25-34", 4: "Age: 35-44", 5: "Age: 45-54", 6: "Age: 55-65"},
    "S4": {1: "Kids in HH: Yes", 2: "Kids in HH: No"},
    "D1": {1: "Gender: Female", 2: "Gender: Male", 3: "Gender: Non-Binary"},
    "D3": {1: "Marital: Single", 2: "Marital: Married", 3: "Marital: Living with Partner", 4: "Marital: Divorced", 5: "Marital: Separated", 6: "Marital: Widowed"},
    "D5": {1: "Income: <$25k", 2: "Income: $25k-$50k", 3: "Income: $50k-$75k", 4: "Income: $75k-$100k", 5: "Income: $100k-$150k", 6: "Income: $150k-$200k", 7: "Income: $200k+"},
    "D7": {1: "Asian Background: Chinese", 2: "Asian Background: Filipino", 3: "Asian Background: Japanese", 4: "Asian Background: Korean", 5: "Asian Background: South Asian", 6: "Asian Background: Southeast Asian", 7: "Asian Background: Other"},
    "D8": {1: "Immigration: 1st Gen", 2: "Immigration: 1.5 Gen", 3: "Immigration: 2nd Gen", 4: "Immigration: 3rd Gen"},
    "D9": {1: "Immigration Length: 0-5 years", 2: "Immigration Length: 6-10 years", 3: "Immigration Length: 11-20 years", 4: "Immigration Length: 21+ years"},
    "D10": {1: "Edu: Bachelor's", 2: "Edu: High School", 3: "Edu: College Diploma", 4: "Edu: Master's", 5: "Edu: Some College", 6: "Edu: Trade School", 7: "Edu: No HS/Some School", 8: "Edu: Doctorate/Professional", 9: "Edu: Attended Trade School"},
    "D11": {1: "Employ: Full Time", 2: "Employ: Part Time", 3: "Employ: Seeking", 4: "Employ: Student", 5: "Employ: Homemaker", 6: "Employ: Not Seeking", 7: "Employ: Retired"}
}

# Auto-expanding loop algorithm mapping all 135 dynamic Q8 options cleanly
VARIETIES = {
    1: "Orange Juice", 2: "Lemonade/Limeades", 3: "Juice (NOT orange/lemonade)", 4: "Simply 50 Orange Juice",
    5: "Orange Juice", 6: "Lemonade/Limeades", 7: "Juice (NOT orange/lemonade)", 8: "Zero Sugar (fruit blends)", 9: "Zero Sugar (lemonades)",
    10: "Orange Juice", 11: "Lemonade", 12: "Fruit Drinks (NOT orange/lemonade)", 13: "Lower Sugar (orange juice)", 14: "Zero Sugar (fruit blends)", 15: "Zero sugar (lemonades)"
}
for i in range(16, 136):
    offset = (i - 16) % 6
    if offset == 0: VARIETIES[i] = "Orange Juice"
    elif offset == 1: VARIETIES[i] = "Lemonade/Limeades"
    elif offset == 2: VARIETIES[i] = "Fruit Juice/Drink (NOT orange/lemonade)"
    elif offset == 3: VARIETIES[i] = "Lower Sugar (orange juice)"
    elif offset == 4: VARIETIES[i] = "Zero Sugar (fruit blends)"
    elif offset == 5: VARIETIES[i] = "Zero Sugar (lemonades)"

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
    df_valid = pd.DataFrame()
    
    if 'Weight' in df.columns: 
        df_clean['Weight'] = df['Weight']
        df_valid['Weight'] = df['Weight']
    else: 
        df_clean['Weight'] = 1.0
        df_valid['Weight'] = 1.0

    def add_var(name, val_series, valid_mask):
        df_clean[name] = val_series
        df_valid[name] = valid_mask.astype(int)
        
    def get_block_valid_mask(cols):
        exist_cols = [c for c in cols if c in df.columns]
        if not exist_cols: return pd.Series(False, index=df.index)
        temp_df = df[exist_cols].replace(r'^\s*$', np.nan, regex=True)
        return temp_df.notna().any(axis=1)

    # Dynamic individual row variable structural mask processors
    for col, value_map in DEMO_MAP.items():
        if col in df.columns:
            valid_mask = get_block_valid_mask([col])
            s_num = pd.to_numeric(df[col], errors='coerce')
            for val, label in value_map.items(): add_var(f"[{col} Demo] {label}", (s_num == val).astype(int), valid_mask)
                
    eth_cols = [f"D6_{i}" for i in ETHNICITIES.keys() if f"D6_{i}" in df.columns]
    eth_mask = get_block_valid_mask(eth_cols) if eth_cols else pd.Series(True, index=df.index)
    for e_idx, e_name in ETHNICITIES.items():
        if f"D6_{e_idx}" in df.columns: add_var(f"[D6 Demo] Ethnicity: {e_name}", pd.to_numeric(df[f"D6_{e_idx}"], errors='coerce').fillna(0).astype(int), eth_mask)
                
    if 'D2' in df.columns:
        d2_mask = get_block_valid_mask(['D2'])
        d2 = pd.to_numeric(df['D2'], errors='coerce').fillna(0)
        add_var("[D2 Demo] HH Size: 1 Person", (d2 == 1).astype(int), d2_mask)
        add_var("[D2 Demo] HH Size: 2 People", (d2 == 2).astype(int), d2_mask)
        add_var("[D2 Demo] HH Size: 3-4 People", ((d2 >= 3) & (d2 <= 4)).astype(int), d2_mask)
        add_var("[D2 Demo] HH Size: 5+ People", (d2 >= 5).astype(int), d2_mask)

    d4_cols = [c for c in df.columns if c.startswith('D4_')]
    if d4_cols:
        d4_mask = get_block_valid_mask(d4_cols)
        has_u6 = pd.Series(False, index=df.index)
        has_6_12 = pd.Series(False, index=df.index)
        has_13_17 = pd.Series(False, index=df.index)
        for c in d4_cols:
            age_s = pd.to_numeric(df[c], errors='coerce')
            has_u6 = has_u6 | (age_s < 6)
            has_6_12 = has_6_12 | ((age_s >= 6) & (age_s <= 12))
            has_13_17 = has_13_17 | ((age_s >= 13) & (age_s <= 17))
        add_var("[D4 Demo] Has Child <6", has_u6.astype(int), d4_mask)
        add_var("[D4 Demo] Has Child 6-12", has_6_12.astype(int), d4_mask)
        add_var("[D4 Demo] Has Child 13-17", has_13_17.astype(int), d4_mask)

    for q_code, label in CATEGORIES.items():
        if q_code in df.columns: add_var(f"[Quota Category] Buyer: {label}", pd.to_numeric(df[q_code], errors='coerce').fillna(0).astype(int), get_block_valid_mask([q_code]))
    
    for c_idx, c_name in P3M_CATS.items():
        col = f"S6_r{c_idx}_c1" 
        if col in df.columns: add_var(f"[S6 Category] P3M Self: {c_name}", pd.to_numeric(df[col], errors='coerce').fillna(0).astype(int), get_block_valid_mask([col]))

    for b_idx, b_name in BRANDS.items():
        if f"Q1_{b_idx}" in df.columns: add_var(f"[Q1 Brand] Purchased: {b_name}", pd.to_numeric(df[f"Q1_{b_idx}"], errors='coerce').fillna(0).astype(int), get_block_valid_mask([f"Q1_{b_idx}"]))
        if f"Q4_{b_idx}" in df.columns: add_var(f"[Q4 Rejectors/Favs] HH Favorite: {b_name}", pd.to_numeric(df[f"Q4_{b_idx}"], errors='coerce').fillna(0).astype(int), get_block_valid_mask([f"Q4_{b_idx}"]))
        if f"Q5_{b_idx}" in df.columns: add_var(f"[Q5 Brand] Most Recent Purch: {b_name}", pd.to_numeric(df[f"Q5_{b_idx}"], errors='coerce').fillna(0).astype(int), get_block_valid_mask([f"Q5_{b_idx}"]))
        if f"Q7_{b_idx}" in df.columns: add_var(f"[Q7 Rejectors/Favs] Never Consider: {b_name}", pd.to_numeric(df[f"Q7_{b_idx}"], errors='coerce').fillna(0).astype(int), get_block_valid_mask([f"Q7_{b_idx}"]))

    for v_idx, v_name in MRI_VALUES.items():
        col = f"Q18_{v_idx}"
        if col in df.columns: add_var(f"[Q18 Psycho] Core Value: {v_name}", pd.to_numeric(df[col], errors='coerce').fillna(0).astype(int), get_block_valid_mask([col]))
        
    for r_idx, r_name in KIDS_ATTITUDES.items():
        col = f"Q13_r{r_idx}"
        if col in df.columns: add_var(f"[Q13 Kids Attitudes] {r_name}", pd.to_numeric(df[col], errors='coerce').fillna(0), get_block_valid_mask([col]))
        
    for idx, name in BEV_ATTITUDES_1.items():
        col = f"Q16_{idx}"
        if col in df.columns: add_var(f"[Q16 Bev Attitudes] {name}", pd.to_numeric(df[col], errors='coerce').fillna(0).astype(int), get_block_valid_mask([col]))
        
    for idx, name in BEV_ATTITUDES_2.items():
        col = f"Q16x2_{idx}"
        if col in df.columns: add_var(f"[Q16x2 Bev Attitudes] {name}", pd.to_numeric(df[col], errors='coerce').fillna(0).astype(int), get_block_valid_mask([col]))
        
    for r_idx, r_name in BRAND_ATTITUDES.items():
        for b_idx, b_name in BRANDS.items():
            col = f"Q17_r{r_idx}_c{b_idx}"
            if col in df.columns: add_var(f"[Q17 Brand Attitude] {r_name} - {b_name}", pd.to_numeric(df[col], errors='coerce').fillna(0).astype(int), get_block_valid_mask([col]))
            
    for q_code, english_stmt in PSYCHOGRAPHICS.items():
        if q_code in df.columns: add_var(f"[{q_code.split('_')[0]} Psycho] {english_stmt}", pd.to_numeric(df[q_code], errors='coerce').fillna(0), get_block_valid_mask([q_code]))

    q8_mask = get_block_valid_mask([c for c in df.columns if c.startswith('Q8_')])
    for col in [c for c in df.columns if c.startswith('Q8_')]:
        parts = col.replace('Q8_', '').split('.')
        if len(parts) == 2 and parts[1].isdigit():
            variety_code = int(parts[0])
            brand_code = int(parts[1])
            b_name = BRANDS.get(brand_code, "Unknown")
            v_name = VARIETIES.get(variety_code, f"Variety {variety_code}")
            add_var(f"[Q8 Sub-Brand] {b_name} - {v_name}", pd.to_numeric(df[col], errors='coerce').fillna(0).astype(int), q8_mask)

    brand_masks = {}
    for b_idx in BRANDS.keys():
        b_cols = [f"Q2_r{c}_c{b_idx}" for c in CHANNELS.keys()] + \
                 [f"Q3_r{s}_c{b_idx}" for s in SIZES.keys()] + \
                 [f"Q6_{w}.{b_idx}" for w in WHY_CHOOSE.keys()] + \
                 [f"Q9_r{w}_c{b_idx}" for w in WHO_DRINKS.keys()] + \
                 [f"Q9aa_{a}.{b_idx}" for a in OTHER_ADULT_AGES.keys()] + \
                 [f"Q9a_r{w}_c{b_idx}" for w in WHEN_HOW.keys()] + \
                 [f"Q9b_c{b_idx}", f"Q14_c{b_idx}"]
        brand_masks[b_idx] = get_block_valid_mask(b_cols)

    for c_idx, c_name in CHANNELS.items():
        for b_idx, b_name in BRANDS.items():
            if f"Q2_r{c_idx}_c{b_idx}" in df.columns: add_var(f"[Q2 Channel] {c_name} - {b_name}", pd.to_numeric(df[f"Q2_r{c_idx}_c{b_idx}"], errors='coerce').fillna(0).astype(int), brand_masks[b_idx])
    for s_idx, s_name in SIZES.items():
        for b_idx, b_name in BRANDS.items():
            if f"Q3_r{s_idx}_c{b_idx}" in df.columns: add_var(f"[Q3 Size] {s_name} - {b_name}", pd.to_numeric(df[f"Q3_r{s_idx}_c{b_idx}"], errors='coerce').fillna(0).astype(int), brand_masks[b_idx])
    for w_idx, w_name in WHY_CHOOSE.items():
        for b_idx, b_name in BRANDS.items():
            if f"Q6_{w_idx}.{b_idx}" in df.columns: add_var(f"[Q6 Why Choose] {w_name} - {b_name}", pd.to_numeric(df[f"Q6_{w_idx}.{b_idx}"], errors='coerce').fillna(0).astype(int), brand_masks[b_idx])
    for w_idx, w_name in WHO_DRINKS.items():
        for b_idx, b_name in BRANDS.items():
            if f"Q9_r{w_idx}_c{b_idx}" in df.columns: add_var(f"[Q9 Who Drinks] {w_name} - {b_name}", pd.to_numeric(df[f"Q9_r{w_idx}_c{b_idx}"], errors='coerce').fillna(0).astype(int), brand_masks[b_idx])
    for a_idx, a_name in OTHER_ADULT_AGES.items():
        for b_idx, b_name in BRANDS.items():
            if f"Q9aa_{a_idx}.{b_idx}" in df.columns: add_var(f"[Q9aa Who Drinks] Other Adult ({a_name}) - {b_name}", pd.to_numeric(df[f"Q9aa_{a_idx}.{b_idx}"], errors='coerce').fillna(0).astype(int), brand_masks[b_idx])
    for w_idx, w_name in WHEN_HOW.items():
        for b_idx, b_name in BRANDS.items():
            if f"Q9a_r{w_idx}_c{b_idx}" in df.columns: add_var(f"[Q9a When/How] {w_name} - {b_name}", pd.to_numeric(df[f"Q9a_r{w_idx}_c{b_idx}"], errors='coerce').fillna(0).astype(int), brand_masks[b_idx])
    for b_idx, b_name in BRANDS.items():
        if f"Q9b_c{b_idx}" in df.columns:
            s_num = pd.to_numeric(df[f"Q9b_c{b_idx}"], errors='coerce')
            for f_idx, f_name in FREQUENCY.items(): add_var(f"[Q9b Frequency] {f_name} - {b_name}", (s_num == f_idx).astype(int), brand_masks[b_idx])
        if f"Q14_c{b_idx}" in df.columns:
            s_num = pd.to_numeric(df[f"Q14_c{b_idx}"], errors='coerce')
            for r_idx, r_name in REASONS.items(): add_var(f"[Q14 Reason] {r_name} - {b_name}", (s_num == r_idx).astype(int), brand_masks[b_idx])

    q5a_mask = get_block_valid_mask([c for c in df.columns if c.startswith('Q5a')])
    if q5a_mask.any():
        cols = [c for c in df.columns if c.startswith('Q5a')]
        s_num = pd.to_numeric(df[cols[0]], errors='coerce')
        for r_idx, r_name in RECENT_PURCHASE.items(): add_var(f"[Q5a Buying Styles] Recent Purch: {r_name}", (s_num == r_idx).astype(int), q5a_mask)
            
    q15_mask = get_block_valid_mask(['Q15'])
    if 'Q15' in df.columns:
        s_num = pd.to_numeric(df['Q15'], errors='coerce')
        for r_idx, r_name in CONSUMPTION_CHANGE.items(): add_var(f"[Q15 Buying Styles] Consumption: {r_name}", (s_num == r_idx).astype(int), q15_mask)
            
    q_map = {'Q10': 'OJ', 'Q11': 'Lemonade', 'Q12': 'Other Juice'}
    for q_code, q_label in q_map.items():
        if q_code in df.columns:
            q_mask = get_block_valid_mask([q_code])
            s_num = pd.to_numeric(df[q_code], errors='coerce')
            for l_idx, l_name in LOYALTY_APPROACH.items(): add_var(f"[{q_code} Buying Styles] Approach to {q_label}: {l_name}", (s_num == l_idx).astype(int), q_mask)
        
        qa_cols = [c for c in df.columns if c.startswith(f"{q_code}a_")]
        qa_mask = get_block_valid_mask(qa_cols)
        for p_idx, p_name in ADULT_PURCHASE_DRIVERS.items():
            if f"{q_code}a_{p_idx}" in df.columns: add_var(f"[{q_code}a Buying Styles] Adult Driver ({q_label}): {p_name}", pd.to_numeric(df[f"{q_code}a_{p_idx}"], errors='coerce').fillna(0).astype(int), qa_mask)
        
        qb_cols = [c for c in df.columns if c.startswith(f"{q_code}b_")]
        qb_mask = get_block_valid_mask(qb_cols)
        for p_idx, p_name in KIDS_PURCHASE_DRIVERS.items():
            if f"{q_code}b_{p_idx}" in df.columns: add_var(f"[{q_code}b Buying Styles] Kids Driver ({q_label}): {p_name}", pd.to_numeric(df[f"{q_code}b_{p_idx}"], errors='coerce').fillna(0).astype(int), qb_mask)

        qc_col = f"{q_code}c"
        if qc_col in df.columns:
            qc_mask = get_block_valid_mask([qc_col])
            s_num = pd.to_numeric(df[qc_col], errors='coerce')
            for c_idx, c_name in LAST_TIME_INFLUENCE.items(): 
                if c_idx != 4: 
                    add_var(f"[{qc_col} Buying Styles] Last Time Influence ({q_label}): {c_name}", (s_num == c_idx).astype(int), qc_mask)

    if 'Q10d' in df.columns:
        qd_mask = get_block_valid_mask(['Q10d'])
        s_num = pd.to_numeric(df['Q10d'], errors='coerce')
        for d_idx, d_name in LAST_TIME_INFLUENCE.items(): 
            add_var(f"[Q10d Buying Styles] Last Time Value (OJ): {d_name}", (s_num == d_idx).astype(int), qd_mask)

    known_prefixes = ('S1', 'S2', 'S3', 'S4', 'S6', 'D1', 'D2', 'D3', 'D4', 'D5', 'D6', 'D7', 'D8', 'D9', 'D10', 'D11',
                      'Q1_', 'Q2_', 'Q3_', 'Q4_', 'Q5_', 'Q5a', 'Q6_', 'Q7_', 'Q8_', 'Q9_', 'Q9a_', 'Q9aa_', 'Q9b_', 
                      'Q10', 'Q11', 'Q12', 'Q13_', 'Q14_', 'Q15', 'Q16_', 'Q16x2', 'Q17_', 'Q18_', 'Q19_', 'Q20_', 
                      'Q21_', 'Q22_')
    ignore_substrings = ['Quota', 'EndQ', 'sys_', 'Data_', 'botCheck', 'captcha', 'IP_', 'Unnamed', 'CS', 'UniqueResp', 'ListPanel', 'OverallStartQ', 'PanelQ', 'S7', 'S5', 'Q7a', 'Q7Resp_', 'Q8Product', 'Q5Product', 'Q7Rejectors', 'Q8Buyers', 'Q18xMRIxCoding', 'StraightxLiners', 'P', 'L1']
    
    for c in df.columns:
        if c == 'Weight' or any(sub in c for sub in ignore_substrings) or any(c.startswith(p) for p in known_prefixes): continue
        unique_vals = df[c].dropna().unique()
        if len(unique_vals) > 1 and len(unique_vals) <= 15:
            valid_mask = get_block_valid_mask([c])
            for val in unique_vals:
                if str(val).strip() != '': add_var(f"[{c} Raw] Answer: {val}", (df[c] == val).astype(int), valid_mask)

    return df_clean, df_valid

# =====================================================================
# SIDEBAR: UPLOAD & WORKSPACE MANAGEMENT
# =====================================================================
st.sidebar.header("1. Upload Data or Workspace")
uploaded_file = st.sidebar.file_uploader("Upload Master File (.csv/.xlsx) or Workspace (.pkl)", type=["csv", "xlsx", "pkl"])

if uploaded_file:
    with st.spinner("Analyzing survey logic and building dynamic eligible base engine..."):
        if uploaded_file.name.endswith('.pkl'):
            if 'data_loaded' not in st.session_state or st.session_state.get('file_name') != uploaded_file.name:
                workspace = pickle.loads(uploaded_file.getvalue())
                st.session_state['df_working'] = workspace['df_working']
                
                if 'df_valid' not in workspace or workspace['df_valid'].empty:
                    st.session_state['df_valid'] = pd.DataFrame(1, index=workspace['df_working'].index, columns=workspace['df_working'].columns)
                else:
                    st.session_state['df_valid'] = workspace['df_valid']
                    
                st.session_state['created_segments'] = workspace['created_segments']
                st.session_state['data_loaded'] = True
                st.session_state['file_name'] = uploaded_file.name
            st.sidebar.success(f"Workspace Restored! Loaded {len(st.session_state['created_segments'])} Custom Segments.")
        else:
            df_base, df_valid_base = load_and_prep_data(uploaded_file)
            
            is_legacy_state = False
            if 'df_working' in st.session_state:
                if not any('[Q19 Psycho]' in c for c in st.session_state['df_working'].columns):
                    is_legacy_state = True
            
            if 'data_loaded' not in st.session_state or st.session_state.get('file_name') != uploaded_file.name or is_legacy_state:
                st.session_state['df_working'] = df_base.copy()
                st.session_state['df_valid'] = df_valid_base.copy()
                st.session_state['created_segments'] = []
                st.session_state['data_loaded'] = True
                st.session_state['file_name'] = uploaded_file.name
            st.sidebar.success(f"Loaded Master File: {len(df_base)} Respondents!")
    
    all_cols = [c for c in st.session_state['df_working'].columns if c != "Weight" and c not in st.session_state['created_segments']]
    all_vars_for_selection = all_cols + st.session_state['created_segments']
    
    CAT_DEMOS = [c for c in all_cols if "Demo]" in c]
    CAT_CATEGORIES = [c for c in all_cols if "Category]" in c]
    CAT_BRANDS = [c for c in all_cols if "Brand]" in c or "Size]" in c or "Sub-Brand]" in c]
    CAT_BUYING = [c for c in all_cols if "Buying Styles]" in c]
    CAT_FAVS = [c for c in all_cols if "Rejectors/Favs]" in c]
    CAT_CHANNELS = [c for c in all_cols if "Channel]" in c or "When/How]" in c or "Frequency]" in c or "Who Drinks]" in c]
    CAT_REASONS = [c for c in all_cols if "Why Choose]" in c or "Reason]" in c]
    CAT_ATTITUDES = [c for c in all_cols if "Psycho]" in c or "Kids Attitudes]" in c or "Bev Attitudes]" in c]
    CAT_PERCEPTIONS = [c for c in all_cols if "Brand Attitude]" in c]
    CAT_RAW = [c for c in all_cols if "Raw]" in c]
    
    if st.session_state['created_segments']:
        st.sidebar.markdown("---")
        st.sidebar.subheader("💾 Stored Segments")
        for seg in st.session_state['created_segments']:
            col_name, col_del = st.sidebar.columns([4, 1])
            col_name.markdown(f"`{seg}`")
            if col_del.button("❌", key=f"del_{seg}"):
                st.session_state['df_working'] = st.session_state['df_working'].drop(columns=[seg])
                st.session_state['df_valid'] = st.session_state['df_valid'].drop(columns=[seg])
                st.session_state['created_segments'].remove(seg)
                st.rerun()
                
        st.sidebar.markdown("---")
        if st.sidebar.button("🗑️ Clear All Segments", type="secondary"):
            st.session_state['df_working'] = st.session_state['df_working'].drop(columns=st.session_state['created_segments'])
            st.session_state['df_valid'] = st.session_state['df_valid'].drop(columns=st.session_state['created_segments'])
            st.session_state['created_segments'] = []
            st.rerun()

    st.sidebar.markdown("---")
    st.sidebar.subheader("📦 Export Current Workspace")
    workspace_export = {
        'df_working': st.session_state['df_working'],
        'df_valid': st.session_state['df_valid'],
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
                    is_scale = (("Psycho]" in stmt) and ("Core Value" not in stmt)) or ("Kids Attitudes]" in stmt)
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
            seg_valid_base_thresh = pd.Series(False, index=st.session_state['df_working'].index)
            seg_valid_base_mand = pd.Series(True, index=st.session_state['df_working'].index)
            
            for stmt, logic in statement_logic.items():
                matches_df[stmt] = get_scale_mask(st.session_state['df_working'], stmt, logic).astype(bool)
                if stmt in threshold_statements:
                    seg_valid_base_thresh = seg_valid_base_thresh | (st.session_state['df_valid'][stmt] == 1)
                if stmt in mandatory_statements:
                    seg_valid_base_mand = seg_valid_base_mand & (st.session_state['df_valid'][stmt] == 1)
            
            if threshold_statements and mandatory_statements: seg_valid_base = seg_valid_base_thresh & seg_valid_base_mand
            elif threshold_statements: seg_valid_base = seg_valid_base_thresh
            elif mandatory_statements: seg_valid_base = seg_valid_base_mand
            else: seg_valid_base = pd.Series(True, index=st.session_state['df_working'].index)
                    
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
                        st.session_state['df_valid'][segment_name] = seg_valid_base.astype(int)
                        st.session_state['created_segments'].append(segment_name)
                        st.rerun()

        st.markdown("---")
        st.subheader("📏 Saved Segments Sizing")
        if st.session_state['created_segments']:
            sizing_data = []
            total_pop = st.session_state['df_working']['Weight'].sum()
            metric_cols = st.columns(min(len(st.session_state['created_segments']), 4))
            
            for i, seg in enumerate(st.session_state['created_segments']):
                seg_wgt = st.session_state['df_working'][st.session_state['df_working'][seg] == 1]['Weight'].sum()
                seg_unw = len(st.session_state['df_working'][st.session_state['df_working'][seg] == 1])
                market_share = (seg_wgt / total_pop) if total_pop > 0 else 0
                
                with metric_cols[i % 4]:
                    st.metric(label=f"🎯 {seg}", value=f"{int(seg_wgt):,}", delta=f"{market_share * 100:.1f}% Market Share", delta_color="off")
                sizing_data.append({"Segment Name": seg, "Unweighted Count": seg_unw, "Weighted Count": int(seg_wgt), "Market Share (%)": market_share})
            
            st.markdown("<br>", unsafe_allow_html=True)
            st.dataframe(pd.DataFrame(sizing_data).style.format({"Market Share (%)": "{:.1%}", "Unweighted Count": "{:,}", "Weighted Count": "{:,}"}), use_container_width=True)
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
                        if "AND" in qc_logic: qc_valid_base = pd.Series(True, index=st.session_state['df_working'].index)
                        else: qc_valid_base = pd.Series(False, index=st.session_state['df_working'].index)
                        
                        for v in qc_vars:
                            is_scale = (("Psycho]" in v) and ("Core Value" not in v)) or ("Kids Attitudes]" in v)
                            v_mask = st.session_state['df_working'][v].isin([1, 2]) if is_scale else st.session_state['df_working'][v] == 1
                            if "AND" in qc_logic: 
                                qc_mask = qc_mask & v_mask
                                qc_valid_base = qc_valid_base & (st.session_state['df_valid'][v] == 1)
                            else: 
                                qc_mask = qc_mask | v_mask
                                qc_valid_base = qc_valid_base | (st.session_state['df_valid'][v] == 1)
                                
                        st.session_state['df_working'][qc_name] = qc_mask.astype(int)
                        st.session_state['df_valid'][qc_name] = qc_valid_base.astype(int)
                        st.session_state['created_segments'].append(qc_name)
                        st.success(f"✅ {qc_name} added to Saved Segments!")
                        st.rerun()

        st.markdown("---")
        st.markdown("### ⬇️ 1. Select Columns (Banners)")
        col_search_all = st.multiselect("🔍 Universal Search (Type a keyword, brand, or Q-number):", all_vars_for_selection, key="c_search_all")
        
        with st.expander("📂 Or Browse by Category (Columns)", expanded=False):
            c_col1, c_col2, c_col3, c_col4 = st.columns(4)
            with c_col1: col_demos = st.multiselect("Demographics", CAT_DEMOS, key="c_demo")
            with c_col2: col_cats = st.multiselect("Beverage Categories", CAT_CATEGORIES, key="c_cats")
            with c_col3: col_brands = st.multiselect("Brands & Products", CAT_BRANDS, key="c_brand")
            with c_col4: col_psycho = st.multiselect("Attitudes & Psychographics", CAT_ATTITUDES, key="c_psycho")
            
            ex_c1, ex_c2, ex_c3, ex_c4 = st.columns(4)
            with ex_c1: col_buy = st.multiselect("Buying Styles", CAT_BUYING, key="c_buy")
            with ex_c2: col_favs = st.multiselect("Rejectors & Favs", CAT_FAVS, key="c_favs")
            with ex_c3: col_chan = st.multiselect("Channels & Occasions", CAT_CHANNELS, key="c_chan")
            with ex_c4: col_reas = st.multiselect("Drivers & Perceptions", CAT_REASONS + CAT_PERCEPTIONS, key="c_reas")
            col_segs = st.multiselect("Saved Segments", st.session_state['created_segments'], default=st.session_state['created_segments'], key="c_segs")
            if CAT_RAW: col_raw = st.multiselect("Raw Variables", CAT_RAW, key="c_raw")
            else: col_raw = []

        raw_ct_cols = col_search_all + col_demos + col_cats + col_brands + col_psycho + col_buy + col_favs + col_chan + col_reas + col_segs + col_raw
        
        st.session_state['df_working']['Total Population'] = 1
        st.session_state['df_valid']['Total Population'] = 1
        ct_cols = ["Total Population"] + list(dict.fromkeys([x for x in raw_ct_cols if x]))
        
        st.markdown("---")
        st.markdown("### ➡️ 2. Select Rows (Stubs)")
        row_search_all = st.multiselect("🔍 Universal Search (Type a keyword, brand, or Q-number):", all_vars_for_selection, key="r_search_all")
        
        with st.expander("📂 Or Browse by Category (Rows)", expanded=False):
            r_col1, r_col2, r_col3, r_col4 = st.columns(4)
            with r_col1: row_demos = st.multiselect("Demographics ", CAT_DEMOS, key="r_demo")
            with r_col2: row_cats = st.multiselect("Beverage Categories ", CAT_CATEGORIES, key="r_cats")
            with r_col3: row_brands = st.multiselect("Brands & Products ", CAT_BRANDS, key="r_brand")
            with r_col4: row_psycho = st.multiselect("Attitudes & Psychographics ", CAT_ATTITUDES, key="r_psycho")
            
            ex_r1, ex_r2, ex_r3, ex_r4 = st.columns(4)
            with ex_r1: row_buy = st.multiselect("Buying Styles ", CAT_BUYING, key="r_buy")
            with ex_r2: row_favs = st.multiselect("Rejectors & Favs ", CAT_FAVS, key="r_favs")
            with ex_r3: row_chan = st.multiselect("Channels & Occasions ", CAT_CHANNELS, key="r_chan")
            with ex_r4: row_reas = st.multiselect("Drivers & Perceptions ", CAT_REASONS + CAT_PERCEPTIONS, key="r_reas")
            row_segs = st.multiselect("Saved Segments ", st.session_state['created_segments'], key="r_segs")
            if CAT_RAW: row_raw = st.multiselect("Raw Variables ", CAT_RAW, key="r_raw")
            else: row_raw = []

        raw_ct_rows = row_search_all + row_demos + row_cats + row_brands + row_psycho + row_buy + row_favs + row_chan + row_reas + row_segs + row_raw
        ct_rows = list(dict.fromkeys([x for x in raw_ct_rows if x]))
        
        if ct_rows and ct_cols:
            scale_vars_in_ct = [v for v in set(ct_rows + ct_cols) if (("Psycho]" in v) and ("Core Value" not in v)) or ("Kids Attitudes]" in v) or (v == "Total Population")]
            ct_logic_dict = {}
            if scale_vars_in_ct:
                with st.expander("⚙️ Fine-Tune Attitude Scales for Rows & Columns (Defaults to Any Agree)", expanded=False):
                    col_rl1, col_rl2 = st.columns(2)
                    for i, v in enumerate(scale_vars_in_ct):
                        if v == "Total Population": continue
                        t_col = col_rl1 if i % 2 == 0 else col_rl2
                        with t_col:
                            ct_logic_dict[v] = st.selectbox(f"{v[:40]}...", options=SCALE_OPTIONS[2:], index=0, key=f"ct_logic_all_{v}")

            export_data = []
            universe_row = ["Column Base (N)"]
            col_baselines = {}
            
            for c in ct_cols:
                is_scale = (("Psycho]" in c) and ("Core Value" not in c)) or ("Kids Attitudes]" in c)
                if c == "Total Population":
                    col_mask = st.session_state['df_working'][c] == 1
                    c_label = c
                elif is_scale:
                    logic = ct_logic_dict.get(c, "Any Agree (1 or 2 combined)")
                    col_mask = get_scale_mask(st.session_state['df_working'], c, logic)
                    short_suffix = logic.split(" (")[0]
                    c_label = f"{c} ({short_suffix})"
                else:
                    col_mask = st.session_state['df_working'][c] == 1
                    c_label = c
                    
                col_weighted = st.session_state['df_working'][col_mask]['Weight'].sum()
                col_baselines[c] = {"mask": col_mask, "label": c_label}
                universe_row.extend([col_weighted, col_weighted, 1.00, 1.00, 100])
                
            export_data.append(universe_row)
            
            for r in ct_rows:
                if r == "Total Population": continue
                is_scale = (("Psycho]" in r) and ("Core Value" not in r)) or ("Kids Attitudes]" in r)
                if is_scale:
                    logic = ct_logic_dict.get(r, "Any Agree (1 or 2 combined)")
                    r_mask = get_scale_mask(st.session_state['df_working'], r, logic)
                    short_suffix = logic.split(" (")[0]
                    r_label = f"{r} ({short_suffix})"
                else:
                    r_mask = st.session_state['df_working'][r] == 1
                    r_label = r
                    
                r_valid_mask = st.session_state['df_valid'][r] == 1
                stmt_weighted = st.session_state['df_working'][r_mask]['Weight'].sum()
                r_valid_weighted = st.session_state['df_working'][r_valid_mask]['Weight'].sum()
                stmt_vert_pct = (stmt_weighted / r_valid_weighted) if r_valid_weighted > 0 else 0
                
                r_data = [r_label]
                for c in ct_cols:
                    c_mask = col_baselines[c]["mask"]
                    cross_mask = r_mask & c_mask
                    cross_weighted = st.session_state['df_working'][cross_mask]['Weight'].sum()
                    
                    valid_for_cell_mask = c_mask & r_valid_mask
                    cell_base_wgt = st.session_state['df_working'][valid_for_cell_mask]['Weight'].sum()
                    
                    vert_pct = (cross_weighted / cell_base_wgt) if cell_base_wgt > 0 else 0
                    horz_pct = (cross_weighted / stmt_weighted) if stmt_weighted > 0 else 0
                    idx_score = (vert_pct / stmt_vert_pct * 100) if stmt_vert_pct > 0 else 0
                    
                    r_data.extend([cross_weighted, cell_base_wgt, vert_pct, horz_pct, int(round(idx_score, 0))])
                export_data.append(r_data)
            
            preview_headers = ["Statement"]
            metrics = ["Count", "Base (N)", "Vertical(%)", "Horizontal(%)", "Index"]
            for c in ct_cols:
                c_display = col_baselines[c]["label"]
                for m in metrics: preview_headers.append(f"{c_display} - {m}")
                    
            df_preview = pd.DataFrame(export_data, columns=preview_headers).set_index("Statement")
            
            st.markdown("---")
            st.markdown("**Preview (First 10 Rows):**")
            format_dict = {}
            for col in df_preview.columns:
                if "Vertical" in col or "Horizontal" in col: format_dict[col] = "{:.1%}" 
                elif "Count" in col or "Base (N)" in col: format_dict[col] = "{:,.0f}"
                elif "Index" in col: format_dict[col] = "{:.0f}"
            st.dataframe(df_preview.head(10).style.format(format_dict))
            
            excel_headers = ["Statement"] 
            excel_sub_headers = [""]
            for c in ct_cols:
                c_display = col_baselines[c]["label"]
                excel_headers.extend([c_display, "", "", "", ""])
                excel_sub_headers.extend(["Count", "Base (N)", "Vertical(%)", "Horizontal(%)", "Index"])
                
            df_excel = pd.DataFrame(export_data).set_index(0)
            df_excel.index.name = "Statement"
            df_excel.columns = pd.MultiIndex.from_tuples(zip(excel_headers[1:], excel_sub_headers[1:]))
            
            output = io.BytesIO()
            with pd.ExcelWriter(output, engine='openpyxl') as writer:
                pd.DataFrame([
                    ["CROSSTAB TITLE : Universal Crosstabs"], 
                    ["STUDY NAME : Advanced Market Mapper"], 
                    ["SELECTED BASE : Dynamic Question-Level Auto-Base (N sizes automatically adjust to exclude skipped respondents)"], 
                    ["WEIGHT TYPE : Weighted Population"]
                ]).to_excel(writer, index=False, header=False, sheet_name='Crosstab', startrow=0)
                
                df_excel.to_excel(writer, index=True, sheet_name='Crosstab', startrow=9)
                worksheet = writer.sheets['Crosstab']
                for row in worksheet.iter_rows(min_row=12, max_row=worksheet.max_row):
                    for cell in row:
                        if cell.column == 1: continue  
                        col_mod = (cell.column - 1) % 5
                        if col_mod in [3, 4]: cell.number_format = '0.0%'
                        elif col_mod in [1, 2]: cell.number_format = '#,##0'
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
            scale_vars_map = [v for v in set(map_rows + map_cols) if (("Psycho]" in v) and ("Core Value" not in v)) or ("Kids Attitudes]" in v)]
            map_logic_dict = {}
            if scale_vars_map:
                with st.expander("⚙️ Fine-Tune Attitude Scales (Defaults to Any Agree)", expanded=False):
                    col_ml1, col_ml2 = st.columns(2)
                    for i, v in enumerate(scale_vars_map):
                        m_col = col_ml1 if i % 2 == 0 else col_ml2
                        with m_col: map_logic_dict[v] = st.selectbox(f"{v[:40]}...", options=SCALE_OPTIONS[2:], index=0, key=f"map_logic_{v}")
        
        if st.button("🗺️ Generate Map") and map_rows and len(map_cols) > 1:
            map_matrix = []
            for r in map_rows:
                r_data = []
                is_scale_r = (("Psycho]" in r) and ("Core Value" not in r)) or ("Kids Attitudes]" in r)
                if is_scale_r:
                    logic = map_logic_dict.get(r, "Any Agree (1 or 2 combined)")
                    r_mask = get_scale_mask(st.session_state['df_working'], r, logic)
                else: r_mask = st.session_state['df_working'][r] == 1
                    
                for c in map_cols:
                    is_scale_c = (("Psycho]" in c) and ("Core Value" not in c)) or ("Kids Attitudes]" in c)
                    if is_scale_c:
                        logic = map_logic_dict.get(c, "Any Agree (1 or 2 combined)")
                        c_mask = get_scale_mask(st.session_state['df_working'], c, logic)
                    else: c_mask = st.session_state['df_working'][c] == 1
                        
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
                
                fig, ax = plt.subplots(figsize=(10, 8))
                ax.scatter(row_coords[:, 0], row_coords[:, 1], color='steelblue', s=60)
                for i, txt in enumerate(df_map.index): ax.annotate(txt[:25]+"...", (row_coords[i, 0], row_coords[i, 1] + 0.005), color='darkblue', fontsize=9)
                ax.scatter(col_coords[:, 0], col_coords[:, 1], color='crimson', marker='s', s=100)
                for i, txt in enumerate(df_map.columns): ax.annotate(txt, (col_coords[i, 0], col_coords[i, 1] - 0.015), color='darkred', fontsize=11, weight='bold')
                ax.axhline(0, color='black', linewidth=0.8)
                ax.axvline(0, color='black', linewidth=0.8)
                st.pyplot(fig)
            else: st.warning("Not enough data overlap to calculate dimensions.")
else: st.info("⬅️ Please upload the Master Data File in the sidebar to begin.")
