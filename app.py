
import streamlit as st
import pandas as pd
from pybaseball import statcast, playerid_lookup
from datetime import date
import datetime

st.title("⚾ MLB Pitcher Weak Spot Analyzer")

st.markdown("""
This app shows which **batting order slot (1–9)** has hit the most home runs against a selected pitcher using Statcast data.
""")

# Get today's date
today = date.today()

# List of sample pitchers for selection (you can expand or automate this)
pitcher_options = {
    "Mike Soroka": ("Soroka", "Mike"),
    "Logan Webb": ("Webb", "Logan"),
    "Gerrit Cole": ("Cole", "Gerrit"),
    "Zac Gallen": ("Gallen", "Zac"),
    "Blake Snell": ("Snell", "Blake"),
    "Max Fried": ("Fried", "Max"),
    "Corbin Burnes": ("Burnes", "Corbin")
}

# Select pitcher
selected_pitcher = st.selectbox("Choose a pitcher:", list(pitcher_options.keys()))
last_name, first_name = pitcher_options[selected_pitcher]

# Get MLBAM ID
s = playerid_lookup(last_name, first_name)
if s.empty:
    st.error("Pitcher not found in database.")
else:
    pitcher_id = s.loc[s['name_first'] == first_name, 'key_mlbam'].values[0]

    # Fetch Statcast data
    with st.spinner("Fetching Statcast data..."):
        start_dt = '2024-01-01'
        end_dt = today.strftime('%Y-%m-%d')
        data = statcast(start_dt=start_dt, end_dt=end_dt, pitcher=pitcher_id)

    # Filter home runs and group by batting order
    hr_data = data[data['events'] == 'home_run']
    order_counts = hr_data['batting_order'].value_counts().sort_index()
    df = order_counts.to_frame("HRs Allowed")

    st.subheader(f"📊 HRs Allowed by Batting Order Slot — {selected_pitcher}")
    if not df.empty:
        st.bar_chart(df)
        worst_slot = df['HRs Allowed'].idxmax()
        worst_hr = df['HRs Allowed'].max()
        st.markdown(f"### 🚨 **{selected_pitcher}** gives up the most HRs to slot **#{worst_slot}** with **{worst_hr} HRs**.")
    else:
        st.success("🎉 No home runs allowed by this pitcher in the selected date range.")
