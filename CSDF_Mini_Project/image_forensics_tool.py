#!/usr/bin/env python3
"""
image_forensics_tool.py

Simple Image Forensics Tool:
 - Hashes (md5, sha1, sha256)
 - EXIF extraction
 - Perceptual hashes (ahash, phash)
 - Histogram & stats
 - Error Level Analysis (ELA) image saved
 - Simple LSB/noise stego heuristic

Usage:
    python image_forensics_tool.py --input path/to/image_or_folder --out results_folder
"""

import os
import sys
import argparse
import hashlib
import csv
from PIL import Image, ImageChops, ImageEnhance, ExifTags
import piexif
import imagehash
import numpy as np
import cv2   # OpenCV, used only for optional display or further processing
import math
from collections import Counter
import json

# ---------- Utilities ----------

def compute_hashes(path):
    """Return dict with md5, sha1, sha256 for file at path."""
    h_md5 = hashlib.md5()
    h_sha1 = hashlib.sha1()
    h_sha256 = hashlib.sha256()
    with open(path, 'rb') as f:
        while True:
            chunk = f.read(8192)
            if not chunk:
                break
            h_md5.update(chunk)
            h_sha1.update(chunk)
            h_sha256.update(chunk)
    return {'md5': h_md5.hexdigest(), 'sha1': h_sha1.hexdigest(), 'sha256': h_sha256.hexdigest()}

def extract_exif(path):
    """Return a dict of selected EXIF tags (if any)."""
    try:
        exif_dict = piexif.load(path)
    except Exception:
        return {}
    out = {}
    # common tags: 0th/Exif/GPS
    def get_tag(ifd, tag_name):
        try:
            for k, v in ExifTags.TAGS.items():
                if v == tag_name:
                    return ifd.get(k)
        except Exception:
            return None
    # easier: parse known fields manually
    zeroth = exif_dict.get("0th", {})
    exif = exif_dict.get("Exif", {})
    gps = exif_dict.get("GPS", {})

    # Camera model
    try:
        model = zeroth.get(piexif.ImageIFD.Model)
        if model:
            if isinstance(model, bytes):
                model = model.decode(errors='ignore')
            out['Model'] = model
    except Exception:
        pass
    # DateTime
    try:
        dt = zeroth.get(piexif.ImageIFD.DateTime)
        if dt:
            if isinstance(dt, bytes):
                dt = dt.decode(errors='ignore')
            out['DateTime'] = dt
    except Exception:
        pass
    # GPS
    if gps:
        out['GPS'] = {}
        try:
            # convert GPS rational format to decimal degrees
            def _rational_to_deg(rat):
                return float(rat[0][0]) / float(rat[0][1]) if isinstance(rat[0], tuple) else float(rat[0])
            # robust conversion
            def gps_to_deg(gps_tuple, ref):
                try:
                    d = gps_tuple[0]
                    m = gps_tuple[1]
                    s = gps_tuple[2]
                    def to_float(t):
                        return t[0]/t[1]
                    deg = to_float(d) + to_float(m)/60.0 + to_float(s)/3600.0
                    if ref in [b'S', 'S', 'W', b'W']:
                        deg = -deg
                    return deg
                except Exception:
                    return None
            lat = gps.get(piexif.GPSIFD.GPSLatitude)
            latref = gps.get(piexif.GPSIFD.GPSLatitudeRef)
            lon = gps.get(piexif.GPSIFD.GPSLongitude)
            lonref = gps.get(piexif.GPSIFD.GPSLongitudeRef)
            if lat and lon:
                out['GPS']['lat'] = gps_to_deg(lat, latref)
                out['GPS']['lon'] = gps_to_deg(lon, lonref)
        except Exception:
            pass

    return out

def image_stats(img):
    """Return per-channel mean and variance and histogram peaks."""
    arr = np.array(img)
    if arr.ndim == 2:
        channels = 1
    else:
        channels = arr.shape[2]
    stats = {}
    if channels == 1:
        mean = float(np.mean(arr))
        var = float(np.var(arr))
        stats['mean'] = mean
        stats['var'] = var
        hist, _ = np.histogram(arr.flatten(), bins=256, range=(0,255))
        stats['hist_peak'] = int(np.argmax(hist))
    else:
        stats['channels'] = {}
        for c, name in enumerate(['R','G','B']):
            ch = arr[:,:,c]
            stats['channels'][name] = {'mean': float(np.mean(ch)), 'var': float(np.var(ch)),
                                       'hist_peak': int(np.argmax(np.histogram(ch.flatten(), bins=256, range=(0,255))[0]))}
    return stats

def compute_perceptual_hashes(img):
    """Compute average hash and phash using imagehash."""
    ah = str(imagehash.average_hash(img))
    ph = str(imagehash.phash(img))
    return {'ahash': ah, 'phash': ph}

def ela_image(pil_img, resave_quality=90, scale=10):
    """
    Return a PIL image of Error Level Analysis (ELA).
    Steps: save PIL image to JPEG at given quality, reload, compute absolute difference,
    enhance difference by scale factor for visualization.
    """
    from io import BytesIO
    orig = pil_img.convert('RGB')
    buffer = BytesIO()
    orig.save(buffer, format='JPEG', quality=resave_quality)
    buffer.seek(0)
    compressed = Image.open(buffer)
    # difference
    diff = ImageChops.difference(orig, compressed)
    # enhance
    extrema = diff.getextrema()
    # scale so that max difference becomes more visible
    enhanced = ImageEnhance.Brightness(diff).enhance(scale)
    return enhanced

def lsb_noise_heuristic(img):
    """
    Heuristic to estimate LSB embedding:
    - Extract least significant bit plane for each channel.
    - Compute proportion of 1s, standard deviation, and bit entropy.
    - Return a small score where higher indicates more randomness (possible stego).
    """
    arr = np.array(img.convert('RGB'))
    scores = {}
    for i, name in enumerate(['R','G','B']):
        ch = arr[:,:,i]
        lsb = ch & 1  # 0/1 matrix
        p1 = float(np.mean(lsb))
        var = float(np.var(lsb))
        # entropy of bit distribution
        p = p1
        if p in (0.0,1.0):
            ent = 0.0
        else:
            ent = -(p*math.log2(p) + (1-p)*math.log2(1-p))
        scores[name] = {'p1': p1, 'var': var, 'entropy': ent}
    # Combine into a single score: average entropy and variance
    avg_entropy = sum(scores[c]['entropy'] for c in ['R','G','B']) / 3.0
    avg_var = sum(scores[c]['var'] for c in ['R','G','B']) / 3.0
    # Normalize and combine heuristically
    score = avg_entropy + 2.0 * avg_var
    return {'per_channel': scores, 'score': score}

# ---------- Main processing ----------

def analyze_image(path, out_dir):
    base = os.path.basename(path)
    name, ext = os.path.splitext(base)
    out = {'file': base}
    # hashes
    out.update(compute_hashes(path))
    # exif
    out['exif'] = extract_exif(path)
    # open image
    try:
        pil = Image.open(path)
    except Exception as e:
        out['error'] = f"Cannot open image: {e}"
        return out
    # stats
    out['stats'] = image_stats(pil)
    # perceptual hashes
    out['phashes'] = compute_perceptual_hashes(pil)
    # ela
    try:
        ela = ela_image(pil, resave_quality=90, scale=10)
        ela_path = os.path.join(out_dir, f"ela_{name}.png")
        ela.save(ela_path)
        out['ela_image'] = ela_path
    except Exception as e:
        out['ela_error'] = str(e)
    # lsb heuristic
    try:
        lsb = lsb_noise_heuristic(pil)
        out['lsb'] = lsb
    except Exception as e:
        out['lsb_error'] = str(e)

    # simple tamper heuristic: ELA bright regions fraction
    try:
        ela_np = np.array(Image.open(out['ela_image']).convert('L'))
        # threshold bright differences
        bright = np.sum(ela_np > 30)
        total = ela_np.size
        fraction = bright / total
        out['ela_bright_fraction'] = fraction
        out['ela_suspicious'] = fraction > 0.01  # heuristic threshold
    except Exception:
        out['ela_suspicious'] = False

    return out

def find_images(input_path):
    imgs = []
    if os.path.isfile(input_path):
        imgs.append(input_path)
    else:
        for root, _, files in os.walk(input_path):
            for f in files:
                if f.lower().endswith(('.jpg', '.jpeg', '.png', '.tiff', '.bmp')):
                    imgs.append(os.path.join(root, f))
    return imgs

def write_csv_report(results, out_csv):
    keys = ['file','md5','sha1','sha256','exif','phashes','stats','lsb','ela_image','ela_bright_fraction','ela_suspicious','error']
    with open(out_csv, 'w', newline='', encoding='utf-8') as csvf:
        writer = csv.DictWriter(csvf, fieldnames=keys)
        writer.writeheader()
        for r in results:
            row = {k: json.dumps(r.get(k)) if k in ('exif','phashes','stats','lsb') else r.get(k) for k in keys}
            writer.writerow(row)

def main():
    parser = argparse.ArgumentParser(description="Simple Image Forensics Tool")
    parser.add_argument('--input', '-i', required=True, help="Input image file or directory")
    parser.add_argument('--out', '-o', default='forensic_results', help="Output folder for results (default forensic_results)")
    args = parser.parse_args()

    os.makedirs(args.out, exist_ok=True)
    images = find_images(args.input)
    if not images:
        print("No images found in", args.input)
        sys.exit(1)
    results = []
    print(f"Found {len(images)} images. Processing...")
    for idx, img in enumerate(images, 1):
        print(f"[{idx}/{len(images)}] {img}")
        res = analyze_image(img, args.out)
        results.append(res)
    out_csv = os.path.join(args.out, 'report.csv')
    write_csv_report(results, out_csv)
    print("Done. Report written to:", out_csv)
    print("ELA images saved to:", args.out)

if __name__ == '__main__':
    main()
