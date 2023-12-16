# UEF Robotics & XR Turtle"Voice"Bot

- Inspired by the advancements in voice-activated robots, the project addresses a critical need for personalized interaction. 

- In scenarios where a household robot responds to various speakers, this ideation ensures that only commands from verified sources, such as the homeowner, are acknowledged. 

- This not only enhances user privacy but also safeguards against unintended actions, encouraging a more secure and tailored human-robot interaction experience.

Given below is a brief description of the files:

### `Dataset` directory:

Consists of Manasi's (verified speaker) 30 voice recordings in the `Manasi` folder. Some test audios are present in the `Test` folder. `make_dataset.py` is the script for a Streamlit website where users can create their own dataset by recording their audios. They can then retrain the models to identify them as the verified speaker.

### `Robotics_&_XR_ECAPA_TDNN.ipynb`:

Google Colab where the ECAPA-TNN architecture was setup to extract embeddings from audios.

### `Robitics_&_XR_KMeans.ipynb`:

Google Colab where a basic KMeans clustering model was created to distinguish between speakers. Also shows the method for command extraction using the IBM Watson Speech-to-Text API.

### `app_ecapa.py`

Python script to make use of the ECAPA-TNN architecture like shown in the Google Colab `Robotics_&_XR_ECAPA_TDNN.ipynb` and integrate it with a Streamlit app. 

### `app_kmeans.py`

Python script that invokes the `speaker_identifier.pkl` model which is the KMeans algorithm based model to distinguish among speakers. Based on the Google Colab `Robitics_&_XR_KMeans.ipynb` and shows integration with the Streamlit app.

### `audio.wav`

The audio file which keeps on getting rewrited whenever a new audio is recorded.

### `commands.txt`

After successful speaker verification and speech-to-text, the valid commands are appended here.

### `obey_me.py`

ROS node that reads the `commands.txt` file, executes the commands sequentially and gives target coordinated to the robot.

### `speaker_embeddings.csv`

Dataset of embeddings from different speakers and Manasi's audios. Whenever a new audio is recorded (for the ECAPA-TDNN approach) and its embeddings are extracted, cosine similarity score is calculated between the new audio and all the audios in this dataset to find the best match.

### `speaker_identifier.pkl` 

KMeans clustering based 88.19% accurate (but recording device dependent) model.

<br><br>

** *It is important to note that in order to execute the files, some paths might to be change according to the file location.*
