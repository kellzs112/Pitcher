
import streamlit as st
import pandas as pd
from pybaseball import statcast, playerid_lookup
from datetime import date

st.title("⚾ Pitcher Weak Spot Analyzer")
st.markdown("Shows the batting order position (1–9) that hits the most HRs against selected pitchers.")

# Pitcher selection
pitchers = {
    "Mike Soroka": ("Soroka", "Mike"),
    "Mason Birdsong": ("Birdsong", "Mason"),
    "Blake Snell": ("Snell", "Blake"),
    "Zac Gallen": ("Gallen", "Zac"),
    "Corbin Burnes": ("Burnes", "Corbin")
}
pitcher_name = st.selectbox("Choose a pitcher:", list(pitchers.keys()))
last_name, first_name = pitchers[pitcher_name]

# Look up pitcher ID
lookup = playerid_lookup(last_name, first_name)
match = lookup[
    (lookup['name_first'].str.lower() == first_name.lower()) &
    (lookup['name_last'].str.lower() == last_name.lower())
]

if match.empty:
    st.error(f"❌ Could not find player ID for {pitcher_name}.")
else:
    pitcher_id = match['key_mlbam'].values[0]
    st.info(f"Pitcher ID: {pitcher_id}")

    # Fetch statcast data
    start_date = "2024-01-01"
    end_date = date.today().strftime("%Y-%m-%d")
    with st.spinner("Fetching Statcast data..."):
        data = statcast(start_dt=start_date, end_dt=end_date, pitcher=pitcher_id)

    # Filter HRs
    hr_data = data[data['events'] == 'home_run']
    if 'batting_order' in hr_data.columns and not hr_data.empty:
        hr_counts = hr_data['batting_order'].value_counts().sort_index()
        df = pd.DataFrame(hr_counts).reset_index()
        df.columns = ['Batting Order Slot', 'HRs Allowed']
        st.bar_chart(df.set_index('Batting Order Slot'))
        max_row = df.loc[df['HRs Allowed'].idxmax()]
        st.markdown(f"### 🚨 Weakest slot: **#{int(max_row['Batting Order Slot'])}** — {int(max_row['HRs Allowed'])} HRs")
    else:
        st.success("🎉 No HRs allowed by this pitcher during the selected period.")
