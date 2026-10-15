#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
URL Monitor - versione CLOUD (GitHub Actions).

Eseguito da GitHub Actions ogni 15 minuti. A differenza della versione locale,
qui lo storico vive SOLO nei file committati nel repo (il runner e' effimero):
lo script LEGGE lo status.json esistente, aggiunge il nuovo check, applica la
retention 24h e riscrive status.json. Il workflow poi committa il file e lo
pubblica su GitHub Pages insieme alla dashboard.

Le URL da monitorare stanno in urls.txt (una per riga, # per commenti).
"""

import json
import os
import ssl
import time
import socket
import urllib.request
import urllib.error
from datetime import datetime, timezone

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
# In GitHub Actions pubblichiamo la cartella 'public' su Pages:
PUBLIC_DIR = os.path.join(BASE_DIR, "public")

URLS_FILE   = os.path.join(BASE_DIR, "urls.txt")
STATUS_FILE = os.path.join(PUBLIC_DIR, "status.json")
BADGE_FILE  = os.path.join(PUBLIC_DIR, "badge.json")
LOG_FILE    = os.path.join(BASE_DIR, "monitor.log")

SLOW_THRESHOLD_S = 3.0     # oltre questo tempo (secondi) -> GIALLO (SLOW)
TIMEOUT_S        = 15
RETENTION_HOURS  = 25

SSL_CTX = ssl.create_default_context()
SSL_CTX.check_hostname = False
SSL_CTX.verify_mode = ssl.CERT_NONE


def log(msg):
    line = f"{datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S')}Z  {msg}"
    print(line)
    try:
        with open(LOG_FILE, "a", encoding="utf-8") as f:
            f.write(line + "\n")
    except Exception:
        pass


def load_urls():
    urls = []
    if not os.path.exists(URLS_FILE):
        return urls
    with open(URLS_FILE, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith("#"):
                urls.append(line)
    return urls


def host_of(url):
    try:
        return url.split("//", 1)[1].split("/", 1)[0]
    except Exception:
        return url


def check(url):
    start = time.time()
    try:
        req = urllib.request.Request(
            url, method="GET",
            headers={"User-Agent": "Mozilla/5.0 (URL-Monitor-Cloud)"},
        )
        resp = urllib.request.urlopen(req, timeout=TIMEOUT_S, context=SSL_CTX)
        elapsed = time.time() - start
        code = resp.getcode()
        try:
            resp.read(2048)
        except Exception:
            pass
        if code < 400:
            status = "SLOW" if elapsed > SLOW_THRESHOLD_S else "UP"
            err = None
        else:
            status = "FAIL"
            err = f"HTTP {code}"
        return {"status": status, "code": code,
                "ms": round(elapsed * 1000), "error": err}
    except urllib.error.HTTPError as e:
        elapsed = time.time() - start
        return {"status": "FAIL", "code": e.code,
                "ms": round(elapsed * 1000), "error": f"HTTP {e.code}"}
    except (urllib.error.URLError, socket.timeout, Exception) as e:
        elapsed = time.time() - start
        return {"status": "FAIL", "code": None,
                "ms": round(elapsed * 1000),
                "error": f"{type(e).__name__}: {str(e)[:120]}"}


def load_prev_history():
    """Legge lo storico dal status.json committato, con retention."""
    if not os.path.exists(STATUS_FILE):
        return []
    try:
        with open(STATUS_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
    except Exception:
        return []
    cutoff = time.time() - RETENTION_HOURS * 3600
    return [r for r in data.get("history", []) if r.get("ts", 0) >= cutoff]



def write_badge(n_up, n_slow, n_fail, total):
    """Scrive badge.json nel formato endpoint di Shields.io.
    Verde = tutto ok, giallo = qualche lentezza, rosso = almeno un down."""
    if total == 0:
        message, color = "nessuna URL", "lightgrey"
    elif n_fail > 0:
        message, color = f"{n_fail} down / {total}", "red"
    elif n_slow > 0:
        message, color = f"{n_slow} lenti / {total}", "yellow"
    else:
        message, color = f"{total} up", "brightgreen"
    badge = {"schemaVersion": 1, "label": "url-monitor",
             "message": message, "color": color}
    with open(BADGE_FILE, "w", encoding="utf-8") as f:
        json.dump(badge, f, ensure_ascii=False)


def main():
    os.makedirs(PUBLIC_DIR, exist_ok=True)
    urls = load_urls()
    if not urls:
        log("Nessuna URL in urls.txt — niente da controllare.")
        return

    now = time.time()
    now_iso = datetime.now(timezone.utc).isoformat()

    history = load_prev_history()
    results = []
    n_fail = n_slow = n_up = 0

    for url in urls:
        r = check(url)
        r.update({"url": url, "host": host_of(url), "ts": now, "iso": now_iso})
        results.append(r)
        history.append(r)
        if r["status"] == "FAIL":
            n_fail += 1
            log(f"ALERT FAILURE  {r['host']}  {r['error']}  ({r['ms']}ms)")
        elif r["status"] == "SLOW":
            n_slow += 1
            log(f"WARN  SLOW     {r['host']}  {r['ms']}ms")
        else:
            n_up += 1

    payload = {
        "generated_at": now_iso,
        "slow_threshold_s": SLOW_THRESHOLD_S,
        "summary": {"up": n_up, "slow": n_slow, "fail": n_fail, "total": len(urls)},
        "current": results,
        "history": history,
    }
    with open(STATUS_FILE, "w", encoding="utf-8") as f:
        json.dump(payload, f, ensure_ascii=False, indent=1)

    write_badge(n_up, n_slow, n_fail, len(urls))

    log(f"CHECK done  up={n_up} slow={n_slow} fail={n_fail}  "
        f"(storico: {len(history)} record)")


if __name__ == "__main__":
    main()
