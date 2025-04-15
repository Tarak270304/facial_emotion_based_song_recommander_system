import streamlit as st
from streamlit_webrtc import webrtc_streamer
import av
import cv2
import numpy as np
import mediapipe as mp
from keras.models import load_model
import webbrowser
import os

model = load_model("model.keras",compile=False)
label = np.load("labels.npy")

holistic = mp.solutions.holistic
hands = mp.solutions.hands
drawing = mp.solutions.drawing_utils

if "run" not in st.session_state:
    st.session_state["run"] = True

if os.path.exists("emotion.npy"):
    emotion = np.load("emotion.npy")[0]
else:
    emotion = ""

st.header("Emotion Based Music Recommender")

class EmotionProcessor:
    def recv(self, frame):
        frm = frame.to_ndarray(format="bgr24")
        frm = cv2.flip(frm, 1)
        res = holis.process(cv2.cvtColor(frm, cv2.COLOR_BGR2RGB))
        lst = []

        if res.face_landmarks:
            for i in res.face_landmarks.landmark:
                lst.append(i.x - res.face_landmarks.landmark[1].x)
                lst.append(i.y - res.face_landmarks.landmark[1].y)

            if res.left_hand_landmarks:
                for i in res.left_hand_landmarks.landmark:
                    lst.append(i.x - res.left_hand_landmarks.landmark[8].x)
                    lst.append(i.y - res.left_hand_landmarks.landmark[8].y)
            else:
                lst.extend([0.0] * 42)

            if res.right_hand_landmarks:
                for i in res.right_hand_landmarks.landmark:
                    lst.append(i.x - res.right_hand_landmarks.landmark[8].x)
                    lst.append(i.y - res.right_hand_landmarks.landmark[8].y)
            else:
                lst.extend([0.0] * 42)

            lst = np.array(lst).reshape(1, -1)
            pred = label[np.argmax(model.predict(lst, verbose=0))]
            np.save("emotion.npy", np.array([pred]))
            cv2.putText(frm, pred, (50, 50), cv2.FONT_ITALIC, 1, (255, 0, 0), 2)

        drawing.draw_landmarks(frm, res.face_landmarks, holistic.FACEMESH_TESSELATION)
        drawing.draw_landmarks(frm, res.left_hand_landmarks, hands.HAND_CONNECTIONS)
        drawing.draw_landmarks(frm, res.right_hand_landmarks, hands.HAND_CONNECTIONS)
        return av.VideoFrame.from_ndarray(frm, format="bgr24")

holis = holistic.Holistic()

lang = st.radio('Language', ('Telugu', 'Hindi', 'English'))
singer = st.text_input("Singer")

if lang and singer and st.session_state["run"]:
    webrtc_streamer(key="emotion", video_processor_factory=EmotionProcessor)

if st.button("Recommend me songs"):
    if not os.path.exists("emotion.npy"):
        st.warning("Please let me capture your emotion first")
        st.session_state["run"] = True
    else:
        emotion = np.load("emotion.npy")[0]
        webbrowser.open(f"https://www.youtube.com/results?search_query={lang}+{emotion}+song+{singer}")
        os.remove("emotion.npy")
        st.session_state["run"] = False
