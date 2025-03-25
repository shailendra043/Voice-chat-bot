import streamlit as st
import requests
import sounddevice as sd
import numpy as np
import wavio
import os
from gtts import gTTS

# Together AI API Key (Replace with your actual key)
TOGETHER_AI_KEY = "a05bd3c0021a25d190d8906e8eb724eb7119a045484cf3852bcb082f3419802b"
TOGETHER_AI_URL = "https://api.together.xyz/v1/chat/completions"

# ✅ Correct Model Name
MODEL_NAME = "meta-llama/Llama-3.3-70B-Instruct-Turbo"

# Streamlit Page Configuration
st.set_page_config(page_title="AI Voice Bot", page_icon="🎤", layout="centered")

# Custom CSS for UI Styling
st.markdown("""
    <style>
        .stButton>button {
            width: 100%;
            border-radius: 10px;
            padding: 12px;
            background-color: #007BFF;
            color: white;
            font-size: 18px;
            border: none;
            transition: 0.3s;
        }
        .stButton>button:hover {
            background-color: #0056b3;
        }
        .stAudio {
            background-color: #f8f9fa;
            border-radius: 10px;
            padding: 10px;
        }
        .stText {
            font-size: 20px;
            font-weight: bold;
            color: #333;
        }
        .title {
            text-align: center;
            font-size: 28px;
            font-weight: bold;
        }
    </style>
""", unsafe_allow_html=True)

st.markdown('<p class="title">🎙 AI Voice Chatbot (Together AI)</p>', unsafe_allow_html=True)
st.write("🔊 Speak to the AI and get a real-time response!")

# Audio Recording Parameters
SAMPLE_RATE = 44100  # 44.1 kHz
DURATION = 5  # 5 seconds

# 🎤 **Voice Recording & AI Response**
if st.button("🎤 Start Talking"):
    st.write("🎙 Recording for 5 seconds...")
    
    # Record audio
    recording = sd.rec(int(DURATION * SAMPLE_RATE), samplerate=SAMPLE_RATE, channels=1, dtype=np.int16)
    sd.wait()
    
    # Save audio as WAV file
    audio_file = "user_audio.wav"
    wavio.write(audio_file, recording, SAMPLE_RATE, sampwidth=2)
    
    st.write("🔄 Processing Speech...")
    
    # Convert speech to text (Google Speech Recognition via SpeechRecognition library)
    import speech_recognition as sr
    recognizer = sr.Recognizer()
    with sr.AudioFile(audio_file) as source:
        audio_data = recognizer.record(source)
        try:
            user_text = recognizer.recognize_google(audio_data)
            st.success(f"👤 You: {user_text}")

            # 📡 **API Request to Together AI**
            headers = {"Authorization": f"Bearer {TOGETHER_AI_KEY}", "Content-Type": "application/json"}
            payload = {
                "model": MODEL_NAME,  # ✅ Fixed Model Name
                "messages": [
                    {"role": "system", "content": "You are a helpful AI assistant."},
                    {"role": "user", "content": user_text}
                ]
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
