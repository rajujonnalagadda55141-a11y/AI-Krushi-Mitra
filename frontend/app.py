# app.py
import streamlit as st
import requests
import time
import html
import traceback

# Optional: server-side speech recognition (works when the server has microphone access)
# If you run Streamlit locally on the same machine and want mic recognition from server,
# uncomment the imports below and install pyaudio + SpeechRecognition:
#
# pip install SpeechRecognition pyaudio
#
# If you prefer browser mic (client-side), see notes below — that approach requires a custom component.

try:
    import speech_recognition as sr
    HAS_SR = True
except Exception:
    HAS_SR = False

# ----------------------------
# Helpers
# ----------------------------
BACKEND_URL = "http://localhost:8000/ask"  # change if your API is elsewhere

def ask_backend(question: str, timeout: int = 120):
    """Send question to backend and return (ok, answer_or_error_text, elapsed_seconds)."""
    if not question or not question.strip():
        return False, "Empty question", 0.0
    try:
        start = time.time()
        resp = requests.post(BACKEND_URL, json={"question": question}, timeout=timeout)
        elapsed = time.time() - start
        if resp.status_code != 200:
            # return body for debugging
            return False, f"Backend returned {resp.status_code}: {resp.text}", elapsed
        data = resp.json()
        answer = data.get("answer", "")
        return True, answer, elapsed
    except requests.exceptions.RequestException as e:
        return False, f"Connection error: {e}", 0.0
    except Exception as e:
        return False, f"Unexpected error: {e}\n{traceback.format_exc()}", 0.0

def recognize_speech_server(timeout=5, phrase_time_limit=8):
    """Server-side microphone capture using SpeechRecognition.
    Works only if the server process has access to a microphone (local dev).
    """
    if not HAS_SR:
        return None, "SpeechRecognition not installed on server."
    r = sr.Recognizer()
    try:
        with sr.Microphone() as source:
            r.adjust_for_ambient_noise(source, duration=0.5)
            audio = r.listen(source, timeout=timeout, phrase_time_limit=phrase_time_limit)
        try:
            text = r.recognize_google(audio)
            return text, None
        except sr.UnknownValueError:
            return None, "Could not understand speech."
        except sr.RequestError as e:
            return None, f"Speech recognition request error: {e}"
    except Exception as e:
        return None, f"Microphone error: {e}"

# ----------------------------
# Streamlit UI
# ----------------------------
st.set_page_config(page_title="AI Krushi Mitra", page_icon="🌾", layout="centered")
st.title("🌾 AI Krushi Mitra")
st.write("Simple farming advice for Indian farmers")
st.info("Ask in Telugu, Hindi, or English. Type your question and press Get Advice (or use Speak).")

# Initialize session state
if "last_answer" not in st.session_state:
    st.session_state.last_answer = ""
if "last_question" not in st.session_state:
    st.session_state.last_question = ""
if "status_msg" not in st.session_state:
    st.session_state.status_msg = ""

# Input area (text)
question = st.text_area("Ask your farming question:", value="", placeholder="Example: My cotton leaves are turning yellow")

col1, col2, col3 = st.columns([1, 1, 1])

# Button: Submit typed question
with col1:
    if st.button("Get Advice"):
        st.session_state.status_msg = ""
        if not question.strip():
            st.warning("Please enter your question before asking.")
        else:
            st.session_state.last_question = question
            with st.spinner("🤖 AI Krushi Mitra is thinking..."):
                ok, resp_text, elapsed = ask_backend(question)
                if not ok:
                    st.error("Error getting advice.")
                    st.code(resp_text)
                else:
                    st.success("🌾 Advice:")
                    st.write(resp_text)
                    st.caption(f"Response time: {round(elapsed, 2)} seconds")
                    st.session_state.last_answer = resp_text

# Button: Server-side speech (only use if your server has mic access)
with col2:
    if st.button("Speak Question (server mic)"):
        st.session_state.status_msg = "Listening..."
        st.info(st.session_state.status_msg)
        text, err = recognize_speech_server()
        if err:
            st.warning(err)
        else:
            st.session_state.last_question = text
            st.write("Recognized:", text)
            with st.spinner("🤖 AI Krushi Mitra is thinking..."):
                ok, resp_text, elapsed = ask_backend(text)
                if not ok:
                    st.error("Error getting advice.")
                    st.code(resp_text)
                else:
                    st.success("🌾 Advice:")
                    st.write(resp_text)
                    st.caption(f"Response time: {round(elapsed, 2)} seconds")
                    st.session_state.last_answer = resp_text

# Button: Read last answer (browser TTS)
with col3:
    if st.button("Read Last Answer (browser)"):
        if not st.session_state.last_answer:
            st.warning("No answer available to read.")
        else:
            safe_text = html.escape(st.session_state.last_answer).replace("\n", "\\n")
            tts_html = f"""
            <div>
              <button onclick="const u = new SpeechSynthesisUtterance(`{safe_text}`); u.rate=0.95; speechSynthesis.speak(u);">🔊 Play Answer</button>
            </div>
            <script>
              // automatically click the button so it plays immediately (optional)
              // document.querySelector('button').click();
            </script>
            """
            st.components.v1.html(tts_html, height=60)

# Show last answer below (persisted in session state)
if st.session_state.last_answer:
    st.subheader("Last Answer")
    st.write(st.session_state.last_answer)

# Helpful note about alternative: client-side speech
st.markdown("---")
st.markdown("**Note:** If you want in-browser (client-side) speech recognition (microphone from user's browser), we can add a small JavaScript component that uses the Web Speech API and then sends the recognized text to the backend. That requires embedding custom HTML/JS via `st.components.v1.html` and is the recommended approach for production (server-side mic only works when server runs on same machine and has mic access).")

# Debug info (optional; remove in production)
if st.checkbox("Show debug info"):
    st.write("Last question:", st.session_state.get("last_question", ""))
    st.write("Last answer length:", len(st.session_state.get("last_answer", "")))
    st.write("Has SpeechRecognition lib on server:", HAS_SR)
