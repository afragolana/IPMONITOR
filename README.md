# URL Monitor — Cloud (GitHub Actions + GitHub Pages)

Monitoraggio **gratuito** di URL **pubbliche**, senza usare il tuo PC.
GitHub Actions esegue il check ogni 15 minuti e pubblica una dashboard
stile IPMonitor su GitHub Pages (timeline 24h + % uptime).

> ⚠️ **Solo URL pubbliche.** Il runner di GitHub è su internet pubblico: NON
> può raggiungere le URL interne/intranet (`.sidi.mpi.it`,
> `miurjb*.pubblica.istruzione.it`, ecc.), che risulterebbero sempre rosse.
> Metti in `urls.txt` solo URL che si aprono **senza VPN**.

## 📂 Struttura del repository

```
urlmonitor-cloud/
├── .github/workflows/monitor.yml   ← il workflow (cron ogni 15 min + deploy Pages)
├── monitor.py                      ← script di check
├── urls.txt                        ← le URL da monitorare (una per riga)
├── public/
│   ├── index.html                  ← la dashboard (servita da Pages)
│   └── status.json                 ← dati + storico (aggiornati dall'Action)
└── README.md
```

## 🚀 Setup su GitHub (una volta sola)

### 1. Crea il repository
- Vai su https://github.com/new → crea un repo, es. `url-monitor` (può essere **pubblico**;
  se lo vuoi privato, GitHub Pages privato richiede un piano a pagamento — per un repo
  pubblico è tutto gratis).
- **Importante:** la dashboard sarà visibile pubblicamente se il repo è pubblico. Dato che
  monitoriamo solo URL pubbliche, in genere va bene. Se preferisci non esporla, vedi la nota
  in fondo.

### 2. Carica i file
Due modi:
- **Via browser:** nel repo → *Add file → Upload files* → trascina tutto il contenuto di
  questa cartella (incluse le sottocartelle `.github` e `public`). Commit.
- **Via git:**
  ```bash
  git init
  git add .
  git commit -m "URL monitor iniziale"
  git branch -M main
  git remote add origin https://github.com/<TUO-UTENTE>/url-monitor.git
  git push -u origin main
  ```

### 3. Abilita GitHub Pages
- Repo → **Settings → Pages**
- In *Build and deployment* → **Source: GitHub Actions**. Salva.

### 4. Abilita i permessi delle Actions
- Repo → **Settings → Actions → General** → scorri a *Workflow permissions*
- Seleziona **Read and write permissions** → Salva.
  (Serve perché l'Action committa `status.json` aggiornato.)

### 5. Modifica le URL
- Apri `urls.txt` e lascia attive (senza `#`) solo le URL pubbliche che vuoi monitorare.
  Ho già pre-impostato come candidate `unica.istruzione.gov.it`, `www.mim.gov.it` e
  `wsmiur...`; **verificale dal telefono senza VPN** e correggi.

### 6. Avvia il primo run
- Repo → tab **Actions** → workflow *URL Monitor* → **Run workflow**.
- Dopo ~1 minuto, la dashboard sarà online a:
  **`https://<TUO-UTENTE>.github.io/url-monitor/`**

Da lì gira da sola ogni 15 minuti. ✅

## 📊 La dashboard
Identica alla versione locale: per ogni URL una timeline **23 ore (oraria) + ultima
ora (15 min)**, con **% uptime 24h** a destra. 🟩 OK · 🟨 lento (>3s) · 🟥 failure.
Lo storico si popola nel tempo (24h per la vista completa).

## ⚙️ Personalizzazioni
- **Frequenza:** nel file `.github/workflows/monitor.yml`, campo `cron`. Nota: GitHub
  Actions su cron può avere ritardi di qualche minuto (è normale sul piano gratuito).
- **Soglia lentezza / timeout:** in cima a `monitor.py` (`SLOW_THRESHOLD_S`, `TIMEOUT_S`).

## 🏷️ Badge di stato

Lo script genera `public/badge.json` (formato endpoint Shields.io). Aggiungi questo
badge in cima al README del tuo repo — mostra verde/giallo/rosso in base allo stato:

```markdown
![URL Monitor](https://img.shields.io/endpoint?url=https://TUO-UTENTE.github.io/url-monitor/badge.json)
```

Sostituisci `TUO-UTENTE` e `url-monitor` con i tuoi. Il badge diventa:
**verde** = tutte su · **giallo** = qualcuna lenta · **rosso** = almeno una down ·
**grigio** = in attesa del primo run.

## 🔔 Alert
Gli alert di failure vengono scritti in `monitor.log` (committato) con `ALERT FAILURE`.
Vuoi anche un'email/Telegram? Si può aggiungere uno step al workflow — chiedimelo.

## 🔒 Nota privacy
Se il repo è **pubblico**, la dashboard e le URL in `urls.txt` sono visibili a chiunque
abbia il link. Monitoriamo solo URL pubbliche, quindi di norma non è un problema. Se vuoi
tenerle riservate, serve un repo privato con Pages a pagamento, oppure proteggere la pagina
— fammi sapere e vediamo l'alternativa.

## 💸 Costi — tutto gratis
GitHub Actions: 2.000 minuti/mese gratis per repo privati, **illimitati per repo pubblici**.
Ogni run dura pochi secondi. GitHub Pages: gratis per repo pubblici.
