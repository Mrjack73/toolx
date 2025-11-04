import os
from flask import Flask, render_template, request, send_file
from pytubefix import YouTube
from rembg import remove
from PIL import Image
import instaloader

app = Flask(__name__)

# --------- HOME ----------
@app.route("/")
def home():
    return render_template("index.html")


# --------- YOUTUBE VIDEO DOWNLOAD ----------
@app.route("/video", methods=["GET", "POST"])
def video():
    if request.method == "POST":
        yt_video_link = request.form.get("yt_v")
        if not yt_video_link:
            return render_template("yt_video.html", message="❌ Please enter a YouTube link.")
        try:
            yt = YouTube(yt_video_link)
            stream = yt.streams.get_highest_resolution()
            temp_path = "/tmp"  # Render writable directory
            file_path = stream.download(output_path=temp_path)
            return send_file(file_path, as_attachment=True, download_name=f"{yt.title}.mp4")
        except Exception as e:
            return render_template("yt_video.html", message=f"❌ Error: {str(e)}")
    return render_template("yt_video.html", message="")


# --------- YOUTUBE AUDIO DOWNLOAD ----------
@app.route("/audio", methods=["GET", "POST"])
def audio():
    if request.method == "POST":
        yt_audio_link = request.form.get("yt_a")
        if not yt_audio_link:
            return render_template("yt_audio.html", message="❌ Please enter a YouTube link.")
        try:
            yt_audio = YouTube(yt_audio_link)
            audio_stream = yt_audio.streams.filter(only_audio=True).first()
            temp_path = "/tmp"
            audio_file = audio_stream.download(output_path=temp_path)
            return send_file(audio_file, as_attachment=True, download_name=f"{yt_audio.title}.mp3")
        except Exception as e:
            return render_template("yt_audio.html", message=f"❌ Error: {str(e)}")
    return render_template("yt_audio.html", message="")


# --------- INSTAGRAM REEL DOWNLOAD ----------
@app.route("/reel", methods=["GET", "POST"])
def insta():
    if request.method == "POST":
        insta_url = request.form.get("insta_reel")
        if not insta_url:
            return render_template("reel.html", message="❌ Please enter an Instagram reel link.")
        try:
            download_folder = "/tmp/Instagram_Reels"
            os.makedirs(download_folder, exist_ok=True)
            shortcode = insta_url.split("/")[-2]

            L = instaloader.Instaloader(
                dirname_pattern=download_folder,
                download_video_thumbnails=False,
                download_comments=False,
                save_metadata=False
            )
            post = instaloader.Post.from_shortcode(L.context, shortcode)
            L.download_post(post, target="Reel")

            for file in os.listdir(download_folder):
                if file.endswith(".mp4"):
                    file_path = os.path.join(download_folder, file)
                    return send_file(file_path, as_attachment=True, download_name="Reel.mp4")

            return render_template("reel.html", message="❌ Reel not found or private.")
        except Exception as e:
            return render_template("reel.html", message=f"❌ Error: {str(e)}")
    return render_template("reel.html", message="")


# --------- IMAGE BACKGROUND REMOVER ----------
@app.route("/remove_bg", methods=["GET", "POST"])
def removeimg():
    if request.method == "POST":
        try:
            image = request.files["image"]
            input_img = Image.open(image)
            output = remove(input_img)

            output_path = "/tmp/BgRemovedimg.png"
            output.save(output_path)
            return send_file(output_path, as_attachment=True)
        except Exception as e:
            return render_template("bg-remove.html", message=f"❌ Error: {str(e)}")
    return render_template("bg-remove.html", message="")


# --------- RUN APP ----------
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
