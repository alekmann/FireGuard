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

## Sikkerhet: API-nøkkel autentisering

### Oversikt

FireGuard bruker en API-nøkkel basert autentiseringsmekansime for service-to-service kommunikasjon. Løsningen er designet for:
- Enkel integrasjon uten UI-krav
- Støtte for flere testere (flere nøkler)
- Sikker lagring (kun hash-verdier lagres)
- Enkel revokering av nøkler

### Hvordan det fungerer

1. **Klient sender nøkkelen**: Klienten legger til `X-API-Key` header med rå nøkkelverdien
   ```
   GET /api/fire-risk HTTP/1.1
   X-API-Key: FGK_...
   ```

2. **Server validerer**: 
   - Serveren hasher den innkomne nøkkelen med SHA-256
   - Slår opp dokumentet i Firestore collection `api_keys` med id = sha256(nøkkel)
   - Sjekker at dokumentet eksisterer og `revoked` = false

3. **Resultat**:
   - ✅ Hvis token er valid og ikke revokert → Forespørsel tillatt
   - ❌ Hvis token mangler → 401 Unauthorized
   - ❌ Hvis token er invalid → 403 Forbidden
   - ❌ Hvis token er revokert → 403 Forbidden

### Firestore datastruktur

Collection: `api_keys`

```json
{
  "sha256_hash_of_raw_key": {
    "name": "string (tester navn)",
    "created_at": "ISO 8601 timestamp",
    "revoked": "boolean"
  }
}
```

### Utstede en ny API-nøkkel

```bash
export GOOGLE_APPLICATION_CREDENTIALS=/path/to/serviceAccountKey.json
python functions/app/tools/issue_api_key.py --name "tester1"
```

**Output:**
```
=== API KEY (give this to the tester) ===
FGK_aBcDeFgHiJkLmNoPqRsTuVwXyZ1234567890
=== END (not stored in Firestore) ===

Stored hash doc id: abc123def456...
```

**Viktig:** Den rå nøkkelen skrives ut kun én gang. Gis direkte til testoren.

### Revokere en API-nøkkel

```bash
export GOOGLE_APPLICATION_CREDENTIALS=/path/to/serviceAccountKey.json
python functions/app/tools/revoke_api_key.py --key "FGK_aBcDeFgHiJkLmNoPqRsTuVwXyZ1234567890"
```

En revokert nøkkel kan ikke brukes igjen, selv om den oppfyller validering ellers.

### Bruk i kode

For å beskytte en FastAPI route, bruk `require_api_key` dependency:

```python
from fastapi import Depends
from app.security.api_keys import require_api_key

@app.get("/api/protected")
async def protected_endpoint(user = Depends(require_api_key)):
    return {"data": "sensitive"}
```

I `main.py` er alle protected routes automatisk sikret via router dependency:

```python
app.include_router(
    fire_risk_router,
    dependencies=[Depends(require_api_key)],
)
```

### Sikkerhetshensyn

| Hensyn | Løsning |
|--------|---------|
| Raw keys lagres | Kun SHA-256 hashes lagres i Firestore |
| Key rotation | Opprett ny, revokér gammel |
| Brute force | Firestore rate limiting + database security rules |
| Transport | Bruk HTTPS (Firebase Functions bruker TLS) |
| Multiple testers | Hver tester får egen key |
