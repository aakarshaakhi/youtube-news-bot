"""
get_youtube_token.py
--------------------
Run this ONCE from Termux on your Android phone.
It opens a browser login → you approve → refresh token is printed.
Copy that token into GitHub Secrets as YOUTUBE_REFRESH_TOKEN.

Usage:
  python get_youtube_token.py \
    --client_id YOUR_CLIENT_ID \
    --client_secret YOUR_CLIENT_SECRET
"""

import argparse
from google_auth_oauthlib.flow import InstalledAppFlow
import json

SCOPES = ["https://www.googleapis.com/auth/youtube.upload"]

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--client_id",     required=True)
    parser.add_argument("--client_secret", required=True)
    args = parser.parse_args()

    client_config = {
        "installed": {
            "client_id":     args.client_id,
            "client_secret": args.client_secret,
            "auth_uri":      "https://accounts.google.com/o/oauth2/auth",
            "token_uri":     "https://oauth2.googleapis.com/token",
            "redirect_uris": ["urn:ietf:wg:oauth:2.0:oob", "http://localhost"]
        }
    }

    flow = InstalledAppFlow.from_client_config(client_config, SCOPES)

    print("\n⚠️  A browser link will appear below.")
    print("Open it, log in with your YouTube Google account, and approve access.\n")

    creds = flow.run_console()

    print("\n" + "="*60)
    print("✅ SUCCESS! Copy this REFRESH TOKEN into GitHub Secrets")
    print("   Secret name: YOUTUBE_REFRESH_TOKEN")
    print("="*60)
    print(f"\nREFRESH TOKEN:\n{creds.refresh_token}\n")


if __name__ == "__main__":
    main()
