import wave
import time
import streamlit as st
import sounddevice as sd
from datetime import datetime

def record_audio(filename, duration=1):
    audio_data = sd.rec(int(44100 * duration), samplerate=44100, channels=1, dtype='int16')
    sd.wait()

    with wave.open(filename, 'wb') as wf:
        wf.setnchannels(1)
        wf.setsampwidth(2)
        wf.setframerate(44100)
        wf.writeframes(audio_data.tobytes())

st.title('Dataset Creater')
speaker_name = st.text_input('Enter your name: ', value='Manasi')

if st.button('Go'):
    st.write("Recording...")
    current_time = datetime.now()
    file_name = 'Dataset/' + speaker_name.strip() + '/rec_' + str(current_time.strftime("%H_%M_%S")) + '.wav'
    record_audio(file_name)
    st.audio(file_name, format="audio/wav")
    st.success('Recording saved!')
    time.sleep(3)
    if st.button('Record Another'):
        st.experimental_rerun()