import streamlit as st
import pandas as pd
import gspread
from google.oauth2.service_account import Credentials
from datetime import date

st.set_page_config(
    page_title="IBS-HYD Classroom Occupancy Dashboard",
    layout="wide"
)

st.title("IBS-HYD Classroom Occupancy Dashboard")

# GOOGLE SHEETS CONNECTION

try:
    scope = [
        "https://www.googleapis.com/auth/spreadsheets",
        "https://www.googleapis.com/auth/drive"
    ]

    creds = Credentials.from_service_account_info(
        st.secrets["gcp_service_account"],
        scopes=scope
    )

    client = gspread.authorize(creds)

    sheet = client.open("IBS Room Bookings").sheet1

    st.success("Google Sheets Connected Successfully")

except Exception as e:
    st.error(f"Google Sheets Error: {e}")

# ==================================================
# MASTER ROOM LIST
# ==================================================

lt_rooms = [
    "LT-A","LT-B","LT-C","LT-D","LT-E","LT-F",
    "LT-G","LT-H","LT-I","LT-J","LT-K","LT-L"
]

cr_rooms = [f"CR-{i}" for i in range(1,29)]

all_rooms = lt_rooms + cr_rooms

# ==================================================
# LOAD DATA
# ==================================================

try:

    df = pd.read_csv("master_timetable.csv")

    st.success("Timetable Loaded Successfully")

    # ==================================================
    # KPI SECTION
    # ==================================================

    total_rooms = len(all_rooms)

    col1, col2, col3 = st.columns(3)

    col1.metric("Total Rooms", total_rooms)
    col2.metric("LT Rooms", len(lt_rooms))
    col3.metric("CR Rooms", len(cr_rooms))

    st.divider()

    # ==================================================
    # FULL TIMETABLE
    # ==================================================

    st.header("Full Timetable")

    st.dataframe(df, use_container_width=True)

    st.divider()

    # ==================================================
    # FACULTY SEARCH
    # ==================================================

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

    # ==================================================
    # ROOM SEARCH
    # ==================================================

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
            f"{room} is currently not used in the timetable."
        )

    st.divider()

    # ==================================================
    # VACANT ROOM FINDER
    # ==================================================

    st.header("Vacant Room Finder")

    col1, col2, col3 = st.columns(3)

    with col1:
        selected_day = st.selectbox(
            "Select Day",
            sorted(df["Day"].dropna().unique())
        )

    with col2:
        selected_time = st.selectbox(
            "Select Time Slot",
            sorted(df["Time_Slot"].dropna().unique())
        )

    with col3:
        room_type = st.selectbox(
            "Room Type",
            ["All", "LT Only", "CR Only"]
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

    if room_type == "LT Only":
        vacant_rooms = [
            room
            for room in vacant_rooms
            if room.startswith("LT")
        ]

    elif room_type == "CR Only":
        vacant_rooms = [
            room
            for room in vacant_rooms
            if room.startswith("CR")
        ]

    col1, col2 = st.columns(2)

    with col1:
        st.subheader("Occupied Rooms")
        st.write(sorted(occupied_rooms))

    with col2:
        st.subheader("Vacant Rooms")
        st.write(sorted(vacant_rooms))

    st.divider()

    # ==================================================
    # OCCUPANCY SUMMARY
    # ==================================================

    st.header("Occupancy Summary")

    occupied_count = len(occupied_rooms)

    if room_type == "LT Only":
        total_available = len(lt_rooms)

    elif room_type == "CR Only":
        total_available = len(cr_rooms)

    else:
        total_available = len(all_rooms)

    vacant_count = total_available - occupied_count

    occupancy_percent = round(
        (occupied_count / total_available) * 100,
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
    # ==================================================
    # BOOK ROOM
    # ==================================================

    st.header("Book a Room")

    with st.form("booking_form"):

        requester = st.text_input("Your Name")
        email = st.text_input("Email")
        event_name = st.text_input("Event Name")

        booking_day = st.selectbox(
            "Day",
            sorted(df["Day"].dropna().unique())
        )

        booking_time = st.selectbox(
            "Time Slot",
            sorted(df["Time_Slot"].dropna().unique())
        )
        occupied_rooms = df[
            (df["Day"] == booking_day)
            &
            (df["Time_Slot"] == booking_time)
        ]["Room"].tolist()
        
        bookings = sheet.get_all_records()
        
        approved_rooms = []
        
        for row in bookings:
        
            if (
                row["Day"] == booking_day
                and row["Time_Slot"] == booking_time
                and row["Status"] == "Approved"
            ):
                approved_rooms.append(row["Room"])
        
        available_rooms = [
            room
            for room in all_rooms
            if room not in occupied_rooms
            and room not in approved_rooms
        ]
        
        booking_room = st.selectbox(
            "Available Rooms",
            sorted(available_rooms)
        )
        

        submit = st.form_submit_button("Submit Booking Request")

        if submit:

            occupied_rooms = df[
                (df["Day"] == booking_day)
                &
                (df["Time_Slot"] == booking_time)
            ]["Room"].tolist()

            if booking_room in occupied_rooms:

                st.error(
                    "Room already occupied by a class."
                )

            else:

                request_id = len(sheet.get_all_records()) + 1

                sheet.append_row([
                    request_id,
                    "",
                    booking_day,
                    booking_time,
                    booking_room,
                    event_name,
                    requester,
                    email,
                    "Pending"
                ])

                st.success(
                    "Booking Request Submitted Successfully!"
                )
    
            
except Exception as e:

    st.error(f"Error: {e}")
