import streamlit as st
from io import BytesIO
from gtts import gTTS
from gensim.summarization import summarize
import sqlite3  # For database interaction
from dotenv import load_dotenv # For loading environment variables
from youtube_transcript_api import YouTubeTranscriptApi
import google.generativeai as genai
import pyperclip
import re

# Connect to the database
conn = sqlite3.connect("database.db")
c = conn.cursor()

# Configure GenAI with API key
genai.configure(api_key="Enter your API key here")  # Access API key from environment variable

# Constants and prompts
prompt = """You are a YouTube video summarizer. Please provide the summary of the text given here: """

def is_valid_email(email):
    """
    Check if the email format is valid.
    """
    email_regex = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(email_regex, email)


def text_to_speech(text, language='en'):
    """
    Converts text to speech and returns the raw audio data.
    """
    tts = gTTS(text=text, lang=language, slow=False)
    fp = BytesIO()
    tts.write_to_fp(fp)
    return fp.getvalue()


def generate_summary(text, ratio=0.2):
    """
    Generates a summary of the provided text.
    """
    try:
        summary = summarize(text, ratio=ratio)
        return summary
    except Exception as e:
        st.error(f"Error generating summary: {e}")
        return None


def extract_transcript_details(youtube_video_url):
    try:
        video_id = youtube_video_url.split("=")[1]
        transcript_text = YouTubeTranscriptApi.get_transcript(video_id)

        transcript = " ".join(segment["text"] for segment in transcript_text)
        return transcript
    except Exception as e:
        st.error(f"Error fetching transcript: {e}")
        return None


def generate_gemini_content(transcript_text, prompt):
    try:
        model = genai.GenerativeModel("gemini-pro")
        response = model.generate_content(prompt + transcript_text)
        return response.text
    except Exception as e:
        st.error(f"Error generating summary: {e}")
        return None


def login(email, password):
    if not email or not password:
        st.error("Please enter both email and password.")
        return False
    
    if not is_valid_email(email):
        st.error("Please enter a valid email address.")
        return False

    c.execute("SELECT * FROM users WHERE email = ? AND password = ?", (email, password))
    user_id = c.fetchone()
    if user_id:
        st.session_state["user_logged_in"] = True
        st.session_state["user_id"] = user_id[0]  # Store user ID in session state
        st.session_state["username"] = user_id[1]  # Store username in session state
        return True
    else:
        st.error("Incorrect email or password. Please try again.")
        return False


def register(username, email, password):
    if not username or not email or not password:
        st.error("Please fill in all fields.")
        return False, "Please fill in all fields."
        
    if not is_valid_email(email):
        st.error("Please enter a valid email address.")
        return False, "Invalid email address."

    c.execute("SELECT * FROM users WHERE email = ?", (email,))
    existing_user = c.fetchone()
    if existing_user:
        st.error("Email already exists. Please choose a different email.")
        return False, "Email already exists."
    else:
        c.execute("INSERT INTO users (username, email, password) VALUES (?, ?, ?)", (username, email, password))
        conn.commit()
        return True, "Registration successful. Please login."


def summarization():
    st.title("Summarization Page")
    st.write("Summarize your YouTube video below:")
    youtube_link = st.text_input("Enter the Youtube video link:")

    if youtube_link:
        video_id = youtube_link.split("=")[1]
        st.image(f"http://img.youtube.com/vi/{video_id}/0.jpg", use_column_width=1200)

    if st.button("**Summarize**"):
        transcript_text = extract_transcript_details(youtube_link)
        if transcript_text:
            summary = generate_gemini_content(transcript_text, prompt)
            st.subheader("Summary:")
            st.write(summary)
            st.session_state["summary_text"] = summary  # Store summary for potential audio generation
            
            # Text-to-speech conversion
            audio_data = text_to_speech(summary)
            st.audio(audio_data, format="audio/mp3")

            # Insert the summary into the database
            user_id = st.session_state["user_id"]  # Get user_id from session state
            c.execute("INSERT INTO summaries (user_id, video_url, summary) VALUES (?, ?, ?)",
                      (user_id, youtube_link, summary))  # Insert user_id into the query
            conn.commit()

            
        
        else:
            st.error("Error: Unable to fetch transcript. Please try again.")


def view_history():
    if st.session_state.get("user_logged_in"):
        user_id = st.session_state["user_id"]

        # Filter by date
        filter_date = st.date_input("Filter by date:")

        # Build SQL query based on search criteria
        query = "SELECT * FROM summaries WHERE user_id = ?"
        params = [user_id]

        if filter_date:
            query += " AND DATE(created_at) = ?"
            params.append(filter_date)

        query += " ORDER BY created_at DESC"

        # Execute SQL query
        c.execute(query, tuple(params))
        summaries = c.fetchall()

        if summaries:
            st.title("Your Summary History")
            for summary in summaries:
                st.subheader(f"Summary for: {summary[2]} (Created: {summary[4]})")
                st.image(f"http://img.youtube.com/vi/{summary[2].split('=')[1]}/0.jpg", use_column_width=True)
                st.write(summary[3])  # Display video URL and summary text
                if st.button(f"Copy Summary {summary[0]}"):
                    pyperclip.copy(summary[3])
                    st.success("Summary copied to clipboard!")
        else:
            st.subheader("No summaries found matching the criteria.")
    else:
        st.error("You must be logged in to view your summary history.")


def sign_out():
    st.session_state["user_logged_in"] = False
    st.session_state["user_id"] = None
    st.success("You have been successfully logged out.")


def main():
    # Create tables for users and summaries (if they don't exist)
    c.execute('''CREATE TABLE IF NOT EXISTS users (
                user_id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT NOT NULL,
                email TEXT UNIQUE NOT NULL,
                password TEXT NOT NULL
                )''')

    c.execute('''CREATE TABLE IF NOT EXISTS summaries (
              id INTEGER PRIMARY KEY AUTOINCREMENT,
              user_id INTEGER,
              video_url TEXT,
              summary TEXT,
              created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
              FOREIGN KEY (user_id) REFERENCES users(user_id)
            )''')

    # Login/Registration logic in sidebar
    with st.sidebar:
        if st.session_state.get("user_logged_in", False):
            st.write(f"Logged in as: {st.session_state['username']}")
            if st.button("`Sign Out`"):
                sign_out()
        else:
            choice = st.radio("Select an option:", ["Login", "Register" , "Summarize Text"])
            if choice == "Login":
                email = st.text_input("Email")
                password = st.text_input("Password", type="password")
                if st.button("`Login`"):
                    if login(email, password):
                        st.session_state["user_logged_in"] = True
                        st.session_state["email"] = email
                        st.success("Login successful!")
                        st.rerun()  # Rerun the app to display summarization section conditionally
                    else:
                        # Handle login failure (e.g., display error message)
                        pass  # Placeholder for error handling

            elif choice == "Register":
                new_username = st.text_input("Username")
                new_email = st.text_input("Email")
                new_password = st.text_input("Password", type="password")
                if st.button("`Register`"):
                    success, message = register(new_username, new_email, new_password)
                    if success:
                        st.success(message)
                    else:
                        st.error(message)

            elif choice == "Summarize Text":
                #st.write("Text Summarizer")
                text_input = st.text_area("Enter the text you want to summarize:",key="text_input2")
                ratio = st.slider("Select the ratio of summary to original text:", 0.1, 1.0, 0.5, 0.1,key="slider1")

                if st.button("**Enter**",key="button2"):
                    if text_input:
                        # Generate summary
                        summary_text = generate_summary(text_input, ratio)
                        if summary_text:
                            # Convert summary to speech
                            audio_data = text_to_speech(summary_text)
                            st.audio(audio_data, format="audio/mp3")
                            # Display summary
                            st.subheader("Summary:")
                            st.write(summary_text)
                


    # Display summarization section only for logged-in users
    if st.session_state.get("user_logged_in", False):
        st.header("Welcome back!")
        st.write("Choose an option below:")
        selected_option = st.radio("", ["Summarize a YouTube Video", "View Summary History"])
        if selected_option == "Summarize a YouTube Video":
            summarization()
        elif selected_option == "View Summary History":
            view_history()
    else:
        st.markdown("# YouTube Summarizer")
        st.image("/Users/anandapadmanabhan/Downloads/logo.svg", width=100)

        st.write("")
        
        st.markdown("## AI Summary for Long Videos,&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp; &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp; Articles & Text")
        st.write("###### Instantly summarize lengthy videos, articles and texts in seconds with YouTube Summarizer for Free. Effortlessly  grasp complex content.")
        st.markdown("##### Please Login to Summarize YouTube Videos")
        st.write("")
        st.write("")
        st.write("")
        st.write("")
        st.write("")
        # st.write("")
        # st.write("")
        # st.write("")
        # st.write("")
        st.markdown("## Click to Summarize Articles & Texts")

        # Button to reveal the text input and summary feature (for text summarization)
        if st.button("**Summarize**"):
            st.session_state["show_summary"] = True

        # Display text input and summary feature when show_summary is True
        if st.session_state.get("show_summary", False):
            text_input = st.text_area("Enter the text you want to summarize:", key="text_input1")
            ratio = st.slider("Select the ratio of summary to original text:", 0.1, 1.0, 0.5, 0.1,key="slider2")

            if st.button("**Enter**",key="button1"):
                if text_input:
                    # Generate summary
                    summary = generate_summary(text_input, ratio)
                    if summary:
                        # Convert summary to speech
                        audio_data = text_to_speech(summary)
                        st.audio(audio_data, format="audio/mp3")
                        # Display summary
                        st.subheader("Summary:")
                        st.write(summary)
                    else:
                        st.error("Unable to generate summary. Please try again.")
    
                else:
                    st.error("Please enter some text to summarize.")
            

    # Close the database connection
    conn.close()


if __name__ == "__main__":
    main()

