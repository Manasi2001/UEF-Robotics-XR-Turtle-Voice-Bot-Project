import streamlit as st
import extra_streamlit_components as stx

import sounddevice as sd
import wave

import joblib
import torch
import librosa
import soundfile
import torchaudio
import time
import numpy as np
import pandas as pd
from numpy.linalg import norm
from speechbrain.pretrained import EncoderClassifier
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
        with open("App/recordings/audio.wav", mode="rb") as wav:  

            response = Speech2Text.recognize(audio=wav, content_type="audio/wav")

            if len(response.result['results']) == 0:
                st.error('No words recognized.') 
                st.info("Refresh to try again.")

            else:
                df = pd.read_csv('App/speaker_embeddings.csv')
                signal, fs = soundfile.read('App/recordings/audio.wav')  ## switch to 'App/recordings/audio.wav'
                classifier = EncoderClassifier.from_hparams(source="speechbrain/spkrec-ecapa-voxceleb")
                signal_tensor = torch.from_numpy(signal[np.newaxis, :]).to(classifier.device)
                embedding = classifier.encode_batch(signal_tensor)
                df = df.reset_index(drop=True)
                cosine_sim = []
                test_audio_embedding = (embedding[0][0].numpy())
                for i in range(len(df)):
                    i_th_embedding = np.array(list(df.iloc[i,:-1]))
                    cosine_sim.append(np.dot(test_audio_embedding, i_th_embedding)/(norm(test_audio_embedding)*norm(i_th_embedding)))
                max_cosine_sim_value_index = cosine_sim.index(max(cosine_sim))
                speaker_pred = list(df.iloc[:,-1])[max_cosine_sim_value_index]
                st.write(speaker_pred)
                if speaker_pred == 'Manasi':
                    decoded_speaker = 'Manasi'
                else:
                    decoded_speaker = 'Others'
                    st.error('Unverified Speaker')
                    st.info("Refresh to try again.")

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