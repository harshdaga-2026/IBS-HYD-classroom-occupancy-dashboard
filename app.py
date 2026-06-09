import streamlit as st
import pandas as pd

st.set_page_config(
    page_title="IBS-HYD Classroom Occupancy Dashboard",
    layout="wide"
)

st.title("IBS-HYD Classroom Occupancy Dashboard")

try:

    df = pd.read_csv("master_timetable.csv")

    st.success("Timetable Loaded Successfully")

    # KPI

    total_rooms = df["Room"].nunique()

    st.metric(
        "Total Rooms",
        total_rooms
    )

    # Full Timetable

    st.header("Full Timetable")

    st.dataframe(df)

    st.divider()

    # Faculty Search

    st.header("Faculty Search")

    faculty = st.selectbox(
        "Select Faculty",
        sorted(df["Faculty"].dropna().unique())
    )

    faculty_data = df[df["Faculty"] == faculty]

    st.dataframe(faculty_data)

    st.divider()

    # Room Search

    st.header("Room Search")

    room = st.selectbox(
        "Select Room",
        sorted(df["Room"].dropna().unique())
    )

    room_data = df[df["Room"] == room]

    st.dataframe(room_data)

    st.divider()

    # Vacant Room Finder

    st.header("Vacant Room Finder")

    selected_day = st.selectbox(
        "Select Day",
        sorted(df["Day"].unique())
    )

    selected_time = st.selectbox(
        "Select Time Slot",
        sorted(df["Time_Slot"].unique())
    )

    occupied_rooms = df[
        (df["Day"] == selected_day)
        &
        (df["Time_Slot"] == selected_time)
    ]["Room"].tolist()

    all_rooms = sorted(
        df["Room"].dropna().unique()
    )

    vacant_rooms = [
        room
        for room in all_rooms
        if room not in occupied_rooms
    ]

    st.write("### Vacant Rooms")

    st.write(vacant_rooms)

    st.divider()


except Exception as e:

    st.error(e)
