import streamlit as st
import pandas as pd
import os
import hashlib
from datetime import datetime
from email.message import EmailMessage
import smtplib

# --------------------------
# Email Function
# --------------------------
def send_confirmation_email(hotel_name, job_number, prepared_by, room_entries):
    msg = EmailMessage()
    msg["Subject"] = "📬 New Hotel Log Entry Submitted"
    msg["From"] = os.environ.get("SMTP_EMAIL")
    msg["To"] = os.environ.get("SEND_TO")

    # Build detailed summary
    summary = f"""
Hotel: {hotel_name}
Job Number: {job_number}
Prepared By: {prepared_by}
Total Rooms: {len(room_entries)}

Room Details:
"""
    for i, room in enumerate(room_entries, start=1):
        summary += f"""
Room {i}:
  • Room #: {room['Room #']}
  • Employee (Day): {room['Employee (Day)']}
  • Employee (Night): {room['Employee (Night)']}
  • Check-In: {room['Check-In']}
  • Check-Out: {room['Check-Out']}
  • Actual Cost: ${room['Actual Cost']:.2f}
"""

    msg.set_content(summary)

    try:
        with smtplib.SMTP(os.environ.get("SMTP_SERVER"), int(os.environ.get("SMTP_PORT"))) as server:
            server.starttls()
            server.login(os.environ.get("SMTP_EMAIL"), os.environ.get("SMTP_PASSWORD"))
            server.send_message(msg)
        st.info("📧 Confirmation email sent.")
    except Exception as e:
        st.error(f"❌ Email failed: {e}")

# --------------------------
# App Setup
# --------------------------
LOG_FILE = "hotel_log.csv"
USERS = {
    "admin": "letmein",
    "employee": "employee1"
}

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

HASHED_USERS = {u: hash_password(p) for u, p in USERS.items()}

# --------------------------
# Authentication
# --------------------------
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
            st.rerun()
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
# Employee View
# --------------------------
else:
    st.image("logo.png", width=150, caption="Precision Energy Systems")
    st.title("🏨 Precision Energy Hotel Usage Tracker")
    st.write("Easily log and track employee hotel stays.")

    st.subheader("Hotel Information")
    hotel_name = st.text_input("Hotel Name")
    hotel_address = st.text_input("Hotel Address")
    hotel_phone = st.text_input("Hotel Phone")
    hotel_contact = st.text_input("Hotel Contact Person")
    hotel_confirmation = st.text_input("Hotel Confirmation Number")
    negotiated_rate = st.number_input("Negotiated Rate Per Night ($)", min_value=0.0, format="%.2f")

    st.subheader("Room Assignments")
    room_entries = []
    num_rooms = st.number_input("How many rooms to log?", min_value=1, max_value=20, value=1)

    for i in range(num_rooms):
        st.markdown(f"**Room {i+1} Details**")
        room_num = st.text_input("Room Number", key=f"room_num_{i}")
        emp_day = st.text_input("Employee (Day Shift)", key=f"emp_day_{i}")
        emp_night = st.text_input("Employee (Night Shift)", key=f"emp_night_{i}")
        check_in = st.date_input("Check-In Date", key=f"check_in_{i}")
        check_out = st.date_input("Check-Out Date", key=f"check_out_{i}")
        actual_cost = st.number_input("Actual Cost ($)", min_value=0.0, format="%.2f", key=f"actual_cost_{i}")
        room_entries.append({
            "Room #": room_num,
            "Employee (Day)": emp_day,
            "Employee (Night)": emp_night,
            "Check-In": check_in.strftime("%m/%d/%Y"),
            "Check-Out": check_out.strftime("%m/%d/%Y"),
            "Actual Cost": actual_cost
        })

    st.subheader("Administrative Info")
    prepared_by = st.text_input("Prepared By")
    date_prepared = datetime.today().strftime("%m/%d/%Y")
    job_number = st.text_input("Job Number")

    if st.button("📩 Submit Entry"):
        df_new = pd.DataFrame()
        for row in room_entries:
            record = {
                "Hotel Name": hotel_name,
                "Hotel Address": hotel_address,
                "Hotel Phone": hotel_phone,
                "Hotel Contact": hotel_contact,
                "Confirmation #": hotel_confirmation,
                "Negotiated Rate": negotiated_rate,
                "Room #": row["Room #"],
                "Employee (Day)": row["Employee (Day)"],
                "Employee (Night)": row["Employee (Night)"],
                "Check-In": row["Check-In"],
                "Check-Out": row["Check-Out"],
                "Actual Cost": row["Actual Cost"],
                "Prepared By": prepared_by,
                "Date Prepared": date_prepared,
                "Job Number": job_number
            }
            df_new = pd.concat([df_new, pd.DataFrame([record])], ignore_index=True)

        if os.path.exists(LOG_FILE):
            old_data = pd.read_csv(LOG_FILE)
            df_new = pd.concat([old_data, df_new], ignore_index=True)

        df_new.to_csv(LOG_FILE, index=False)
        send_confirmation_email(hotel_name, job_number, prepared_by, room_entries)
        st.success("✅ Entry saved successfully!")

