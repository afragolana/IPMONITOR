# Comandi git pronti da copiare

> Sostituisci `TUO-UTENTE` con il tuo username GitHub e `url-monitor` con il nome del repo (se lo chiami diversamente). I comandi vanno eseguiti **dentro la cartella **`urlmonitor-cloud` (quella che contiene `monitor.py`).

---

## 0. Prerequisiti (una volta sola)

Verifica che git sia installato:

```bash
git --version

```

Se non lo è: scaricalo da [https://git-scm.com/download/win](https://git-scm.com/download/win)

Imposta nome ed email (se non già fatto):

```bash
git config --global user.name  "Biagio Cerbone"
git config --global user.email "biagio.cerbone@dxc.com"

```

---

## 1. Crea il repository su GitHub

Vai su [https://github.com/new](https://github.com/new) → nome `url-monitor` → **Public** → **NON** aggiungere README/.gitignore (ci sono già) → *Create repository*.

---

## 2. Primo push del progetto

Apri il terminale nella cartella `urlmonitor-cloud` ed esegui:

```bash
git init
git add .
git commit -m "URL monitor iniziale"
git branch -M main
git remote add origin https://github.com/TUO-UTENTE/url-monitor.git
git push -u origin main

```

> 💡 Al push, GitHub ti chiederà le credenziali. Usa un **Personal Access Token** come password (non la password dell'account): GitHub → Settings → Developer settings → Personal access tokens → *Generate new token (classic)* → spunta `repo` → genera e incollalo quando richiesto.

---

## 3. Configura GitHub Pages e permessi (dal browser)

- **Settings → Pages** → *Source:* **GitHub Actions**
- **Settings → Actions → General** → *Workflow permissions:* **Read and write permissions** → Save

---

## 4. Avvia il primo run

- Tab **Actions** → workflow *URL Monitor* → **Run workflow**
- Dopo ~1 min la dashboard è online a: **[https://TUO-UTENTE.github.io/url-monitor/](https://TUO-UTENTE.github.io/url-monitor/)**

---

## Aggiornamenti successivi (quando modifichi urls.txt o altro)

```bash
git add .
git commit -m "aggiorno le URL monitorate"
git push

```

L'Action riparte automaticamente ad ogni push (oltre che ogni 15 minuti).

---

## Comandi utili

| Azione | Comando |
| --- | --- |
| Vedere lo stato dei file | `git status` |
| Vedere la history dei commit | `git log --oneline` |
| Scaricare le modifiche fatte dal bot (status.json) | `git pull` |
| Annullare modifiche locali non committate | `git checkout -- .` |

> ⚠️ Il bot dell'Action committa `status.json` da solo ad ogni run. Prima di fare push di modifiche tue, lancia `git pull` per allineare, altrimenti git potrebbe segnalare un conflitto. In caso di conflitto su `status.json`, puoi tranquillamente tenere la versione remota: `git checkout --theirs public/status.json` poi `git add public/status.json`.

