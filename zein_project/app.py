import streamlit as st
import pandas as pd
import numpy as np

# =====================================
# FILE SETUP
# =====================================
USERS_FILE = "users.csv"
MARKS_FILE = "marks.csv"

def load_users():
    try:
        return pd.read_csv(USERS_FILE)
    except:
        df = pd.DataFrame(columns=["username", "password", "role"])
        df.to_csv(USERS_FILE, index=False)
        return df

def load_marks():
    try:
        return pd.read_csv(MARKS_FILE)
    except:
        df = pd.DataFrame(columns=["student", "subject", "marks"])
        df.to_csv(MARKS_FILE, index=False)
        return df

users = load_users()
marks = load_marks()

# =====================================
# APP TITLE
# =====================================
st.title("📚 Zein School Management System")

# =====================================
# LOGIN
# =====================================
if "user" not in st.session_state:
    st.subheader("Login")
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")
    if st.button("Login"):
        match = users[(users.username == username) & (users.password == password)]
        if not match.empty:
            st.session_state.user = match.iloc[0].to_dict()
            st.rerun()
        else:
            st.error("Wrong username or password")
    st.stop()

user = st.session_state.user
role = user["role"]
st.sidebar.success(f"Logged in as {user['username']} ({role})")
if st.sidebar.button("Logout"):
    del st.session_state.user
    st.rerun()

# =====================================
# ADMIN PANEL
# =====================================
if role == "admin":
    st.header("🛠 Admin Panel")
    st.subheader("Add New User")
    new_username = st.text_input("Username")
    new_password = st.text_input("Password", type="password")
    new_role = st.selectbox("Role", ["admin", "teacher", "student"])

    if st.button("Create User"):
        if new_username.strip() == "" or new_password.strip() == "":
            st.error("Fields cannot be empty")
        elif new_username in users["username"].values:
            st.error("Username already exists")
        else:
            new_user = pd.DataFrame([{
                "username": new_username,
                "password": new_password,
                "role": new_role
            }])
            users = pd.concat([users, new_user], ignore_index=True)
            users.to_csv(USERS_FILE, index=False)
            st.success("User created successfully")
            st.rerun()
    st.subheader("All Users")
    st.dataframe(users)

# =====================================
# TEACHER PANEL - Editable Marks Table
# =====================================
elif role == "teacher":
    st.header("👩‍🏫 Teacher Panel")

    # Select student
    st.subheader("Select Student")
    student_list = users[users.role == "student"]["username"].tolist()
    selected_student = st.selectbox("Student", student_list)

    # Filter marks for selected student
    student_marks = marks[marks.student == selected_student].copy()

    # If no marks yet, initialize empty table
    if student_marks.empty:
        st.info("No marks yet. Add new subjects below.")
        student_marks = pd.DataFrame(columns=["student", "subject", "marks"])

    # Editable table
    st.subheader(f"Edit/Add Marks for {selected_student}")
    student_marks = st.data_editor(student_marks, num_rows="dynamic")

    # Ensure student column is always correct
    student_marks["student"] = selected_student

    if st.button("Save All Changes"):
        # Remove old student data
        marks = marks[marks.student != selected_student]
        # Append updated marks
        marks = pd.concat([marks, student_marks], ignore_index=True)
        marks.to_csv(MARKS_FILE, index=False)
        st.success(f"Marks for {selected_student} saved!")

    st.subheader("All Marks")
    st.dataframe(marks)

# =====================================
# STUDENT PANEL
# =====================================
elif role == "student":
    st.header("🎓 Student Dashboard")
    student_data = marks[marks.student == user["username"]]

    if student_data.empty:
        st.info("No marks available yet.")
    else:
        st.subheader("📊 Subject Performance")
        st.dataframe(student_data)
        st.bar_chart(student_data.set_index("subject")["marks"])
        avg = student_data["marks"].mean()
        st.write(f"### 📈 Current Average: {round(avg,2)}")

        weak_subjects = student_data[student_data["marks"] < 50]
        if not weak_subjects.empty:
            st.warning("Weak subjects detected:")
            for _, row in weak_subjects.iterrows():
                st.error(f"{row['subject']} — {row['marks']}")

        # Trend & prediction
        scores = student_data["marks"].values
        if len(scores) > 1:
            x = np.arange(len(scores))
            y = scores
            coeff = np.polyfit(x, y, 1)
            trend = np.poly1d(coeff)
            next_exam = trend(len(scores))
            st.subheader("🔮 Future Prediction")
            st.write(f"Predicted Next Average Score: **{round(next_exam,2)}**")
            if next_exam > avg:
                st.success("📈 Your performance trend is improving!")
            elif next_exam < avg:
                st.error("📉 Your performance trend is declining. Focus more!")
            else:
                st.info("➡ Your performance is stable.")

        st.subheader("🤖 Study Advice")
        for _, row in weak_subjects.iterrows():
            subject = row["subject"].lower()
            if subject == "math":
                advice = "• Practice daily problem solving\n• Focus on understanding formulas\n• Solve past exam questions"
            elif subject == "english":
                advice = "• Improve vocabulary daily\n• Practice reading comprehension\n• Write essays weekly"
            elif subject == "science":
                advice = "• Understand concepts\n• Watch experiment videos\n• Create summary notes"
            else:
                advice = "• Study regularly\n• Revise weak topics\n• Ask your teacher questions"
            st.info(f"{row['subject']} Advice:\n{advice}")

        if avg >= 80:
            st.success("🌟 Excellent performance! Keep pushing!")
        elif avg >= 50:
            st.info("👍 Good progress. Focus on weak subjects to improve.")
        else:
            st.error("📚 Significant improvement needed. Make a study plan and stay consistent.")
