#!/usr/bin/env python3
"""AstroMystic AI — Automated Instagram Publisher Client"""
import os
import sys
import json
import time
import argparse
from instagrapi import Client
from instagrapi.exceptions import LoginRequired

# Reconfigure stdout to UTF-8
sys.stdout.reconfigure(encoding='utf-8')

SESSION_FILE = os.path.join(os.path.dirname(__file__), "session.json")

def get_client():
    cl = Client()
    # Randomize user agent to simulate genuine browser
    cl.set_user_agent("Mozilla/5.0 (iPhone; CPU iPhone OS 16_6 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.6 Mobile/15E148 Safari/604.1")
    return cl

def load_session(cl):
    if os.path.exists(SESSION_FILE):
        try:
            print("[+] Found cached session file. Attempting login using session...")
            with open(SESSION_FILE, "r") as f:
                session_data = json.load(f)
            cl.set_settings(session_data)
            cl.login_by_sessionid(session_data["uuids"]["phone_id"]) # simple verification
            print("  [OK] Session authenticated successfully!")
            return True
        except Exception as e:
            print(f"  [Warning] Cached session invalid or expired: {e}")
            # Delete invalid session
            try:
                os.remove(SESSION_FILE)
            except Exception:
                pass
    return False

def save_session(cl):
    try:
        settings = cl.get_settings()
        with open(SESSION_FILE, "w") as f:
            json.dump(settings, f, indent=2)
        print("[+] Session saved successfully to session.json")
    except Exception as e:
        print(f"[-] Error saving session: {e}")

def handle_login(username, password):
    cl = get_client()
    if load_session(cl):
        return cl
        
    print(f"[+] Authenticating directly for user: {username} ...")
    if not password:
        import getpass
        password = getpass.getpass("Enter Instagram Password: ")
        
    try:
        # Direct login
        cl.login(username, password)
        print("  [OK] Direct login successful!")
        save_session(cl)
        return cl
    except Exception as e:
        print(f"[-] Authentication Failed: {e}")
        sys.exit(1)

def main():
    parser = argparse.ArgumentParser(description="AstroMystic Instagram Automation Client")
    subparsers = parser.add_subparsers(dest="command", required=True)

    # 1. Login Command
    login_parser = subparsers.add_parser("login", help="Authenticate and cache session")
    login_parser.add_argument("--username", required=True, help="Instagram username")
    login_parser.add_argument("--password", help="Instagram password (will prompt if omitted)")

    # 2. Check Session
    subparsers.add_parser("check-session", help="Check if active cached session is valid")

    # 3. Publish Carousel
    carousel_parser = subparsers.add_parser("publish-carousel", help="Publish a carousel of images")
    carousel_parser.add_argument("--username", required=True, help="Instagram username")
    carousel_parser.add_argument("--images", nargs="+", required=True, help="List of image file paths")
    carousel_parser.add_argument("--caption", required=True, help="Caption text")

    # 4. Publish Single Photo
    photo_parser = subparsers.add_parser("publish-photo", help="Publish a single photo")
    photo_parser.add_argument("--username", required=True, help="Instagram username")
    photo_parser.add_argument("--image", required=True, help="Image file path")
    photo_parser.add_argument("--caption", required=True, help="Caption text")

    # 5. Publish Reel
    reel_parser = subparsers.add_parser("publish-reel", help="Publish an MP4 video as a Reel")
    reel_parser.add_argument("--username", required=True, help="Instagram username")
    reel_parser.add_argument("--video", required=True, help="Video file path")
    reel_parser.add_argument("--caption", required=True, help="Caption text")

    args = parser.parse_args()

    if args.command == "login":
        handle_login(args.username, args.password)

    elif args.command == "check-session":
        cl = get_client()
        if load_session(cl):
            print("  [SUCCESS] Session is ACTIVE and VALID.")
        else:
            print("  [FAILED] No valid session. Please login first.")
            sys.exit(1)

    elif args.command == "publish-photo":
        cl = handle_login(args.username, None)
        image_path = os.path.abspath(args.image)
        if not os.path.exists(image_path):
            print(f"[-] Error: Image path does not exist: {image_path}")
            sys.exit(1)
            
        print(f"[+] Publishing photo: {image_path} ...")
        try:
            media = cl.photo_upload(path=image_path, caption=args.caption)
            print(f"  [SUCCESS] Photo posted successfully! Media ID: {media.id}")
        except Exception as e:
            print(f"[-] Posting Failed: {e}")
            sys.exit(1)

    elif args.command == "publish-carousel":
        cl = handle_login(args.username, None)
        
        # Resolve absolute paths
        resolved_images = []
        for img in args.images:
            abs_img = os.path.abspath(img)
            if os.path.exists(abs_img):
                resolved_images.append(abs_img)
            else:
                print(f"[-] Warning: Image skipped (not found): {abs_img}")
                
        if not resolved_images:
            print("[-] Error: No valid images found to compile carousel.")
            sys.exit(1)
            
        print(f"[+] Compiling and publishing carousel with {len(resolved_images)} slides...")
        try:
            # instagrapi carousel upload takes a list of paths
            media = cl.album_upload(paths=resolved_images, caption=args.caption)
            print(f"  [SUCCESS] Carousel album posted successfully! Media ID: {media.id}")
        except Exception as e:
            print(f"[-] Carousel Posting Failed: {e}")
            sys.exit(1)

    elif args.command == "publish-reel":
        cl = handle_login(args.username, None)
        video_path = os.path.abspath(args.video)
        if not os.path.exists(video_path):
            print(f"[-] Error: Video path does not exist: {video_path}")
            sys.exit(1)
            
        print(f"[+] Uploading and publishing video Reel: {video_path} ...")
        try:
            # clip_upload registers the video as a native Reel
            media = cl.clip_upload(path=video_path, caption=args.caption)
            print(f"  [SUCCESS] Video Reel published successfully! Media ID: {media.id}")
        except Exception as e:
            print(f"[-] Video Reel Posting Failed: {e}")
            sys.exit(1)

if __name__ == "__main__":
    main()
