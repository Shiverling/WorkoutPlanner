import streamlit as st
import pandas as pd
import plotly.express as px
import json
from datetime import datetime

# Initialize session state
def init_session():
    if 'plans' not in st.session_state:
        st.session_state.plans = {}
    if 'selected_plan' not in st.session_state:
        st.session_state.selected_plan = None

init_session()

# App title
st.title("Weekly Workout Planner with Recovery Visualizer")

# Sidebar for Plan Selection and Management
st.sidebar.header("Manage Plans")

plan_name = st.sidebar.text_input("Plan Name")
if st.sidebar.button("Create New Plan"):
    if plan_name and plan_name not in st.session_state.plans:
        st.session_state.plans[plan_name] = []
        st.session_state.selected_plan = plan_name

selected = st.sidebar.selectbox("Select Plan", list(st.session_state.plans.keys()))
if selected:
    st.session_state.selected_plan = selected

if st.sidebar.button("Delete Selected Plan") and st.session_state.selected_plan:
    del st.session_state.plans[st.session_state.selected_plan]
    st.session_state.selected_plan = None

# Add/Edit Workout
st.header("Add/Edit Workout")
if st.session_state.selected_plan:
    day = st.selectbox("Day of the Week", ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"])
    time = st.time_input("Time")
    muscle_group = st.selectbox("Muscle Group", ["Chest", "Back", "Legs", "Arms", "Shoulders", "Core", "Full Body"])
    duration = st.number_input("Duration (minutes)", min_value=10, max_value=180, value=60)
    if st.button("Add Workout"):
        st.session_state.plans[st.session_state.selected_plan].append({
            "day": day,
            "time": str(time),
            "muscle_group": muscle_group,
            "duration": duration,
            "timestamp": datetime.now().isoformat()
        })

    # Display Editable Table
    df = pd.DataFrame(st.session_state.plans[st.session_state.selected_plan])
    st.subheader("Workout Plan")
    if not df.empty:
        editable_df = st.data_editor(df, num_rows="dynamic", key="editable")
        st.session_state.plans[st.session_state.selected_plan] = editable_df.to_dict("records")
    else:
        st.info("No workouts added yet.")

    # Recovery Visualizer and Usefulness
    st.subheader("Recovery & Usefulness Visualizer")
    if not df.empty:
        # Compute recovery index (simple model)
        muscle_days = {}
        recovery_data = []

        for idx, row in df.iterrows():
            day_index = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"].index(row['day'])
            mg = row['muscle_group']

            if mg not in muscle_days:
                muscle_days[mg] = []

            last_day = max(muscle_days[mg]) if muscle_days[mg] else None
            recovery_gap = day_index - last_day if last_day is not None else 7
            muscle_days[mg].append(day_index)

            if recovery_gap >= 3:
                color = "green"
                usefulness = 100
            elif recovery_gap == 2:
                color = "yellow"
                usefulness = 75
            elif recovery_gap == 1:
                color = "orange"
                usefulness = 40
            else:
                color = "red"
                usefulness = 10

            recovery_data.append({
                "Day": row['day'],
                "Muscle Group": mg,
                "Usefulness %": usefulness,
                "Color": color
            })

        vis_df = pd.DataFrame(recovery_data)
        fig = px.bar(vis_df, x="Day", y="Usefulness %", color="Color",
                     hover_data=["Muscle Group"],
                     color_discrete_map={"green": "green", "yellow": "yellow", "orange": "orange", "red": "red"})
        st.plotly_chart(fig)

else:
    st.warning("Please create or select a workout plan to continue.")

# Save Plans to JSON (optional local download)
if st.button("Download Plans as JSON"):
    st.download_button("Download", data=json.dumps(st.session_state.plans, indent=2), file_name="workout_plans.json")
