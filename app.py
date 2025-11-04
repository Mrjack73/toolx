import os
from flask import Flask, render_template, request
from pytubefix import YouTube
from rembg import remove
from PIL import Image
import instaloader
import cloudinary
import cloudinary.uploader

# ---------- CONFIGURE CLOUDINARY ----------
cloudinary.config(
    cloud_name="Toolx",  # replace with your cloud name
    api_key="569951559739562",  # your API key
    api_secret="TPmd3JzmYyvyhgCgn0aCAPS0J74"  # your API secret
)

app = Flask(__name__)

# ---------- HOME ----------
@app.route("/")
def home():
    return render_template("index.html")

# ---------- YOUTUBE VIDEO DOWNLOAD ----------
@app.route("/video", methods=["GET", "POST"])
def video():
    if request.method == "POST":
        yt_video_link = request.form.get("yt_v")
        if not yt_video_link:
            return render_template("yt_video.html", message="❌ Please enter a YouTube link.")
        try:
            yt = YouTube(yt_video_link)
            stream = yt.streams.get_highest_resolution()
            temp_path = "/tmp"
            file_path = stream.download(output_path=temp_path)

            # Upload to Cloudinary
            upload_result = cloudinary.uploader.upload_large(
                file_path, resource_type="video", folder="toolx_videos"
            )
            cloud_url = upload_result["secure_url"]

            return render_template("yt_video.html", message="✅ Download ready!", link=cloud_url)

        except Exception as e:
            return render_template("yt_video.html", message=f"❌ Error: {str(e)}")

    return render_template("yt_video.html", message="")

# ---------- YOUTUBE AUDIO DOWNLOAD ----------
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

            # Upload to Cloudinary (audio treated as video resource)
            upload_result = cloudinary.uploader.upload_large(
                audio_file, resource_type="video", folder="toolx_audio"
            )
            cloud_url = upload_result["secure_url"]

            return render_template("yt_audio.html", message="✅ Audio ready!", link=cloud_url)
        except Exception as e:
            return render_template("yt_audio.html", message=f"❌ Error: {str(e)}")
    return render_template("yt_audio.html", message="")

# ---------- INSTAGRAM REEL DOWNLOAD ----------
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

            # Find and upload the reel
            for file in os.listdir(download_folder):
                if file.endswith(".mp4"):
                    file_path = os.path.join(download_folder, file)
                    upload_result = cloudinary.uploader.upload_large(
                        file_path, resource_type="video", folder="toolx_reels"
                    )
                    cloud_url = upload_result["secure_url"]
                    return render_template("reel.html", message="✅ Reel ready!", link=cloud_url)

            return render_template("reel.html", message="❌ Reel not found or private.")
        except Exception as e:
            return render_template("reel.html", message=f"❌ Error: {str(e)}")
    return render_template("reel.html", message="")

# ---------- IMAGE BACKGROUND REMOVER ----------
@app.route("/remove_bg", methods=["GET", "POST"])
def removeimg():
    if request.method == "POST":
        try:
            image = request.files["image"]
            input_img = Image.open(image)
            output = remove(input_img)

            output_path = "/tmp/BgRemovedimg.png"
            output.save(output_path)

            # Upload to Cloudinary (as image)
            upload_result = cloudinary.uploader.upload(
                output_path, resource_type="image", folder="toolx_removed_bg"
            )
            cloud_url = upload_result["secure_url"]

            return render_template("bg-remove.html", message="✅ Background removed!", link=cloud_url)
        except Exception as e:
            return render_template("bg-remove.html", message=f"❌ Error: {str(e)}")
    return render_template("bg-remove.html", message="")

# ---------- RUN APP ----------
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
