import cv2
import mediapipe as mp
import time
import numpy as np

# ---------------- SETUP ----------------
mp_pose = mp.solutions.pose
mp_face = mp.solutions.face_mesh
mp_drawing = mp.solutions.drawing_utils

cap = cv2.VideoCapture(0)

# ---------------- TIME ----------------
start_time = time.time()
bad_time = 0
good_time = 0

bad_start = None
good_start = None
sleep_start = None

# ---------------- EYE ----------------
LEFT_EYE = [33, 160, 158, 133, 153, 144]

def eye_ratio(landmarks, eye):
    p1 = np.array([landmarks[eye[1]].x, landmarks[eye[1]].y])
    p2 = np.array([landmarks[eye[5]].x, landmarks[eye[5]].y])
    p3 = np.array([landmarks[eye[2]].x, landmarks[eye[2]].y])
    p4 = np.array([landmarks[eye[4]].x, landmarks[eye[4]].y])
    p5 = np.array([landmarks[eye[0]].x, landmarks[eye[0]].y])
    p6 = np.array([landmarks[eye[3]].x, landmarks[eye[3]].y])

    v1 = np.linalg.norm(p1 - p2)
    v2 = np.linalg.norm(p3 - p4)
    h = np.linalg.norm(p5 - p6)

    return (v1 + v2) / (2.0 * h)

def format_time(sec):
    return f"{int(sec//60)}m {int(sec%60)}s"

# ---------------- MAIN ----------------
with mp_pose.Pose(0.5,0.5) as pose, mp_face.FaceMesh(0.5,0.5) as face:
    
    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break

        frame = cv2.flip(frame,1)
        frame = cv2.resize(frame, (640,480))

        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

        pose_res = pose.process(rgb)
        face_res = face.process(rgb)

        status = "No Detection ❌"
        color = (255,255,255)

        is_bad = False

        # -------- POSTURE --------
        if pose_res.pose_landmarks:
            lm = pose_res.pose_landmarks.landmark
            diff = abs(lm[11].y - lm[12].y)

            cv2.putText(frame, f"Diff: {round(diff,3)}",
                        (30,40),
                        cv2.FONT_HERSHEY_SIMPLEX,0.7,(255,255,255),2)

            if diff > 0.03:
                is_bad = True
                status = "Bad Posture ❌"
            else:
                status = "Good Posture ✅"

        else:
            is_bad = True
            status = "No Person 🚫"

        # -------- EYE DETECTION (FIXED) --------
        if face_res.multi_face_landmarks:
            face_lm = face_res.multi_face_landmarks[0].landmark
            ear = eye_ratio(face_lm, LEFT_EYE)

            # show EAR for debugging
            cv2.putText(frame, f"EAR: {round(ear,2)}",
                        (30,260),
                        cv2.FONT_HERSHEY_SIMPLEX,0.7,(255,255,255),2)

            if ear < 0.25:  # 👈 tuned threshold

                if sleep_start is None:
                    sleep_start = time.time()

                elif time.time() - sleep_start > 3:  # 👈 3 sec rule
                    is_bad = True
                    status = "Sleeping 😴"

            else:
                sleep_start = None

        else:
            is_bad = True
            status = "Face Not Visible 🚫"

        # -------- TIME LOGIC --------
        if is_bad:
            color = (0,0,255)

            if bad_start is None:
                bad_start = time.time()

            if good_start is not None:
                good_time += time.time() - good_start
                good_start = None

        else:
            color = (0,255,0)

            if good_start is None:
                good_start = time.time()

            if bad_start is not None:
                bad_time += time.time() - bad_start
                bad_start = None

        total_time = time.time() - start_time

        # -------- DISPLAY --------
        cv2.putText(frame, status, (30,80),
                    cv2.FONT_HERSHEY_SIMPLEX,1,color,3)

        cv2.putText(frame, f"Total: {format_time(total_time)}", (30,130),
                    cv2.FONT_HERSHEY_SIMPLEX,0.7,(255,255,255),2)

        cv2.putText(frame, f"Good: {format_time(good_time)}", (30,160),
                    cv2.FONT_HERSHEY_SIMPLEX,0.7,(0,255,0),2)

        cv2.putText(frame, f"Bad: {format_time(bad_time)}", (30,190),
                    cv2.FONT_HERSHEY_SIMPLEX,0.7,(0,0,255),2)

        # draw skeleton
        if pose_res.pose_landmarks:
            mp_drawing.draw_landmarks(frame, pose_res.pose_landmarks, mp_pose.POSE_CONNECTIONS)

        cv2.imshow("Posture AI", frame)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

cap.release()
cv2.destroyAllWindows()