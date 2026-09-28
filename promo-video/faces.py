# Detect the face in every frame of a video (for vertical reframing + A/V sync checks).
# Usage: faces.py <video> <out.json> [width height]   (decodes at 25 fps, scaled for speed)
import sys, json, subprocess, numpy as np, cv2

src, out = sys.argv[1], sys.argv[2]
W, H = (int(sys.argv[3]), int(sys.argv[4])) if len(sys.argv) > 4 else (960, 540)
casc = cv2.CascadeClassifier(cv2.data.haarcascades + "haarcascade_frontalface_default.xml")
assert not casc.empty(), "cascade missing"
p = subprocess.Popen(["ffmpeg", "-v", "error", "-i", src, "-vf", f"fps=25,scale={W}:{H}", "-f", "rawvideo",
                      "-pix_fmt", "gray", "-"], stdout=subprocess.PIPE)
res, i = [], 0
prev = None
while True:
    b = p.stdout.read(W * H)
    if len(b) < W * H: break
    g = np.frombuffer(b, np.uint8).reshape(H, W)
    faces = casc.detectMultiScale(g, 1.12, 6, minSize=(W // 16, W // 16))
    box = None
    if len(faces):
        # keep the largest face; prefer continuity with the previous box
        faces = sorted(faces, key=lambda f: -f[2] * f[3])
        box = [int(v) for v in faces[0]]
    res.append(box)
    i += 1
json.dump({"w": W, "h": H, "boxes": res}, open(out, "w"))
print("frames", i, "with face", sum(b is not None for b in res))
