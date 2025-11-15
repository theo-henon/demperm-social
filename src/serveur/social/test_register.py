#!/usr/bin/env python3
"""Test simple de l'endpoint de register"""
import requests
import json

response = requests.post(
    "http://localhost:8000/api/v1/auth/register",
    json={
        "username": "test9999",
        "email": "test9999@example.com",
        "password": "SecurePass123!",
        "password_confirm": "SecurePass123!",
        "display_name": "Test User"
    }
)

print(f"Status: {response.status_code}")
print(f"Content-Type: {response.headers.get('Content-Type')}")
print("\nResponse:")
if 'application/json' in response.headers.get('Content-Type', ''):
    print(json.dumps(response.json(), indent=2))
else:
    # Si c'est du HTML, essayons d'extraire l'erreur
    text = response.text
    if 'Exception Type' in text:
        lines = text.split('\n')
        for i, line in enumerate(lines):
            if 'Exception Type' in line or 'Exception Value' in line:
                print(lines[i:min(i+5, len(lines))])
    else:
        print(text[:500])
