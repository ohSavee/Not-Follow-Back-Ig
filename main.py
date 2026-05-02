"""
    pip install instagrapi python-dotenv
"""

import json
import time
from pathlib import Path
from instagrapi import Client
from instagrapi.exceptions import TwoFactorRequired

SESSION_FILE = "session.json"
OUTPUT_FILE  = "non_followers.json"


# ─── CHALLENGE HELP ──────────────────────────────────────────────────────────

def print_challenge_help(username: str) -> None:
    pad = lambda s, n: s + " " * (n - len(s))
    print(f"Instagram ha bloccato l'account @{pad(username, 23)}")


def _is_challenge(e: Exception) -> bool:
    return "challenge" in str(type(e).__name__).lower() or \
           "challenge" in str(e).lower()


# ─── LOGIN ───────────────────────────────────────────────────────────────────

def login(username: str, password: str, label: str = None) -> Client:
    label = label or f"@{username}"
    cl = Client()
    cl.delay_range = [1, 3]

    if Path(SESSION_FILE).exists():
        print("[*] Carico sessione salvata")
        try:
            cl.load_settings(SESSION_FILE)
            cl.login(username, password)
            cl.get_timeline_feed()
            print("[✓] Sessione ripristinata.")
            return cl
        except Exception:
            print("[!] Sessione non valida. Cancello e riaccedo")
            Path(SESSION_FILE).unlink(missing_ok=True)

    print(f"[*] Effettuo il login con {label}...")
    try:
        cl.login(username, password)
    except TwoFactorRequired:
        code = input("[2FA] Inserisci il codice di verifica: ").strip()
        cl.login(username, password, verification_code=code)
    except Exception as e:
        if _is_challenge(e):
            print_challenge_help(username)
            raise SystemExit(1)
        raise

    cl.dump_settings(SESSION_FILE)
    print("[✓] Login completato. Sessione salvata.")
    return cl


# ─── CORE LOGIC ──────────────────────────────────────────────────────────────

def get_non_followers(cl: Client, user_id: int) -> list[dict]:

    print("\n[*] Recupero lista following...")
    try:
        following = cl.user_following(user_id)
    except Exception as e:
        if _is_challenge(e):
            print_challenge_help(cl.username)
            raise SystemExit(1)
        raise
    print(f"    → Stai seguendo {len(following)} persone")

    time.sleep(2)

    print("[*] Recupero lista followers")
    try:
        followers = cl.user_followers(user_id)
    except Exception as e:
        if _is_challenge(e):
            print_challenge_help(cl.username)
            raise SystemExit(1)
        raise
    print(f"    → Hai {len(followers)} follower")

    follower_ids = set(followers.keys())

    return [
        {
            "user_id":     str(uid),
            "username":    user.username,
            "full_name":   user.full_name,
            "profile_url": f"https://www.instagram.com/{user.username}/",
        }
        for uid, user in following.items()
        if uid not in follower_ids
    ]


# ─── OUTPUT ──────────────────────────────────────────────────────────────────

def print_results(non_followers: list[dict]) -> None:
    print(f"\n{'─'*55}")
    print(f"NON TI SEGUONO: {len(non_followers)} utenti")
    print(f"{'─'*55}")
    for i, user in enumerate(non_followers, 1):
        name = f" ({user['full_name']})" if user["full_name"] else ""
        print(f"  {i:>3}. @{user['username']}{name}")
        print(f"       {user['profile_url']}")
    print(f"{'─'*55}\n")


def save_results(non_followers: list[dict]) -> None:
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        json.dump(non_followers, f, ensure_ascii=False, indent=2)
    print(f"[✓] Risultati salvati in '{OUTPUT_FILE}'")


def _choose_mode() -> str:
    print("  Seleziona la modalità:\n")
    print("[1] Account singolo")
    print("[2] Burner account")
    print()
    while True:
        choice = input("Scelta (1/2): ").strip()
        if choice in ("1", "2"):
            return choice
        print("[!] Inserisci 1 o 2.")


if __name__ == "__main__":
    mode = _choose_mode()
    print()

    if mode == "1":
        import mode_single
        mode_single.run()
    else:
        import mode_dual
        mode_dual.run()