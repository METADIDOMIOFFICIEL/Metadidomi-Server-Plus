import os
import subprocess
from typing import List

def generate_video_thumbnails(video_path: str, output_dir: str, n_thumbnails: int = 5) -> List[str]:
    """
    Génère n_thumbnails images à intervalles réguliers pour une vidéo donnée.
    Retourne la liste des chemins des miniatures générées.
    """
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    # Récupère la durée de la vidéo
    cmd_duration = [
        'ffprobe', '-v', 'error', '-show_entries', 'format=duration',
        '-of', 'default=noprint_wrappers=1:nokey=1', video_path
    ]
    try:
        duration = float(subprocess.check_output(cmd_duration).decode().strip())
    except Exception:
        duration = 1200  # Valeur par défaut si erreur
    # Génère les miniatures
    thumbnails = []
    for i in range(n_thumbnails):
        t = int(duration * i / n_thumbnails)
        thumb_path = os.path.join(output_dir, f"{os.path.basename(video_path)}_{i}.jpg")
        cmd = [
            'ffmpeg', '-ss', str(t), '-i', video_path,
            '-frames:v', '1', '-q:v', '2', '-vf', 'scale=320:180', thumb_path,
            '-y'
        ]
        try:
            subprocess.run(cmd, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            thumbnails.append(thumb_path)
        except Exception:
            pass
    return thumbnails

if __name__ == "__main__":
    # Exemple d'utilisation
    video = r"web_uploads/Boruto Episode 215 Sub Indo - Samehadaku.mp4"
    output = r"app/static/thumbnails"
    thumbs = generate_video_thumbnails(video, output)
    print("Miniatures générées :", thumbs)
