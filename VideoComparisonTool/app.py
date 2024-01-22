import tkinter as tk
from tkinter import ttk

import cv2
from PIL import Image, ImageTk


class VideoController:
    def __init__(self, video_source):
        self.cap = cv2.VideoCapture(video_source)
        self.video_source = video_source

        self.width, self.height = int(self.cap.get(3)), int(self.cap.get(4))

        self.is_playing = True
        self.scale_factor = 1.0
        self.photo = None

    def play(self):
        self.is_playing = True

    def pause(self):
        self.is_playing = False

    def forward(self, seconds):
        current_frame = self.cap.get(cv2.CAP_PROP_POS_FRAMES)
        fps = self.cap.get(cv2.CAP_PROP_FPS)
        new_frame = current_frame + fps * seconds
        self.cap.set(cv2.CAP_PROP_POS_FRAMES, new_frame)

    def backward(self, seconds):
        current_frame = self.cap.get(cv2.CAP_PROP_POS_FRAMES)
        fps = self.cap.get(cv2.CAP_PROP_FPS)
        new_frame = current_frame - fps * seconds
        self.cap.set(cv2.CAP_PROP_POS_FRAMES, new_frame)

    def update_display(self):
        ret, frame = self.cap.read()
        if ret:
            frame_resized = cv2.resize(frame, None, fx=self.scale_factor, fy=self.scale_factor)
            self.photo = self.convert_frame_to_image(frame_resized)
        else:
            self.is_playing = False
            self.cap.release()

    def convert_frame_to_image(self, frame):
        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        img = Image.fromarray(frame_rgb)
        return ImageTk.PhotoImage(img)

    def go_to_frame(self, frame_index):
        self.cap.set(cv2.CAP_PROP_POS_FRAMES, frame_index)
        self.update_display()


class VideoUI:
    def __init__(self, master, video_controller):
        self.master = master
        self.master.title("Video Comparison Tool")

        self.video_controller = video_controller

        self.canvas = tk.Canvas(
            self.master,
            width=self.video_controller.width,
            height=self.video_controller.height,
        )
        self.canvas.grid(row=0, column=0, columnspan=3)

        self.create_buttons()

        self.time_scale = None
        self.create_time_scale()

        self.zoom_in_zoom_out()

        self.frame_entry_label = None
        self.frame_entry = None
        self.btn_go_to_frame = None

        self.create_go_to_frame_layout()
        self.video_loop()

    def create_time_scale(self):
        self.time_scale = ttk.Scale(
            self.master,
            from_=0,
            to=100,
            orient=tk.HORIZONTAL,
            length=self.video_controller.width,
        )
        self.time_scale.place(x=0, y=self.video_controller.height - 200)
        self.time_scale.set(0)

    def zoom_in_zoom_out(self):
        self.master.bind("<Control-MouseWheel>", self.on_mousewheel)

    def create_buttons(self):
        btn_play = ttk.Button(self.master, text="Play", command=self.video_controller.play)
        btn_pause = ttk.Button(self.master, text="Pause", command=self.video_controller.pause)
        btn_forward = ttk.Button(
            self.master,
            text="Forward",
            command=lambda: self.video_controller.forward(2),
        )
        btn_backward = ttk.Button(
            self.master,
            text="Backward",
            command=lambda: self.video_controller.backward(2),
        )

        btn_play.place(x=860, y=900)
        btn_pause.place(x=960, y=900)
        btn_forward.place(x=760, y=900)
        btn_backward.place(x=660, y=900)

    def on_mousewheel(self, event):
        if self.video_controller.is_playing:
            self.video_controller.pause()
            self.master.after(500, self.video_controller.play)
        if event.delta > 0:
            self.video_controller.scale_factor *= 1.1
        else:
            self.video_controller.scale_factor /= 1.1
        self.update_video_display()

    def update_video_display(self):
        self.video_controller.update_display()
        self.canvas.create_image(0, 0, anchor=tk.NW, image=self.video_controller.photo)
        self.canvas.config(scrollregion=self.canvas.bbox(tk.ALL))
        self.time_scale.set(
            int(
                (
                    self.video_controller.cap.get(cv2.CAP_PROP_POS_FRAMES)
                    / self.video_controller.cap.get(cv2.CAP_PROP_FRAME_COUNT)
                )
                * 100
            )
        )

    def video_loop(self):
        if self.video_controller.is_playing:
            self.update_video_display()
            self.master.after(30, self.video_loop)
        else:
            self.master.after(100, self.video_loop)

    def create_go_to_frame_layout(self):
        self.frame_entry_label = ttk.Label(self.master, text="Go to Frame:")
        self.frame_entry_label.place(x=1060, y=900)

        self.frame_entry = ttk.Entry(self.master)
        self.frame_entry.place(x=1160, y=900)
        self.frame_entry.bind("<Return>", self.go_to_frame)

    def go_to_frame(self, event=None):
        try:
            frame_index = int(self.frame_entry.get())
            self.video_controller.go_to_frame(frame_index)
        except ValueError:
            print("Invalid frame index input.")


class VideoComparisonApp:
    def __init__(self, master, video_source="data/video.mp4"):
        self.video_controller = VideoController(video_source)
        self.video_player_ui = VideoUI(master, self.video_controller)


def main():
    root = tk.Tk()
    app = VideoComparisonApp(root, video_source="data/video.mp4")
    root.mainloop()


if __name__ == "__main__":
    main()
