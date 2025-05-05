import os
import subprocess
from tempfile import NamedTemporaryFile
from tkinter import Tk, Label, Button, Entry, filedialog, Checkbutton, BooleanVar, Frame, Scale, HORIZONTAL
from moviepy.config import change_settings
from moviepy.editor import VideoFileClip, AudioFileClip, concatenate_videoclips
import moviepy.video.fx.all as vfx
from moviepy.video.fx.all import mirror_x, blackwhite, lum_contrast, invert_colors
from moviepy.video.compositing.CompositeVideoClip import CompositeVideoClip
from moviepy.video.VideoClip import ImageClip
from pydub import AudioSegment

# Configure FFmpeg path
change_settings({
    "FFMPEG_BINARY": os.path.join(
        os.getcwd(),
        "ffmpeg-static",
        "bin",
        "ffmpeg"
    )
})

def reverse_with_ffmpeg(input_path: str) -> str:
    """Reverse a video using FFmpeg"""
    tmp = NamedTemporaryFile(delete=False, suffix=".mp4")
    cmd = [
        "ffmpeg", "-y",
        "-i", input_path,
        "-vf", "reverse",
        "-af", "areverse",
        "-c:v", "libx264", "-preset", "fast", "-crf", "18",
        "-c:a", "aac",
        tmp.name
    ]
    subprocess.run(cmd, check=True)
    return tmp.name

class TikTokShortMaker:
    def __init__(self, master):
        self.master = master
        master.title("TikTok Short Video Maker")

        # Initialize variables
        self.dialog_path = None
        self.bgm_path = None
        self.video_paths = []
        self.light_leak_path = None
        self.reverse_var = BooleanVar()
        self.flip_var = BooleanVar()
        self.grayscale_var = BooleanVar()
        self.invert_var = BooleanVar()
        self.slow_motion_var = BooleanVar()
        self.fps = 30

        # UI Elements
        Label(master, text="1. Select Dialog Audio").pack()
        Button(master, text="Browse Dialog", command=self.load_dialog).pack()

        Label(master, text="2. Select Background Music (optional)").pack()
        Button(master, text="Browse BGM", command=self.load_bgm).pack()

        Label(master, text="3. Select Videos").pack()
        Button(master, text="Browse Videos", command=self.load_videos).pack()

        # Effects Frame
        effects_frame = Frame(master)
        effects_frame.pack(pady=10)
        Checkbutton(effects_frame, text="Reverse Video", variable=self.reverse_var).grid(row=0, column=0)
        Checkbutton(effects_frame, text="Flip Horizontal", variable=self.flip_var).grid(row=0, column=1)
        Checkbutton(effects_frame, text="Grayscale", variable=self.grayscale_var).grid(row=0, column=2)
        Checkbutton(effects_frame, text="Invert Colors", variable=self.invert_var).grid(row=0, column=3)
        Checkbutton(effects_frame, text="Slow Motion", variable=self.slow_motion_var).grid(row=1, column=0)

        Label(effects_frame, text="Slow Factor:").grid(row=1, column=1)
        self.slow_factor_entry = Entry(effects_frame, width=5)
        self.slow_factor_entry.insert(0, "2.0")
        self.slow_factor_entry.grid(row=1, column=2)

        # Brightness/Contrast Controls
        Label(effects_frame, text="Brightness").grid(row=2, column=0)
        self.brightness_scale = Scale(effects_frame, from_=-100, to=100, orient=HORIZONTAL, length=300)
        self.brightness_scale.set(0)
        self.brightness_scale.grid(row=2, column=1, columnspan=3)

        Label(effects_frame, text="Contrast").grid(row=3, column=0)
        self.contrast_scale = Scale(effects_frame, from_=-100, to=100, orient=HORIZONTAL, length=300)
        self.contrast_scale.set(0)
        self.contrast_scale.grid(row=3, column=1, columnspan=3)

        # FPS Controls
        fps_frame = Frame(master)
        fps_frame.pack(pady=5)
        Label(fps_frame, text="Output FPS:").pack(side="left")
        self.fps_entry = Entry(fps_frame, width=5)
        self.fps_entry.insert(0, "30")
        self.fps_entry.pack(side="left")

        # Additional Options
        Button(master, text="Load Light Leak Image (optional)", command=self.load_light_leak).pack(pady=5)
        Button(master, text="Create TikTok Video", command=self.create_video).pack(pady=20)

    def load_dialog(self):
        self.dialog_path = filedialog.askopenfilename(filetypes=[("Audio Files", "*.mp3 *.wav")])

    def load_bgm(self):
        self.bgm_path = filedialog.askopenfilename(filetypes=[("Audio Files", "*.mp3 *.wav")])

    def load_videos(self):
        self.video_paths = list(filedialog.askopenfilenames(filetypes=[("Video Files", "*.mp4 *.mov *.avi")]))

    def load_light_leak(self):
        self.light_leak_path = filedialog.askopenfilename(filetypes=[("Image Files", "*.png *.jpg *.jpeg")])

    def apply_slow_motion(self, clip):
        try:
            factor = float(self.slow_factor_entry.get())
            if factor <= 1.0:
                factor = 2.0
        except ValueError:
            factor = 2.0
        return clip.fx(vfx.speedx, 1/factor)

    def process_videos(self, paths, dialog_duration):
        if not paths:
            return None

        processed_clips = []
        
        # Process each video with effects
        for path in paths:
            original_path = path
            if self.reverse_var.get():
                try:
                    path = reverse_with_ffmpeg(path)
                except subprocess.CalledProcessError:
                    path = original_path

            clip = VideoFileClip(path)

            # Apply all selected effects
            if self.slow_motion_var.get():
                clip = self.apply_slow_motion(clip)
            if self.flip_var.get():
                clip = mirror_x(clip)
            if self.grayscale_var.get():
                clip = blackwhite(clip)
            if self.invert_var.get():
                clip = invert_colors(clip)
            if self.brightness_scale.get() or self.contrast_scale.get():
                clip = lum_contrast(
                    clip,
                    lum=self.brightness_scale.get(),
                    contrast=self.contrast_scale.get(),
                    contrast_thr=128
                )
            if self.light_leak_path:
                leak = ImageClip(self.light_leak_path).set_duration(clip.duration).resize(clip.size).set_opacity(0.3)
                clip = CompositeVideoClip([clip, leak])

            # Standardize video format (TikTok vertical format)
            clip = clip.resize(height=1920)
            if clip.w < 1080:
                pad = (1080 - clip.w) // 2
                clip = clip.margin(left=pad, right=pad, color=(0, 0, 0))

            processed_clips.append(clip)

        # Combine all processed clips
        if not processed_clips:
            return None

        final_clip = concatenate_videoclips(processed_clips)

        # Adjust duration to match dialog
        if final_clip.duration < dialog_duration:
            # Loop the entire concatenated sequence
            final_clip = final_clip.loop(duration=dialog_duration)
        elif final_clip.duration > dialog_duration:
            # Trim to dialog length
            final_clip = final_clip.subclip(0, dialog_duration)

        return final_clip

    def create_video(self):
        if not self.dialog_path or not self.video_paths:
            print("Error: Please select both dialog audio and at least one video!")
            return

        try:
            self.fps = int(self.fps_entry.get())
            if not (1 <= self.fps <= 120):
                raise ValueError
        except ValueError:
            print("Invalid FPS value. Using default 30 FPS")
            self.fps = 30

        # Load and measure dialog duration
        dialog = AudioSegment.from_file(self.dialog_path)
        dialog_duration = len(dialog) / 1000  # Convert ms to seconds

        # Process videos
        video_clip = self.process_videos(self.video_paths, dialog_duration)
        if not video_clip:
            print("Error: No valid video clips were processed!")
            return

        # Mix audio
        if self.bgm_path:
            bgm = AudioSegment.from_file(self.bgm_path)
            combined_audio = dialog.overlay(bgm - 10)  # Reduce BGM volume by 10dB
        else:
            combined_audio = dialog

        # Export final video
        with NamedTemporaryFile(delete=False, suffix=".wav") as temp_audio:
            combined_audio.export(temp_audio.name, format="wav")
            audio_clip = AudioFileClip(temp_audio.name)
            final = video_clip.set_audio(audio_clip)
            final.write_videofile(
                "output_tiktok.mp4",
                fps=self.fps,
                codec="libx264",
                audio_codec="aac",
                threads=4  # Use multiple threads for faster encoding
            )

        print("Video created successfully: output_tiktok.mp4")

if __name__ == "__main__":
    root = Tk()
    app = TikTokShortMaker(root)
    root.mainloop()
