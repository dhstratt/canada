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
    for col, value_map in DEMO_
