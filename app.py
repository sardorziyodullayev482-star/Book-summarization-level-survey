import json
import streamlit as st
from datetime import datetime
import os


version_float = 1.1

# ------------------------------------------ QUESTIONS -----------------------------------------------

def taking_out_questions(filename):
    base_directory = os.path.dirname(os.path.abspath(__file__))
    filepath = os.path.join(base_directory, filename)
    with open(filepath, "r") as file:
        reader = json.load(file)
        return reader

questions = list(taking_out_questions("survey_questions.json"))

psychological_states = {
    "Excellent Summarizing skills": (0, 10),
    "Moderate Summarizing skills and well retention of key details": (11, 20),
    "Basic key point retention skills ": (21, 30),
    "Low level of reading summarization and comprehension": (31, 40),
    "Very low level of reading summarization and comprehension": (41, 50),
    "Critical lack of summarization and key point understanding": (51,60)

}


# ------------------------------------------ FUNCTIONS -----------------------------------------------

def check_name(name: str) -> bool:
    if len(name.strip()) == 0:
        return False
    index = 0
    while index < len(name):
        character = name[index]
        allowed_characters = ({"-", " ", "'"})
        if not (character in allowed_characters or character.isalpha()):
            return False
        index += 1
    return True
def check_date_of_birth(date_of_birth: str) -> bool:
    allowed_date = ("%d-%m-%Y", "%Y-%m-%d")
    is_valid = False
    for time_format in allowed_date:
        try:
            datetime.strptime(date_of_birth, time_format)
            is_valid = True
        except ValueError:
            is_valid = is_valid
    return is_valid
def interpret_score(score: int) -> str:
    for state, (lower, upper) in psychological_states.items():
        if score in range(lower, upper+1):
            return state
    return "Unknown"

def save_as_json(filename: str, data_type: dict):
    with open(filename, "w", encoding="utf-8") as file:
        json.dump(data_type, file, indent=2)

def session_starting():
    name = st.text_input("Your first Name")
    surname = st.text_input("Your last Name")
    date_of_birth = st.text_input("Date of Birth (DD-MM-YYYY or YYYY-MM-DD)")
    studentid = st.text_input("Student ID (digits only)")
    if st.button("Run Survey"):
        st.session_state.survey_started = True
    if st.session_state.survey_started:
            survey_starting(name, surname, date_of_birth, studentid)
            if st.button("Start Again"):
                st.session_state.survey_started = False
                st.rerun()

def survey_starting(name, surname, date_of_birth, studentid):
        errors = set()
        if not check_name(name):
            errors.add("Invalid given name.")
        if not check_name(surname):
            errors.add("Invalid surname.")
        if not check_date_of_birth(date_of_birth):
            errors.add("Invalid date of birth format. Use DD-MM-YYYY.")
        if not studentid.isdigit():
            errors.add("Student ID must be digits only.")
        if errors:
            for e in errors:
                st.error(e)
        else:
            st.success("All inputs are valid. Proceed to answer the questions below.")

            total_score = 0
            answers = []


            for i in range(len(questions)):
                q = questions[i]
                option_labels = [option[0] for option in q["Options"]]
                variant = st.selectbox(f"Question {i + 1}. {q['Q']}", option_labels, key=f"Q{i}")
                position_of_option = option_labels.index(variant)
                score = q["Options"][position_of_option][1]
                total_score += score
                answers.append({
                    "question": q["Q"],
                    "chosen_variant": variant,
                    "score": score
                })

            status = interpret_score(total_score)

            st.markdown(f"## ✅ Your Result: {status}")
            st.markdown(f"**Total Score:** {total_score}")

            # Save results to JSON
            record = {
                "First_name": name,
                "Last_name": surname,
                "Date_of_birth": date_of_birth,
                "Student_id": studentid,
                "Total_score": total_score,
                "Result": status,
                "Answers": answers,
                "Version": version_float
            }

            json_filename = f"{studentid}_result.json"
            save_as_json(json_filename, record)

            st.success(f"Your results are saved as {json_filename}")
            st.download_button("Download your results JSON", json.dumps(record, indent=2), file_name=json_filename)



# ------------------------------------------ STREAMLIT APP DATA -----------------------------------------------
if "survey_started" not in st.session_state:
    st.session_state.survey_started = False
if "page" not in st.session_state:
    st.session_state.page = "menu"

# --- Name of the Survey ---
st.set_page_config(page_title="Book Chapter Summarizing and Key Point Mastery Scale")
st.title("📝 Book Chapter Summarizing and Key Point Mastery Scale")
st.info("Please fill out your details and answer all questions honestly.")

if st.session_state.page == "menu":
    st.subheader("What would you like to do?")
    column_1, column_2 = st.columns(2)
    with column_1:
        if st.button("🆕 Start a new survey"):
            st.session_state.page = "new_survey"
            st.rerun()

    with column_2:
        if st.button("📂 Load existing results"):
            st.session_state.page = "load_results"
            st.rerun()

elif st.session_state.page == "new_survey":
    session_starting()

elif st.session_state.page == "load_results":
    st.subheader("Load Existing Results")

    uploaded_file = st.file_uploader("Upload your results JSON", type="json")

    if uploaded_file is not None:
        data = json.load(uploaded_file)
        st.write("First Name: " ,data["First_name"])
        st.write("Last Name: ", data["Last_name"])
        st.write("Date of birth: ", data["Date_of_birth"])
        st.write("Student ID: ", data["Student_id"])
        st.write("Total_score: ", str(data["Total_score"]))
        st.write("Result: ", data["Result"])

    if st.button("Come back"):
        st.session_state.page = "menu"
        st.rerun()







