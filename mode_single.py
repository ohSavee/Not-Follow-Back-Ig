import getpass
import os
from dotenv import load_dotenv
from main import login, get_non_followers, print_results, save_results

load_dotenv()


def run() -> None:
    username = os.getenv("INSTAGRAM_USERNAME") or input("Username Instagram: ").strip()
    password = os.getenv("INSTAGRAM_PASSWORD") or getpass.getpass("Password Instagram: ")

    cl = login(username, password, label=f"@{username}")
    print(f"[✓] Loggato come: @{username}")

    user_id = cl.user_id

    non_followers = get_non_followers(cl, user_id)
    print_results(non_followers)
    save_results(non_followers)