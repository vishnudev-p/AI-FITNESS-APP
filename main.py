import cv2
from pose_estimation.estimation import PoseEstimator
from exercises.squat import Squat
from exercises.hammer_curl import HammerCurl
from exercises.push_up import PushUp
from feedback.layout import layout_indicators
from feedback.information import get_exercise_info
from utils.draw_text_with_background import draw_text_with_background
import tkinter as tk
from tkinter import messagebox, filedialog
import ttkbootstrap as tb
from ttkbootstrap.constants import *
import hashlib

class FitnessApp:
    def __init__(self, root):
        self.root = root
        self.root.title("AI Fitness App")
        self.root.geometry("296x430")  # Fixed window size
        self.root.resizable(False, False)  # Disable resizing
        self.theme_var = tk.BooleanVar(value=True)  # True for dark, False for light
        self.registered_users = {}  # Store registered users
        self.load_users()  # Load existing users

        # Create frames
        self.login_frame = self.create_login_frame()
        self.signup_frame = self.create_signup_frame()
        self.exercise_frame = self.create_exercise_frame()

        # Show login frame initially
        self.show_login()

    def create_login_frame(self):
        """Create the login frame."""
        frame = tk.Frame(self.root)

        tk.Label(frame, text="Login", font=("Arial", 18, "bold")).pack(pady=10)

        tk.Label(frame, text="Username:").pack(anchor="w", padx=20)
        self.login_username = tb.Entry(frame, bootstyle="primary")
        self.login_username.pack(fill="x", padx=20, pady=5)

        tk.Label(frame, text="Password:").pack(anchor="w", padx=20)
        self.login_password = tb.Entry(frame, bootstyle="primary", show="*")
        self.login_password.pack(fill="x", padx=20, pady=5)

        tb.Button(frame, text="Login", bootstyle="success", command=self.login).pack(pady=10)
        tb.Button(frame, text="Signup", bootstyle="link", command=self.show_signup).pack(pady=10)

        # Theme Toggle
        toggle_frame = tk.Frame(frame)
        toggle_frame.place(relx=1.0, y=10, anchor="ne")
        tb.Checkbutton(toggle_frame, variable=self.theme_var, onvalue=True, offvalue=False,
                       bootstyle="round-toggle", command=self.toggle_theme).pack(side="left")

        return frame

    def create_signup_frame(self):
        """Create the signup frame."""
        frame = tk.Frame(self.root)

        tk.Label(frame, text="Signup", font=("Arial", 18, "bold")).pack(pady=10)

        tk.Label(frame, text="Username:").pack(anchor="w", padx=20)
        self.signup_username = tb.Entry(frame, bootstyle="primary")
        self.signup_username.pack(fill="x", padx=20, pady=5)

        tk.Label(frame, text="Password:").pack(anchor="w", padx=20)
        self.signup_password = tb.Entry(frame, bootstyle="primary", show="*")
        self.signup_password.pack(fill="x", padx=20, pady=5)

        tk.Label(frame, text="Confirm Password:").pack(anchor="w", padx=20)
        self.signup_confirm_password = tb.Entry(frame, bootstyle="primary", show="*")
        self.signup_confirm_password.pack(fill="x", padx=20, pady=5)

        tb.Button(frame, text="Signup", bootstyle="success", command=self.signup).pack(pady=10)
        tb.Button(frame, text="Back", bootstyle="danger", command=self.show_login).pack(side="right", padx=10, pady=20)

        return frame

    def create_exercise_frame(self):
        """Create the exercise selection frame."""
        frame = tk.Frame(self.root)

        tk.Label(frame, text="Select Your Exercise", font=("Arial", 18, "bold")).pack(pady=10)

        tb.Button(frame, text="Push Up", bootstyle="success", command=lambda: self.open_exercise_interface("push_up")).pack(pady=5)
        tb.Button(frame, text="Hammer Curl", bootstyle="success", command=lambda: self.open_exercise_interface("hammer_curl")).pack(pady=5)
        tb.Button(frame, text="Squat", bootstyle="success", command=lambda: self.open_exercise_interface("squat")).pack(pady=5)

        # Back Button
        tb.Button(frame, text="Back", bootstyle="danger", command=self.show_login).pack(side="left", padx=10, pady=10)

        return frame

    def show_login(self):
        """Show the login frame."""
        self.signup_frame.pack_forget()
        self.exercise_frame.pack_forget()
        self.login_frame.pack(pady=20)

    def show_signup(self):
        """Show the signup frame."""
        self.login_frame.pack_forget()
        self.signup_frame.pack(pady=20)

    def show_exercise(self):
        """Show the exercise selection frame."""
        self.login_frame.pack_forget()
        self.signup_frame.pack_forget()
        self.exercise_frame.pack(pady=20)

    def signup(self):
        """Handle user signup."""
        username = self.signup_username.get().strip()
        password = self.signup_password.get().strip()
        confirm_password = self.signup_confirm_password.get().strip()

        if not username or not password or not confirm_password:
            messagebox.showerror("Error", "Please fill in all fields!")
        elif password != confirm_password:
            messagebox.showerror("Error", "Passwords do not match!")
        elif username in self.registered_users:
            messagebox.showerror("Error", "Username already exists!")
        else:
            self.registered_users[username] = self.hash_password(password)
            self.save_users()
            messagebox.showinfo("Success", "Account created successfully!")
            self.show_login()

    def login(self):
        """Handle user login."""
        username = self.login_username.get().strip()
        password = self.login_password.get().strip()

        if username in self.registered_users and self.check_password(password, self.registered_users[username]):
            messagebox.showinfo("Login Successful", "Welcome!")
            self.show_exercise()
        else:
            messagebox.showerror("Login Failed", "Invalid credentials!")

    def toggle_theme(self):
        """Toggle between dark and light themes."""
        if self.theme_var.get():
            self.root.style.theme_use("darkly")  # Dark Mode
        else:
            self.root.style.theme_use("flatly")  # Light Mode

    def hash_password(self, password):
        """Hash the password using SHA-256."""
        return hashlib.sha256(password.encode()).hexdigest()

    def check_password(self, password, hashed_password):
        """Check if the password matches the hashed password."""
        return self.hash_password(password) == hashed_password

    def load_users(self):
        """Load registered users from a file (for persistence)."""
        try:
            with open("users.txt", "r") as file:
                for line in file:
                    username, password = line.strip().split(",")
                    self.registered_users[username] = password
        except FileNotFoundError:
            pass

    def save_users(self):
        """Save registered users to a file."""
        with open("users.txt", "w") as file:
            for username, password in self.registered_users.items():
                file.write(f"{username},{password}\n")

    def open_exercise_interface(self, exercise_type):
        """Open the exercise interface."""
        new_window = tk.Toplevel()
        new_window.title(f"{exercise_type.replace('_', ' ').title()} Interface")
        new_window.geometry("296x430")  # Fixed window size
        new_window.resizable(False, False)  # Disable resizing

        tk.Label(new_window, text="Workout", font=('Helvetica', 16)).pack(pady=10)
        tb.Button(new_window, text="Real Time Workout", bootstyle="success", command=lambda: self.start_exercise(exercise_type, True)).pack(pady=5)
        tb.Button(new_window, text="Upload Video", bootstyle="primary", command=lambda: self.upload_video(exercise_type)).pack(pady=5)

    def upload_video(self, exercise_type):
        """Open a file dialog to upload a video."""
        file_path = filedialog.askopenfilename(
            title="Select a Video File",
            filetypes=[("Video Files", "*.mp4 *.avi *.mov *.mkv")]
        )
        if file_path:
            self.start_exercise(exercise_type, use_webcam=False, video_path=file_path)

    def start_exercise(self, exercise_type, use_webcam=True, video_path=None):
        """Start the exercise tracking."""
        if use_webcam:
            video_source = 0  # Webcam
        else:
            if not video_path:
                messagebox.showerror("Error", "No video file selected!")
                return
            video_source = video_path

        cap = cv2.VideoCapture(video_source)
        pose_estimator = PoseEstimator()

        if not cap.isOpened():
            messagebox.showerror("Error", "Camera or video file not found.")
            return

        if exercise_type == "hammer_curl":
            exercise = HammerCurl()
        elif exercise_type == "squat":
            exercise = Squat()
        elif exercise_type == "push_up":
            exercise = PushUp()
        else:
            messagebox.showerror("Error", "Invalid exercise type.")
            return

        exercise_info = get_exercise_info(exercise_type)

        while cap.isOpened():
            ret, frame = cap.read()
            if not ret:
                break

            results = pose_estimator.estimate_pose(frame, exercise_type)
            if results.pose_landmarks:
                if exercise_type == "squat":
                    counter, angle, stage = exercise.track_squat(results.pose_landmarks.landmark, frame)
                    layout_indicators(frame, exercise_type, (counter, angle, stage))
                elif exercise_type == "hammer_curl":
                    (counter_right, angle_right, counter_left, angle_left,
                     warning_message_right, warning_message_left, progress_right, progress_left, stage_right, stage_left) = exercise.track_hammer_curl(
                        results.pose_landmarks.landmark, frame)
                    layout_indicators(frame, exercise_type,
                                      (counter_right, angle_right, counter_left, angle_left,
                                       warning_message_right, warning_message_left, progress_right, progress_left, stage_right, stage_left))
                elif exercise_type == "push_up":
                    counter, angle, stage = exercise.track_push_up(results.pose_landmarks.landmark, frame)
                    layout_indicators(frame, exercise_type, (counter, angle, stage))

            draw_text_with_background(frame, f"Exercise: {exercise_info.get('name', 'N/A')}", (40, 50),
                                      cv2.FONT_HERSHEY_DUPLEX, 0.7, (255, 255, 255), (118, 29, 14, 0.79), 1)
            draw_text_with_background(frame, f"Reps: {exercise_info.get('reps', 0)}", (40, 80),
                                      cv2.FONT_HERSHEY_DUPLEX, 0.7, (255, 255, 255), (118, 29, 14, 0.79), 1)
            draw_text_with_background(frame, f"Sets: {exercise_info.get('sets', 0)}", (40, 110),
                                      cv2.FONT_HERSHEY_DUPLEX, 0.7, (255, 255, 255), (118, 29, 14, 0.79), 1)

            cv2.imshow(f"{exercise_type.replace('_', ' ').title()} Tracker", frame)

            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

        cap.release()
        cv2.destroyAllWindows()

    def run(self):
        """Run the application."""
        self.root.mainloop()

if __name__ == "__main__":
    root = tb.Window(themename="darkly")  # Use ttkbootstrap for styling
    app = FitnessApp(root)
    app.run()