import os
import streamlit as st
import requests
import speech_recognition as sr
from gtts import gTTS
import pyaudio  # Ensures PyAudio is loaded
import sounddevice as sd  # Alternative audio handling
import numpy as np

# 🔹 Ensure PyAudio is installed
try:
    import pyaudio
except ImportError:
    os.system("pip install --no-cache-dir pyaudio")
    import pyaudio

# 🔹 Together AI API Key
TOGETHER_AI_KEY = "a05bd3c0021a25d190d8906e8eb724eb7119a045484cf3852bcb082f3419802b"
TOGETHER_AI_URL = "https://api.together.xyz/v1/chat/completions"
MODEL_NAME = "meta-llama/Llama-3.3-70B-Instruct-Turbo"

# Streamlit Page Configuration
st.set_page_config(page_title="AI Voice Bot", page_icon="🎤", layout="centered")

# UI Styling
st.markdown("""
    <style>
        .stButton>button { width: 100%; border-radius: 10px; padding: 12px; }
        .stAudio { background-color: #f8f9fa; border-radius: 10px; padding: 10px; }
        .title { text-align: center; font-size: 28px; font-weight: bold; }
    </style>
""", unsafe_allow_html=True)

st.markdown('<p class="title">🎙 AI Voice Chatbot (Together AI)</p>', unsafe_allow_html=True)
st.write("🔊 Speak to the AI and get a real-time response!")

recognizer = sr.Recognizer()

# 🎤 **Voice Recording & AI Response**
if st.button("🎤 Start Talking"):
    with sr.Microphone() as source:
        st.write("🎙 Listening...")
        try:
            audio = recognizer.listen(source, timeout=5)
            st.write("🔄 Processing Speech...")
            user_text = recognizer.recognize_google(audio)
            st.success(f"👤 You: {user_text}")

            # 📡 **API Request to Together AI**
            headers = {"Authorization": f"Bearer {TOGETHER_AI_KEY}", "Content-Type": "application/json"}
            payload = {
                "model": MODEL_NAME,
                "messages": [{"role": "system", "content": "You are a helpful AI assistant."},
                             {"role": "user", "content": user_text}]
            }

            response = requests.post(TOGETHER_AI_URL, json=payload, headers=headers)

            if response.status_code == 200:
                ai_response = response.json().get("choices", [{}])[0].get("message", {}).get("content", "⚠ No response from AI")
                st.success(f"🤖 AI: {ai_response}")

                # 🎶 **Convert AI Response to Speech**
                tts = gTTS(ai_response)
                response_audio = "response.mp3"
                tts.save(response_audio)

                # 🔊 **Play AI Response**
                st.audio(response_audio, format="audio/mp3")

            else:
                st.error(f"❌ API Error: {response.text}")

        except sr.UnknownValueError:
            st.error("😕 Sorry, I couldn't understand that.")
        except sr.RequestError:
            st.error("⚠ Speech recognition service error.")
        except Exception as e:
            st.error(f"🚨 Error: {e}")
