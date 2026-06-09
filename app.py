import streamlit as st
import pandas as pd

st.set_page_config(
    page_title="IBS-HYD Classroom Occupancy Dashboard",
    layout="wide"
)

st.title("IBS-HYD Classroom Occupancy Dashboard")

# --------------------------------------------------
# MASTER ROOM LIST
# --------------------------------------------------

lt_rooms = [
    "LT-A","LT-B","LT-C","LT-D","LT-E","LT-F",
    "LT-G","LT-H","LT-I","LT-J","LT-K","LT-L"
]

cr_rooms = [f"CR-{i}" for i in range(1,29)]

all_rooms = lt_rooms + cr_rooms

# --------------------------------------------------
# LOAD DATA
# --------------------------------------------------

try:

    df = pd.read_csv("master_timetable.csv")

    st.success("Timetable Loaded Successfully")

    # --------------------------------------------------
    # KPI SECTION
    # --------------------------------------------------

    total_rooms = len(all_rooms)

    col1, col2, col3 = st.columns(3)

    col1.metric("Total Rooms", total_rooms)

    col2.metric("LT Rooms", len(lt_rooms))

    col3.metric("CR Rooms", len(cr_rooms))

    st.divider()

    # --------------------------------------------------
    # FULL TIMETABLE
    # --------------------------------------------------

    st.header("Full Timetable")

    st.dataframe(df, use_container_width=True)

    st.divider()

    # --------------------------------------------------
    # FACULTY SEARCH
    # --------------------------------------------------

    st.header("Faculty Search")

    faculty = st.selectbox(
        "Select Faculty",
        sorted(df["Faculty"].dropna().unique())
    )

    faculty_data = df[df["Faculty"] == faculty]

    st.dataframe(
        faculty_data,
        use_container_width=True
    )

    st.divider()

    # --------------------------------------------------
    # ROOM SEARCH
    # --------------------------------------------------

    st.header("Room Search")

    room = st.selectbox(
        "Select Room",
        sorted(all_rooms)
    )

    room_data = df[df["Room"] == room]

    if len(room_data) > 0:
        st.dataframe(
            room_data,
            use_container_width=True
        )
    else:
        st.warning(
            f"{room} is not used in the timetable."
        )

    st.divider()

    # --------------------------------------------------
    # VACANT ROOM FINDER
    # --------------------------------------------------

    st.header("Vacant Room Finder")

    selected_day = st.selectbox(
        "Select Day",
        sorted(df["Day"].dropna().unique())
    )

    selected_time = st.selectbox(
        "Select Time Slot",
        sorted(df["Time_Slot"].dropna().unique())
    )

    occupied_rooms = df[
        (df["Day"] == selected_day)
        &
        (df["Time_Slot"] == selected_time)
    ]["Room"].tolist()

    vacant_rooms = [
        room
        for room in all_rooms
        if room not in occupied_rooms
    ]

    col1, col2 = st.columns(2)

    with col1:
        st.subheader("Occupied Rooms")
        st.write(sorted(occupied_rooms))

    with col2:
        st.subheader("Vacant Rooms")
        st.write(sorted(vacant_rooms))

    st.divider()

    # --------------------------------------------------
    # OCCUPANCY SUMMARY
    # --------------------------------------------------

    st.header("Occupancy Summary")

    occupied_count = len(occupied_rooms)

    vacant_count = len(vacant_rooms)

    occupancy_percent = round(
        (occupied_count / total_rooms) * 100,
        2
    )

    c1, c2, c3 = st.columns(3)

    c1.metric(
        "Occupied Rooms",
        occupied_count
    )

    c2.metric(
        "Vacant Rooms",
        vacant_count
    )

    c3.metric(
        "Occupancy %",
        f"{occupancy_percent}%"
    )

except Exception as e:

    st.error(f"Error: {e}")
