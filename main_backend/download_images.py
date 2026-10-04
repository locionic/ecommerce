import sqlite3
import os
import urllib.request
import time

BASE_URL = "https://ecommerce-x3n5.onrender.com/media/"

conn = sqlite3.connect("db.sqlite3")
cursor = conn.cursor()

def download_paths(table, column):
    try:
        cursor.execute(f"SELECT {column} FROM {table} WHERE {column} IS NOT NULL AND {column} != ''")
    except sqlite3.OperationalError:
        return 0, 0
    
    success = 0
    fail = 0
    for row in cursor.fetchall():
        path = row[0]
        if not path: continue
        
        full_local_path = os.path.join("media", path)
        remote_url = BASE_URL + path.replace("\\", "/")
        os.makedirs(os.path.dirname(full_local_path), exist_ok=True)
        
        if os.path.exists(full_local_path) and os.path.getsize(full_local_path) > 1000:
            # Skip already downloaded images
            continue
            
        print(f"Downloading {remote_url} ...")
        try:
            req = urllib.request.Request(remote_url, headers={'User-Agent': 'Mozilla/5.0'})
            with urllib.request.urlopen(req) as response, open(full_local_path, 'wb') as out_file:
                out_file.write(response.read())
            success += 1
        except Exception as e:
            print(f"Failed to download {path}: {e}")
            fail += 1
    return success, fail

total_s, total_f = 0, 0

print("Downloading product thumbnails...")
s, f = download_paths("store_product", "thumbnail")
total_s += s; total_f += f

print("Downloading album images...")
s, f = download_paths("store_album", "image")
total_s += s; total_f += f

print("Downloading user avatars...")
s, f = download_paths("users_customuser", "avatar")
total_s += s; total_f += f

print(f"\nDone! Successfully downloaded: {total_s}. Failed: {total_f}.")
