import getpass
import os
from dotenv import load_dotenv
from main import login, get_non_followers, print_results, save_results

load_dotenv()

def run() -> None:
    burner_user = os.getenv("BURNER_USERNAME") or input("Username account burner:   ").strip()
    burner_pass = os.getenv("BURNER_PASSWORD") or getpass.getpass("Password account burner:   ")
    target_user = os.getenv("TARGET_USERNAME") or input("Username account target:   ").strip()

    cl = login(burner_user, burner_pass, label=f"@{burner_user} (burner)")
    print(f"[✓] Loggato come: @{burner_user}")

    print(f"\n[*] Cerco il profilo target: @{target_user}...")
    target_info = cl.user_info_by_username(target_user)
    user_id = target_info.pk
    print(f"[✓] Profilo trovato: @{target_user} (ID: {user_id})")

    non_followers = get_non_followers(cl, user_id)
    print_results(non_followers)
    save_results(non_followers)