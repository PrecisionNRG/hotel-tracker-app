
import streamlit as st
import pandas as pd
import os
import hashlib
from datetime import datetime

LOG_FILE = "hotel_log.csv"

# --------------------------
# Login System
# --------------------------
USERS = {
    "admin": "letmein",
    "employee": "employee123"
}

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

HASHED_USERS = {u: hash_password(p) for u, p in USERS.items()}

if "authenticated" not in st.session_state:
    st.session_state.authenticated = False
    st.session_state.username = ""

if not st.session_state.authenticated:
    st.title("🔐 Login")
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")
    if st.button("Login"):
        if username in HASHED_USERS and hash_password(password) == HASHED_USERS[username]:
            st.session_state.authenticated = True
            st.session_state.username = username
            st.success(f"✅ Welcome, {username}!")
            st.experimental_rerun()
        else:
            st.error("❌ Invalid credentials")
    st.stop()

# --------------------------
# Admin View
# --------------------------
if st.session_state.username == "admin":
    st.title("📚 Admin Dashboard - Hotel Log History")
    if os.path.exists(LOG_FILE):
        df_log = pd.read_csv(LOG_FILE)
        st.dataframe(df_log, use_container_width=True)
        st.download_button("📥 Download CSV Log", df_log.to_csv(index=False), file_name="hotel_log.csv", mime="text/csv")
    else:
        st.info("No entries have been submitted yet.")

# --------------------------
# Employee View (Form)
# --------------------------
else:
    st.title("🏨 Precision Energy Hotel Usage Tracker")
    st.write("Easily log and track employee hotel stays.")

    # Logo (optional - centered)
    st.markdown(
        """
        <div style="text-align: center; padding-top: 30px; padding-bottom: 10px;">
            <img src="logo.png" width="150">
            <div style="font-size: 14px; color: gray;">Precision Energy Systems</div>
        </div>
        """,
        unsafe_allow_html=True
    )

    # HOTEL DETAILS
    st.subheader("Hotel Information")
    hotel_name = st.text_input("Hotel Name")
    hotel_address = st.text_input("Hotel Address")
    hotel_phone = st.text_input("Hotel Phone")
    hotel_contact = st.text_input("Hotel Contact Person")
    hotel_confirmation = st.text_input("Hotel Confirmation Number")

    # ROOM DETAILS
    st.subheader("Room Assignments")
    room_entries = []
    num_rooms = st.number_input("How many rooms to log?", min_value=1, max_value=20, value=1)

    for i in range(num_rooms):
        st.markdown(f"**Room {i+1} Details**")
        room_num = st.text_input(f"Room Number", key=f"room_num_{i}")
        emp_day = st.text_input(f"Employee (Day Shift)", key=f"emp_day_{i}")
        emp_night = st.text_input(f"Employee (Night Shift)", key=f"emp_night_{i}")
        check_in = st.date_input(f"Check-In Date", key=f"check_in_{i}")
        check_out = st.date_input(f"Check-Out Date", key=f"check_out_{i}")
        room_entries.append({
            "Room #": room_num,
            "Employee (Day)": emp_day,
            "Employee (Night)": emp_night,
            "Check-In": check_in,
            "Check-Out": check_out
        })

    # PREPARED BY
    st.subheader("Administrative Info")
    prepared_by = st.text_input("Prepared By")
    date_prepared = st.date_input("Date Prepared", value=datetime.today())
    job_number = st.text_input("Job Number")

    # SUBMIT BUTTON
    if st.button("📩 Submit Entry"):
        df_new = pd.DataFrame()
        for row in room_entries:
            record = {
                "Hotel Name": hotel_name,
                "Hotel Address": hotel_address,
                "Hotel Phone": hotel_phone,
                "Hotel Contact": hotel_contact,
                "Confirmation #": hotel_confirmation,
                "Room #": row["Room #"],
                "Employee (Day)": row["Employee (Day)"],
                "Employee (Night)": row["Employee (Night)"],
                "Check-In": row["Check-In"],
                "Check-Out": row["Check-Out"],
                "Prepared By": prepared_by,
                "Date Prepared": date_prepared,
                "Job Number": job_number
            }
            df_new = pd.concat([df_new, pd.DataFrame([record])], ignore_index=True)

        if os.path.exists(LOG_FILE):
            old_data = pd.read_csv(LOG_FILE)
            df_new = pd.concat([old_data, df_new], ignore_index=True)

        df_new.to_csv(LOG_FILE, index=False)
        st.success("✅ Entry saved successfully!")
