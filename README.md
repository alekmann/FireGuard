# FireGuard

## Initial planned software architecture
<img width="1136" height="737" alt="image" src="https://github.com/user-attachments/assets/00d6d53b-8a2d-4311-9e92-b797c3da58c1" />

## Local setup

Følg stegene under for å kjøre Firebase Functions lokalt.

## 1. Gå inn i `functions`-mappen
```bash
cd functions
```
## 2. Opprett et virtuelt miljø
```bash
python -m venv venv
```
## 3. Installer avhengigheter direkte i venv
```bash
./venv/Scripts/python -m pip install -r requirements.txt
```
## 4. Start Firebase-emulatoren
```bash
cd ..
firebase emulators:start --only functions
```
