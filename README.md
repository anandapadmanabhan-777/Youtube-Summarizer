<h1>YouTube Video Summarizer with Text-to-Speech</h1>

This is a web-based application built with Streamlit, which allows users to summarize YouTube videos and text content. The app extracts the transcript of a YouTube video, generates a summary using Generative AI (Gemini), and provides an audio version of the summary. Additionally, users can register, log in, view their history of summaries, and even summarize plain text.

<h3>Features</h3>

**YouTube Video Summarization:** Summarizes the transcript of YouTube videos.

**Text Summarization:** Summarizes entered text and provides an audio version.

**Text-to-Speech:** Converts the generated summaries to speech using gTTS.

**User Registration and Login:** Allows users to register, log in, and manage their summaries.

**Summary History:** Users can view and copy their previously generated summaries.


<h3>Technologies Used</h3>

**Python:** Programming language.

**Streamlit:** Framework for building the interactive web app.

**gTTS (Google Text-to-Speech):** Converts text summaries to speech.

**Gensim:** Summarization library for generating concise text summaries.

**YouTube Transcript API:** Fetches transcripts of YouTube videos.

**Google Gemini API:** For advanced AI-driven content generation.

**SQLite:** Database for storing user data and summaries.

**Pyperclip:** Allows users to copy summaries to the clipboard.

**dotenv:** For managing environment variables (e.g., API keys).

<h3>Prerequisites</h3>

Python 3.x
Install the required dependencies using pip:
pip install streamlit gtts gensim youtube-transcript-api google-generativeai pyperclip sqlite3 python-dotenv
Additional Configuration
Google Gemini API: Ensure you have access to Google Gemini and configure the API key.
Create a .env file in your project directory with the following content:
API_KEY=your_google_gemini_api_key
Usage

<h3>Run the Application:</h3>
Open a terminal, navigate to the project directory, and run the Streamlit app:
streamlit run app.py
Login/Registration:
Users can either log in with an existing account or register a new account.
After logging in, they can start summarizing YouTube videos or text content.
Summarize YouTube Videos:
Users can input a YouTube video URL.
The application will fetch the video transcript, generate a summary, and provide an audio version of the summary.
Summarize Text:
Users can input any text and get a summary based on the selected ratio.
The app will also provide an audio version of the summary.
View History:
Logged-in users can view a history of their past summaries.
The summary can be copied to the clipboard for easy access.
Database Schema

Users Table:
user_id: INTEGER (Primary Key)
username: TEXT
email: TEXT (Unique)
password: TEXT
Summaries Table:
id: INTEGER (Primary Key)
user_id: INTEGER (Foreign Key)
video_url: TEXT
summary: TEXT
created_at: DATETIME (Timestamp)
Example

Summarizing a YouTube Video:
Enter a valid YouTube video link.
The app fetches the video transcript and generates a summary.
The summary is displayed, and an audio version is provided for playback.

Text Summarization:
Enter the text you want to summarize.
Adjust the summary ratio using the slider.
The summary is displayed along with the audio version.

Viewing History:
Logged-in users can view all the summaries they have generated in the past.
Users can filter by date and copy any summary to the clipboard.

<h3>Contributing</h3>

Feel free to contribute to this project by forking the repository, making improvements, and submitting a pull request.

<h3>License</h3>

This project is licensed under the MIT License - see the LICENSE file for details.

