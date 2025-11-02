import os

import instaloader
from PIL import Image
from flask import Flask, render_template, request, send_file
from pytubefix import YouTube
from rembg import remove

app = Flask(__name__)
API_KEY = "07eb1e74-ed26-4bfa-8797-a730bee5b958"

@app.route("/")
def home():
    return render_template("index.html")

# --------- VIDEO DOWNLOAD ROUTE ----------
@app.route("/video", methods=["GET", "POST"])
def video():
    if request.method == "POST":
        yt_video_link = request.form["yt_v"]
        try:
            yt = YouTube(yt_video_link)
            stream = yt.streams.get_highest_resolution()
            file_path = stream.download()
            return send_file(file_path, as_attachment=True, download_name=f"{yt.title}.mp4")
        except Exception as e:
            return render_template("yt_video.html", message=f"❌ Error: {str(e)}")

    return render_template("yt_video.html", message="")
# --------- AUDIO DOWNLOAD ROUTE ----------
@app.route("/audio",methods=["GET", "POST"])
def audio():
    if request.method == "POST":
     yt_audio = request.form["yt_a"]
     try:
         yt_a = YouTube(yt_audio)
         yt_a = yt_a.streams.filter(only_audio=True).first()
         audio_file = yt_a.download()
         return send_file(audio_file,as_attachment=True,download_name=f"{yt_a.title}.mp4")
     except Exception as e:
         return render_template("y_audio.html", message=f"❌ Error: {str(e)}")
    
    return render_template("yt_audio.html",message="")
# --------- Instagram Reel Downloader ----------
@app.route("/reel", methods=["GET", "POST"])
def insta():
    if request.method == "POST":
        insta_url = request.form["insta_reel"]
        try:
            # Create Downloads/Instagram_Reels
            download_folder = os.path.join(os.path.expanduser("~"), "Downloads", "Instagram_Reels")
            os.makedirs(download_folder, exist_ok=True)

            # Extract shortcode
            shortcode = insta_url.split("/")[-2]

            # Setup Instaloader
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

            return render_template("reel.html", message="❌ Reel not found, maybe private?")

        except Exception as e:
            return render_template("reel.html", message=f"❌ Error: {str(e)}")

    return render_template("reel.html", message="")
# --------- Image Background Remover ----------
@app.route("/remove_bg", methods=["GET", "POST"])
def removeimg():
    if request.method == "POST":
     try:
      image = request.files["image"]       # Get uploaded file
      input_img = Image.open(image)
    
      output = remove(input_img)
    
      output_path = "BgRemovedimg.png"
      output.save(output_path)             # Save processed file

      return send_file(output_path, as_attachment=True)  # Return file
     except Exception:
      print("error")
    return render_template("bg-remove.html", message="")
 
import os

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
