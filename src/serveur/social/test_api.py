#!/usr/bin/env python3
"""
Script de test simple pour l'API sociale
"""
import requests
import json
from pprint import pprint

BASE_URL = "http://localhost:8000/api/v1"

def print_response(title, response):
    print(f"\n{'='*60}")
    print(f"{title}")
    print(f"{'='*60}")
    print(f"Status: {response.status_code}")
    try:
        pprint(response.json())
    except:
        print(response.text)

def test_api():
    session = requests.Session()
    
    # 1. Test de création de compte
    print("\n🧪 Test 1: Création de compte")
    import random
    username = f"testuser{random.randint(1000, 9999)}"
    register_data = {
        "username": username,
        "email": f"test{random.randint(1000, 9999)}@example.com",
        "password": "SecurePass123!",
        "password_confirm": "SecurePass123!",
        "display_name": "Test User"
    }
    r = session.post(f"{BASE_URL}/auth/register", json=register_data)
    print_response("Register", r)
    
    if r.status_code != 201:
        print("❌ Échec de la création de compte")
        return
    
    # 2. Test de login
    print("\n🧪 Test 2: Login")
    login_data = {
        "username": username,
        "password": "SecurePass123!"
    }
    r = session.post(f"{BASE_URL}/auth/login", json=login_data)
    print_response("Login", r)
    
    if r.status_code != 200:
        print("❌ Échec du login")
        return
    
    tokens = r.json()
    access_token = tokens.get("access_token")
    headers = {"Authorization": f"Bearer {access_token}"}
    
    # 3. Test de récupération du profil
    print("\n🧪 Test 3: GET /users/me")
    r = session.get(f"{BASE_URL}/users/me", headers=headers)
    print_response("User Profile", r)
    
    if r.status_code != 200:
        print("❌ Échec de récupération du profil")
        return
    
    user_data = r.json()
    user_uuid = user_data.get("id")
    
    # 4. Test de mise à jour du profil
    print("\n🧪 Test 4: PATCH /users/me")
    update_data = {
        "bio": "Ceci est ma bio de test!",
        "profile_visibility": "public"
    }
    r = session.patch(f"{BASE_URL}/users/me", json=update_data, headers=headers)
    print_response("Update Profile", r)
    
    # 5. Test de récupération des settings
    print("\n🧪 Test 5: GET /users/me/settings")
    r = session.get(f"{BASE_URL}/users/me/settings", headers=headers)
    print_response("User Settings", r)
    
    # 6. Test de recherche d'utilisateur
    print("\n🧪 Test 6: GET /users/search?q=test")
    r = session.get(f"{BASE_URL}/users/search?q=test", headers=headers)
    print_response("User Search", r)
    
    # 7. Test de création d'un post
    print("\n🧪 Test 7: POST /posts/create")
    post_data = {
        "content": "Ceci est mon premier post de test!",
        "visibility": "public"
    }
    r = session.post(f"{BASE_URL}/posts/create", json=post_data, headers=headers)
    print_response("Create Post", r)
    
    # 8. Test de récupération du feed
    print("\n🧪 Test 8: GET /posts/feed")
    r = session.get(f"{BASE_URL}/posts/feed", headers=headers)
    print_response("Feed", r)
    
    # 9. Test de refresh token
    print("\n🧪 Test 9: POST /auth/refresh")
    refresh_data = {
        "refresh_token": tokens.get("refresh_token")
    }
    r = session.post(f"{BASE_URL}/auth/refresh", json=refresh_data)
    print_response("Refresh Token", r)
    
    # 10. Test de logout
    print("\n🧪 Test 10: POST /auth/logout")
    r = session.post(f"{BASE_URL}/auth/logout", headers=headers)
    print_response("Logout", r)
    
    print("\n✅ Tests terminés!")

if __name__ == "__main__":
    test_api()
