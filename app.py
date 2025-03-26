# app.py
import os
import streamlit as st
import requests
from gtts import gTTS
import speech_recognition as sr
from audio_recorder_streamlit import audio_recorder

# Together AI API Config
TOGETHER_AI_KEY = "45513378158001858488262601131d87a8c2feceb5e7a7938525c3892f864958"
TOGETHER_AI_URL = "https://api.together.xyz/v1/chat/completions"
MODEL_NAME = "meta-llama/Llama-3.3-70B-Instruct-Turbo"

st.set_page_config(page_title="AI Voice Bot", page_icon="🎤")
st.title("🎙 AI Voice Chatbot")

# Initialize speech recognizer
recognizer = sr.Recognizer()

# Audio recorder component
audio_bytes = audio_recorder(
    text="Click to start recording",
    recording_color="#e87070",
    neutral_color="#6aa36f",
    icon_name="user",
    icon_size="2x",
)

if audio_bytes:
    try:
        # Save audio to file
        with open("audio_input.wav", "wb") as f:
            f.write(audio_bytes)
        
        # Convert audio to text
        with sr.AudioFile("audio_input.wav") as source:
            audio_data = recognizer.record(source)
            user_text = recognizer.recognize_google(audio_data)
            st.success(f"👤 You: {user_text}")
            
            # Process with AI
            headers = {"Authorization": f"Bearer {TOGETHER_AI_KEY}", "Content-Type": "application/json"}
            payload = {
                "model": MODEL_NAME,
                "messages": [{"role": "user", "content": user_text}]
            }
            response = requests.post(TOGETHER_AI_URL, json=payload, headers=headers)

            if response.status_code == 200:
                ai_response = response.json()["choices"][0]["message"]["content"]
                st.success(f"🤖 AI: {ai_response}")

                # Convert response to audio
                tts = gTTS(ai_response, lang='en')
                response_audio = "response.mp3"
                tts.save(response_audio)
                st.audio(response_audio)
                
            else:
                st.error(f"❌ API Error: {response.text}")

    except sr.UnknownValueError:
        st.error("Couldn't understand audio")
    except sr.RequestError as e:
        st.error(f"Speech recognition error: {e}")
    except Exception as e:
        st.error(f"Error processing audio: {str(e)}")