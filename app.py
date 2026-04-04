import customtkinter as ctk
import threading
import time
import cv2
import mediapipe as mp
import pystray
from PIL import Image
from datetime import datetime
from database import save_record

# ---------------- GLOBAL ----------------
running = False

total_time = 0
good_time = 0
bad_time = 0

bad_start = None
good_start = None

# ---------------- MEDIAPIPE ----------------
mp_pose = mp.solutions.pose
mp_drawing = mp.solutions.drawing_utils

pose = mp_pose.Pose()

# ---------------- FORMAT ----------------
def format_time(sec):
    return f"{int(sec//60)}m {int(sec%60)}s"

# ---------------- SYSTEM TRAY ----------------
def run_tray():
    image = Image.new('RGB', (64, 64), color='blue')

    def on_quit(icon, item):
        icon.stop()

    icon = pystray.Icon(
        "PostureAI",
        image,
        menu=pystray.Menu(
            pystray.MenuItem("Quit", on_quit)
        )
    )

    icon.run()

# ---------------- CAMERA ----------------
def run_camera():
    global total_time, good_time, bad_time
    global bad_start, good_start, running

    cap = cv2.VideoCapture(0)
    start_time = time.time()

    while running:
        ret, frame = cap.read()
        if not ret:
            break

        frame = cv2.flip(frame, 1)

        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = pose.process(rgb)

        is_bad = False

        if results.pose_landmarks:
            lm = results.pose_landmarks.landmark
            diff = abs(lm[11].y - lm[12].y)

            if diff > 0.03:
                is_bad = True
                status = "Bad Posture ❌"
                color = (0,0,255)
            else:
                status = "Good Posture ✅"
                color = (0,255,0)
        else:
            is_bad = True
            status = "No Person 🚫"
            color = (0,0,255)

        # -------- TIME --------
        if is_bad:
            if bad_start is None:
                bad_start = time.time()

            if good_start is not None:
                good_time += time.time() - good_start
                good_start = None
        else:
            if good_start is None:
                good_start = time.time()

            if bad_start is not None:
                bad_time += time.time() - bad_start
                bad_start = None

        total_time = time.time() - start_time

        # -------- DRAW LANDMARKS 🔥 --------
        if results.pose_landmarks:
            mp_drawing.draw_landmarks(
                frame,
                results.pose_landmarks,
                mp_pose.POSE_CONNECTIONS,
                mp_drawing.DrawingSpec(color=(0,255,0), thickness=2),
                mp_drawing.DrawingSpec(color=(0,0,255), thickness=2)
            )

        # -------- TEXT DISPLAY --------
        cv2.putText(frame, status, (30,50),
                    cv2.FONT_HERSHEY_SIMPLEX, 1, color, 3)

        cv2.putText(frame, f"Total: {format_time(total_time)}", (30,100),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255,255,255), 2)

        cv2.putText(frame, f"Good: {format_time(good_time)}", (30,130),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0,255,0), 2)

        cv2.putText(frame, f"Bad: {format_time(bad_time)}", (30,160),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0,0,255), 2)

        update_ui()

        cv2.imshow("Posture AI Camera", frame)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()

# ---------------- UI FUNCTIONS ----------------
def start_tracking():
    global running
    running = True

    threading.Thread(target=run_camera).start()
    threading.Thread(target=run_tray).start()

def stop_tracking():
    global running
    running = False

    date = datetime.now().strftime("%Y-%m-%d %H:%M")

    save_record(
        date,
        format_time(total_time),
        format_time(good_time),
        format_time(bad_time)
    )

    status_label.configure(text="Saved to DB ✅")

def update_ui():
    total_label.configure(text=f"Total: {format_time(total_time)}")
    good_label.configure(text=f"Good: {format_time(good_time)}")
    bad_label.configure(text=f"Bad: {format_time(bad_time)}")

# ---------------- UI ----------------
ctk.set_appearance_mode("dark")

app = ctk.CTk()
app.geometry("400x400")
app.title("Posture AI")

title = ctk.CTkLabel(app, text="Posture AI Dashboard", font=("Arial", 20))
title.pack(pady=20)

total_label = ctk.CTkLabel(app, text="Total: 0m 0s")
total_label.pack()

good_label = ctk.CTkLabel(app, text="Good: 0m 0s")
good_label.pack()

bad_label = ctk.CTkLabel(app, text="Bad: 0m 0s")
bad_label.pack()

status_label = ctk.CTkLabel(app, text="")
status_label.pack(pady=10)

start_btn = ctk.CTkButton(app, text="Start", command=start_tracking)
start_btn.pack(pady=10)

stop_btn = ctk.CTkButton(app, text="Stop", command=stop_tracking)
stop_btn.pack(pady=10)

app.mainloop()