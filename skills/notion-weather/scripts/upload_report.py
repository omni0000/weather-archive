#!/usr/bin/env python3
import os
import json
import subprocess
import argparse
from datetime import datetime

# Notion Version constant
NOTION_VERSION = "2025-09-03"
# GitHub Archive Info
GITHUB_USER = "omni0000"
GITHUB_REPO = "weather-archive"
ARCHIVE_DIR = os.path.expanduser("~/.openclaw/workspace/weather-archive")

def get_notion_key():
    key_path = os.path.expanduser("~/.config/notion/api_key")
    if not os.path.exists(key_path):
        raise FileNotFoundError(f"Notion API key not found at {key_path}. Please set it up using the 'notion' skill instructions.")
    with open(key_path, "r") as f:
        return f.read().strip()

def upload_to_github(local_image_path):
    if not os.path.exists(local_image_path):
        raise FileNotFoundError(f"Image not found at {local_image_path}")
    
    # Ensure images directory exists
    images_dir = os.path.join(ARCHIVE_DIR, "images")
    os.makedirs(images_dir, exist_ok=True)
    
    # Copy image with simple date-based name
    timestamp_name = datetime.now().strftime("%Y%m%d")
    filename = f"weather_{timestamp_name}.png"
    relative_path = f"images/{filename}"
    target_path = os.path.join(ARCHIVE_DIR, relative_path)
    
    subprocess.run(["cp", local_image_path, target_path], check=True)
    
    # Git operations
    subprocess.run(["git", "-C", ARCHIVE_DIR, "add", "."], check=True)
    subprocess.run(["git", "-C", ARCHIVE_DIR, "commit", "-m", f"Archive weather report {timestamp_name}"], check=True)
    subprocess.run(["git", "-C", ARCHIVE_DIR, "push"], check=True)
    
    # Construct Raw URL
    raw_url = f"https://raw.githubusercontent.com/{GITHUB_USER}/{GITHUB_REPO}/main/{relative_path}"
    return raw_url

def create_notion_entry(database_id, image_url, summary_text):
    notion_key = get_notion_key()
    url = "https://api.notion.com/v1/pages"
    
    now = datetime.now()
    date_str = now.strftime("%Y-%m-%d")
    weekday_str = now.strftime("%A")

    data = {
        "parent": {"database_id": database_id},
        "properties": {
            "Date": {"title": [{"text": {"content": date_str}}]},
            "Report Date": {"date": {"start": date_str}},
            "Status": {"select": {"name": "Generated"}},
            "Image URL": {"url": image_url}
        },
        "children": [
            {
                "object": "block",
                "type": "heading_3",
                "heading_3": {
                    "rich_text": [{"text": {"content": f"Weather Report - {date_str}"}}]
                }
            },
            {
                "object": "block",
                "type": "image",
                "image": {
                    "type": "external",
                    "external": {
                        "url": image_url
                    }
                }
            }
        ]
    }
    
    res = subprocess.run([
        "curl", "-s", "-X", "POST", url,
        "-H", f"Authorization: Bearer {notion_key}",
        "-H", "Notion-Version: 2022-06-28",
        "-H", "Content-Type: application/json",
        "-d", json.dumps(data)
    ], capture_output=True, text=True)
    
    return res.stdout

import tweepy

# X (Twitter) Archive Info
X_CREDENTIALS_PATH = os.path.expanduser("~/.config/x/credentials.json")

def get_x_credentials():
    if not os.path.exists(X_CREDENTIALS_PATH):
        raise FileNotFoundError(f"X credentials not found at {X_CREDENTIALS_PATH}")
    with open(X_CREDENTIALS_PATH, "r") as f:
        return json.load(f)

def post_to_x(image_path, summary_text):
    creds = get_x_credentials()
    
    # Authenticate with X (V1 for media, V2 for text)
    auth = tweepy.OAuth1UserHandler(
        creds["api_key"], creds["api_key_secret"],
        creds["access_token"], creds["access_token_secret"]
    )
    api_v1 = tweepy.API(auth)
    client_v2 = tweepy.Client(
        bearer_token=creds["bearer_token"],
        consumer_key=creds["api_key"],
        consumer_secret=creds["api_key_secret"],
        access_token=creds["access_token"],
        access_token_secret=creds["access_token_secret"]
    )

    # 1. Upload Media (V1.1)
    media = api_v1.media_upload(filename=image_path)
    media_id = media.media_id

    # 2. Post Tweet (V2)
    now = datetime.now()
    date_str = now.strftime("%Y-%m-%d")
    
    # 기상캐스터 느낌의 멘트 생성 (3줄 내외)
    # 이미지 중심 포스팅을 위해 텍스트 요약 제외
    status = f"✨ {date_str} 오늘의 날씨 배달입니다!\n\n오늘도 상쾌하고 기분 좋은 하루 보내시길 바랄게요! 🌤️\n\n#오늘의날씨 #기상정보 #출근길체크 #날씨리포트 #DailyWeather"
    
    response = client_v2.create_tweet(text=status, media_ids=[media_id])
    return response

def update_notion_with_x_info(page_id, tweet_id, tweet_url):
    notion_key = get_notion_key()
    url = f"https://api.notion.com/v1/pages/{page_id}"
    
    data = {
        "properties": {
            "X Post URL": {"url": tweet_url},
            "X Status": {"select": {"name": "Posted"}}
        }
    }
    
    res = subprocess.run([
        "curl", "-s", "-X", "PATCH", url,
        "-H", f"Authorization: Bearer {notion_key}",
        "-H", "Notion-Version: 2022-06-28",
        "-H", "Content-Type: application/json",
        "-d", json.dumps(data)
    ], capture_output=True, text=True)
    
    return res.stdout

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Upload weather image to GitHub, Notion, and X.")
    parser.add_argument("--database-id", required=True, help="Notion Database ID")
    parser.add_argument("--image-path", required=True, help="Local path to the weather image")
    parser.add_argument("--summary", required=True, help="Weather summary text")
    parser.add_argument("--post-x", action="store_true", help="Whether to post to X")
    
    args = parser.parse_args()
    
    try:
        print("Uploading image to GitHub...")
        image_url = upload_to_github(args.image_path)
        print(f"Image uploaded to GitHub: {image_url}")
        
        print("Creating Notion entry...")
        notion_res_json = create_notion_entry(args.database_id, image_url, args.summary)
        notion_data = json.loads(notion_res_json)
        page_id = notion_data.get("id")
        print(f"Notion entry created (ID: {page_id}).")

        if args.post_x and page_id:
            print("Posting to X (Twitter)...")
            x_result = post_to_x(args.image_path, args.summary)
            tweet_id = x_result.data.get("id")
            # Construct a standard tweet URL (using username or id)
            tweet_url = f"https://x.com/user/status/{tweet_id}"
            print(f"Posted to X: {tweet_url}")
            
            print("Updating Notion with X posting info...")
            update_notion_with_x_info(page_id, tweet_id, tweet_url)
            print("Notion updated with X info.")
        
        print("All tasks completed successfully!")
    except Exception as e:
        print(f"Error: {e}")
        exit(1)
