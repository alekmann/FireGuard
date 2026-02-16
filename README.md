# FireGuard

## Initial planned software architecture
<img width="1136" height="737" alt="image" src="https://github.com/user-attachments/assets/00d6d53b-8a2d-4311-9e92-b797c3da58c1" />

## Local setup

cd functions
python -m venv venv
source venv/Scripts/activate  # Windows
pip install -r requirements.txt
cd ..
firebase emulators:start --only functions
