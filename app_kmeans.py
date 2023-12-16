import streamlit as st
import extra_streamlit_components as stx

import sounddevice as sd
import wave

import joblib
import librosa
import time
import numpy as np
import pandas as pd
from ibm_watson import SpeechToTextV1
from ibm_cloud_sdk_core.authenticators import IAMAuthenticator

def init_router():
    return stx.Router({"/": home, "/manual_move": manual_move})

def record_audio(filename, duration=1):
    audio_data = sd.rec(int(44100 * duration), samplerate=44100, channels=1, dtype='int16')
    sd.wait()

    with wave.open(filename, 'wb') as wf:
        wf.setnchannels(1)
        wf.setsampwidth(2)
        wf.setframerate(44100)
        wf.writeframes(audio_data.tobytes())

def home():

    st.title("Turtlebot Navigator")

    if st.button("Give Command"):
        with st.spinner('Recording...'):
            file_name = "App/recordings/audio.wav"
            record_audio(file_name)
        st.write('Recording finished')
        st.audio(file_name, format="audio/wav")

        apiUrl = "https://api.eu-gb.speech-to-text.watson.cloud.ibm.com/instances/5f9e33da-3d8f-4924-9b18-2ef9c3dd288d"
        myKey = "7NwfZMJOeoVniUj5-XIFYclesdc0VjHzkPZPDBigsD8Y"

        auth = IAMAuthenticator(myKey)
        Speech2Text = SpeechToTextV1(authenticator = auth)
        Speech2Text.set_service_url(apiUrl)

        # Dataset/Manasi/rec_23_28_00.wav
        with open("App/recordings/audio.wav", mode="rb") as wav:  ## switch to 'App/recordings/audio.wav'

            response = Speech2Text.recognize(audio=wav, content_type="audio/wav")

            if len(response.result['results']) == 0:
                st.error('No words recognized.') 
                st.info("Refresh to try again.")

            else:
                header = []
                header.extend([f'mfcc{i}' for i in range(1, 21)])
                header.append('label')

                y,sr = librosa.load(file_name, mono=True, duration=1)
                mfcc = librosa.feature.mfcc(y=y, sr=sr)
                mean_mfcc = []
                for e in mfcc:
                    mean_mfcc.append(np.mean(e))

                df_test = pd.DataFrame(columns=header)
                df_test = pd.concat([df_test, pd.DataFrame([mean_mfcc], columns=header[:-1])])

                kmeans = joblib.load('Command Recognizer/speaker_identifier.pkl')

                speaker_pred = kmeans.predict(df_test[header[:-1]])

                if speaker_pred == 1:
                    decoded_speaker = 'Others'
                    st.error('Unverified Speaker')
                    st.info("Refresh to try again.")
                else:
                    decoded_speaker = 'Manasi'

                if decoded_speaker == 'Manasi':
                    st.success('Verified Speaker: Manasi')
                    recognized_text = response.result['results'][0]['alternatives'][0]['transcript']
                    confidence_score = str(round(response.result['results'][0]['alternatives'][0]['confidence'] * 100, 2)) 
                    flag = 0
                    # recognized_text = 'stop'  ## delete later
                    if 'right' in recognized_text or 'write' in recognized_text:
                        command = 'right'
                        flag = 1
                    elif 'go' in recognized_text:
                        command = 'go'
                        flag = 1
                    elif 'left' in recognized_text or 'l' in recognized_text:
                        command = 'left'
                        flag = 1
                    else:
                        st.error('Valid command not recognized.') 

                    if flag == 1:
                        with open('commands.txt', "a") as handler:
                            handler.write(command)
                            handler.write('\n')

                        st.success('Command recognized: '+ command)
                        st.success('Confidence score: ' + confidence_score +'%')

                        time.sleep(2)
                        st.info("Command Queued")
                    
                    else:
                        st.info("Refresh to try again.")

    if st.sidebar.button('Manual Maneuver'):
        return router.route('/manual_move')
    
def manual_move():
    st.title('Manual Maneuver')
    command = st.selectbox('Choose command: ', ('', 'go', 'left', 'right'))
    if st.button('Submit'):
        st.success('You chose: ' + str(command))
        time.sleep(2)
        st.info("Command Queued")
        with open('commands.txt', "a") as handler:
            handler.write(command)
            handler.write('\n')
    if st.sidebar.button('Give Command'):
        return router.route('/')

router = init_router()
router.show_route_view()