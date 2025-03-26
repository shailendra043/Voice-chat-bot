import os
import streamlit as st
import requests
import speech_recognition as sr
from gtts import gTTS


# Together AI API Config
TOGETHER_AI_KEY = "45513378158001858488262601131d87a8c2feceb5e7a7938525c3892f864958"
TOGETHER_AI_URL = "https://api.together.xyz/v1/chat/completions"
MODEL_NAME = "meta-llama/Llama-3.3-70B-Instruct-Turbo"

st.set_page_config(page_title="AI Voice Bot", page_icon="🎤")

st.title("🎙 AI Voice Chatbot")

recognizer = sr.Recognizer()

if st.button("🎤 Start Talking"):
    with sr.Microphone() as source:
        st.write("Listening...")
        try:
            audio = recognizer.listen(source, timeout=5)
            user_text = recognizer.recognize_google(audio)
            st.success(f"👤 You: {user_text}")

            headers = {"Authorization": f"Bearer {TOGETHER_AI_KEY}", "Content-Type": "application/json"}
            payload = {
                "model": MODEL_NAME,
                "messages": [{"role": "user", "content": user_text}]
            }
            response = requests.post(TOGETHER_AI_URL, json=payload, headers=headers)

            if response.status_code == 200:
                ai_response = response.json()["choices"][0]["message"]["content"]
                st.success(f"🤖 AI: {ai_response}")

                tts = gTTS(ai_response)
                response_audio = "response.mp3"
                tts.save(response_audio)
                st.audio(response_audio)

            else:
                st.error(f"❌ API Error: {response.text}")

        except sr.UnknownValueError:
            st.error("Couldn't understand you.")
        except sr.RequestError:
            st.error("Speech recognition service error.")
