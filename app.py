import streamlit as st
import pandas as pd

st.set_page_config(page_title="IBS Classroom Dashboard")

st.title("IBS-HYD Classroom Occupancy Dashboard")

try:
    df = pd.read_csv("master_timetable.csv")

    st.success("Timetable Loaded Successfully")

    st.subheader("Timetable")

    st.dataframe(df)

    st.subheader("Search Faculty")

    faculty = st.selectbox(
        "Select Faculty",
        sorted(df["Faculty"].dropna().unique())
    )

    faculty_data = df[df["Faculty"] == faculty]

    st.dataframe(faculty_data)

except Exception as e:
    st.error(e)
