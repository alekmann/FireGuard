# FireGuard

## Initial planned software architecture
<img width="1136" height="737" alt="image" src="https://github.com/user-attachments/assets/00d6d53b-8a2d-4311-9e92-b797c3da58c1" />

## Peer Review

Peer review av dette prosjektet er ikke ment å kreve full lokal reproduksjon av produksjonsmiljøet. FireGuard bruker GCP-ressurser og rettigheter som ikke deles bredt, så peer review gjennomføres primært gjennom kodegjennomgang, lokale tester og kall mot den deployede API-en.

### Forutsetninger

For å gjennomføre peer review trenger revieweren:
- tilgang til repoet
- et lokalt Python-miljø for å lese kode og kjøre tester
- en midlertidig `X-API-Key` fra prosjektgruppen for å teste beskyttede endepunkter

### Swagger og API-dokumentasjon

Den deployede API-en er tilgjengelig her:

- Swagger UI: `https://us-central1-fireguard-2faea.cloudfunctions.net/api/docs`
- ReDoc: `https://us-central1-fireguard-2faea.cloudfunctions.net/api/redoc`
- OpenAPI JSON: `https://us-central1-fireguard-2faea.cloudfunctions.net/api/openapi.json`

### Hva revieweren kan teste selv

Revieweren kan lese dokumentasjonen i Swagger/ReDoc, kjøre testene lokalt og teste disse endepunktene i cloud:

```bash
curl "https://us-central1-fireguard-2faea.cloudfunctions.net/api/health"

curl -i \
  -H "X-API-Key: DIN_API_NOKKEL" \
  "https://us-central1-fireguard-2faea.cloudfunctions.net/api/fire-risk/compute-by-location?lat=60.3913&lon=5.3221&points=12"

curl -i -X POST \
  -H "X-API-Key: DIN_API_NOKKEL" \
  -d '' \
  "https://us-central1-fireguard-2faea.cloudfunctions.net/api/messaging/publish-fire-risk?lat=60.3913&lon=5.3221&points=12"
```

### Pub/Sub-verifisering

Hvis revieweren ønsker bekreftelse på at Pub/Sub-kallet faktisk fungerte, kan prosjektgruppen sende skjermbilde eller logg som viser publisert melding. Relevant oppsett:
- topic: `fire-risk-updated`
- subscription: `projects/fireguard-2faea/subscriptions/fire-risk-updated-sub`

### Relevante filer å lese

Ved kodegjennomgang er disse filene spesielt relevante:

- `functions/main.py`
- `functions/app/api/fire_risk.py`
- `functions/app/api/messaging.py`
- `functions/app/services/fire_risk_service.py`
- `functions/app/services/fire_risk_messaging_service.py`
- `functions/app/services/pubsub_publisher_service.py`
- `tests/`

## Local setup

Følg stegene under for å kjøre Firebase Functions lokalt.

### 1. Gå inn i `functions`-mappen
```bash
cd functions
```
### 2. Opprett et virtuelt miljø
```bash
python -m venv venv
```
### 3. Installer avhengigheter direkte i venv
```bash
./venv/Scripts/python -m pip install -r requirements.txt
```
### 4. Start Firebase-emulatoren
```bash
cd ..
firebase emulators:start --only functions
```

Når Functions-emulatoren kjører, er base-URL normalt:

```text
http://127.0.0.1:5001/fireguard-2faea/us-central1/api
```

## Running tests

Kjør testene med Python-interpreteren i `functions/venv`:

```bash
./functions/venv/Scripts/python -m pytest tests
```

Merk at flere tester bruker `pytest.importorskip("frcm")`. Hvis `frcm` ikke er installert i miljøet som brukes til testing, vil disse testene bli markert som `skipped`.

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

## Tilleggsdokumentasjon

### Prosjektoversikt

FireGuard er en Firebase Functions-basert backend som tilbyr:
- REST-endepunkter for beregning av fire risk
- integrasjon mot MET for værdata
- Firestore-basert caching av lokasjonsoppslag
- API-key autentisering for service-to-service bruk
- Pub/Sub-basert messaging for fire risk-events

Backenden er implementert med FastAPI og eksponert gjennom en Firebase Function med navn `api`.

### Runtime-arkitektur

Hovedflyten i backend er delt på disse filene:
- `functions/main.py`
  Initialiserer Firebase, FastAPI, router-registrering og Firebase Functions entrypoint.
- `functions/app/api/fire_risk.py`
  Eksponerer hoved-API-et for synkrone fire risk-beregninger.
- `functions/app/services/fire_risk_service.py`
  Konverterer weather records til `frcm`-modellen og kjører selve fire risk-beregningen.
- `functions/app/services/fire_risk_cache_service.py`
  Lagrer og henter cachede fire risk-resultater i Firestore.
- `functions/app/api/messaging.py`
  Eksponerer Pub/Sub publish-endepunktet.
- `functions/app/services/fire_risk_messaging_service.py`
  Bygger event-payload og koordinerer publish-flyten.
- `functions/app/services/pubsub_publisher_service.py`
  Håndterer publisering til Pub/Sub-topic-et.

### REST-endepunkter

Public endpoint:
- `GET /health`

Protected endpoints:
- `POST /fire-risk/compute`
  Tar imot weather input som JSON eller CSV og returnerer beregnet fire risk.
- `GET /fire-risk/compute-by-location?lat=...&lon=...&points=...`
  Henter data fra MET, beregner fire risk og returnerer resultatet. Bruker Firestore-cache for gjentatte forespørsler.
- `POST /messaging/publish-fire-risk?lat=...&lon=...&points=...`
  Henter værdata, beregner fire risk, bygger et event, publiserer det til Pub/Sub og logger eventet i Firestore.

Alle protected endpoints krever:

```http
X-API-Key: FGK_...
```

### Lokale emulator-URL-er

Når Functions-emulatoren kjører, er base-URL normalt:

```text
http://127.0.0.1:5001/fireguard-2faea/us-central1/api
```

Nyttige eksempler:
- Health:
  `http://127.0.0.1:5001/fireguard-2faea/us-central1/api/health`
- Fire risk by location:
  `http://127.0.0.1:5001/fireguard-2faea/us-central1/api/fire-risk/compute-by-location?lat=60.3913&lon=5.3221&points=12`
- Messaging publish:
  `http://127.0.0.1:5001/fireguard-2faea/us-central1/api/messaging/publish-fire-risk?lat=60.3913&lon=5.3221&points=12`

### Fire risk-beregningsflyt

Det finnes to hovedmåter å beregne fire risk på:
- ved å sende weather records direkte til `POST /fire-risk/compute`
- ved å forespørre en lokasjon via `GET /fire-risk/compute-by-location`

For lokasjonsbaserte forespørsler er flyten:
- sjekk Firestore-cache
- ved cache miss, hent MET-data
- transformer records til `frcm`-modellen
- beregn `ttf` og tilhørende output
- returner resultatet
- cache responsen

### Cache

Caching er implementert i `FireRiskCacheService` og bruker Firestore collection:

```text
fire_risk_cache
```

Cache-nøkkelen er basert på:
- avrundet breddegrad
- avrundet lengdegrad
- ønsket antall points
- gjeldende timeslot

Dette gjør at nesten identiske lokasjonsforespørsler innenfor samme tidsvindu kan gjenbruke cachede resultater.

### Messaging-arkitektur

Messaging-delen er bevisst holdt separat fra de synkrone fire risk-endepunktene.

Messaging-flyten er:
- en klient kaller `POST /messaging/publish-fire-risk`
- backend henter MET-data for ønsket lokasjon
- backend beregner fire risk med eksisterende beregningslogikk
- en event-payload opprettes
- eventet publiseres til Google Cloud Pub/Sub
- eventet logges i Firestore

Pub/Sub-topic:

```text
fire-risk-updated
```

Dette topic-navnet er konfigurert i `pubsub_publisher_service.py`.

Event-payloaden inneholder blant annet:
- `event_id`
- `event_type`
- `published_at`
- `location`
- `points`
- `forecast_start`
- `forecast_end`
- `ttf`
- `result`

Event-log collection i Firestore:

```text
fire_risk_event_log
```

### Forklaring av Pub/Sub-subscriber

Prosjektet bruker i dag:
- topic: `fire-risk-updated`
- subscription: `projects/fireguard-2faea/subscriptions/fire-risk-updated-sub`

Dette er nok til å forklare publish/subscribe-modellen:
- FireGuard publiserer til topic-et
- subscriptionen mottar meldingene
- en annen backend-tjeneste kunne konsumert dem uavhengig

Det betyr at messaging-kravet kan demonstreres uten å bygge en separat subscriber-tjeneste inne i dette repoet.

### Manuell testing

Eksempel på produksjonskall for messaging:

```bash
curl -i -X POST \
  -H "X-API-Key: DIN_API_NOKKEL" \
  -d '' \
  "https://us-central1-fireguard-2faea.cloudfunctions.net/api/messaging/publish-fire-risk?lat=60.3913&lon=5.3221&points=12"
```

Hvis dette lykkes, vil responsen inneholde `message_id` og `event`, og en ny melding skal dukke opp på Pub/Sub-subscriptionen.

### Scheduler-oppsett

Cloud Scheduler trenger ikke et eget batch-endepunkt i dette prosjektet. Den kan kalle det eksisterende publish-endepunktet direkte, på samme måte som det manuelle `curl`-kallet.

Anbefalt oppsett:
- opprett en Cloud Scheduler HTTP-jobb
- pek den til produksjonsendepunktet `/messaging/publish-fire-risk?lat=...&lon=...&points=...`
- bruk HTTP-metode `POST`
- send med `X-API-Key`

For demo-formål er et praktisk oppsett:
- opprett jobben med en gyldig schedule
- pause den
- resume ved behov
- bruk `Force run`
- pause den igjen etterpå

Dette demonstrerer både:
- hvordan jobben er konfigurert
- hvordan den samme jobben senere kan brukes til helautomatisk drift

### CI/CD

Python test-workflow:

```text
.github/workflows/python-tests.yml
```

Denne workflowen:
- setter opp Python 3.12
- installerer dependencies fra `functions/requirements.txt`
- kjører `pytest`

Functions deploy-workflow:

```text
.github/workflows/deploy-functions.yml
```

Denne workflowen:
- trigges på push til `main`
- bygger et Python virtual environment i `functions`
- installerer dependencies
- deployer Firebase Functions til prosjekt `fireguard-2faea`

### Notater om testing

Flere tester bruker `pytest.importorskip("frcm")`. Hvis `frcm` ikke er installert i Python-miljøet som brukes til testing, vil disse testene bli markert som `skipped`.

For lokal kjøring bør testene derfor kjøres med Python-interpreteren i `functions/venv`, for eksempel:

```bash
./functions/venv/Scripts/python -m pytest tests
```

### Notater til presentasjon

En enkel måte å forklare prosjektet på i presentasjon er:
- REST brukes til direkte oppslag og beregning
- Firestore brukes til cache og event-logging
- MET er kilden til værdata
- `frcm` brukes til fire risk-beregning
- Pub/Sub brukes til asynkron distribusjon av events
- Cloud Scheduler kan kalle publish-endepunktet automatisk ved behov

Dette gir en tydelig separasjon mellom:
- synkront API
- persistens/cache
- asynkron messaging
