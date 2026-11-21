import json
import urllib.request
import urllib.error
from pathlib import Path

# Project ke main folder se .env read karo
env_file = Path(__file__).resolve().parent / ".env"

api_key = None

if env_file.exists():
    for line in env_file.read_text().splitlines():
        if line.strip().startswith("FREEMODEL_API_KEY="):
            api_key = line.split("=", 1)[1].strip().strip('"').strip("'")
            break

if not api_key:
    print("ERROR: .env file mein API key nahi mili.")

else:
    url = "https://freemodel.in/v1/models"

    request = urllib.request.Request(
        url,
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
    )

    try:
        with urllib.request.urlopen(request, timeout=30) as response:
            data = json.loads(response.read().decode("utf-8"))

        print("\nSUCCESS! FreeModel API connected.")
        print("\nAvailable Models:\n")

        for model in data.get("data", []):
            print(model.get("id"))

    except urllib.error.HTTPError as e:
        print("API Error:", e.code)
        print(e.read().decode("utf-8"))

    except Exception as e:
        print("Connection Failed:", e)