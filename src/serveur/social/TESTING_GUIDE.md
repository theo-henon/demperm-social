# 🧪 Guide de Test - Backend Demperm Social

Ce guide explique comment tester le backend et écrire de nouveaux tests.

---

## 🚀 Démarrage Rapide

### 1. Installer les dépendances

```bash
# Avec uv (recommandé)
uv sync

# Ou avec pip
pip install -r requirements.txt
```

### 2. Lancer Docker

```bash
docker-compose up -d
```

### 3. Appliquer les migrations

```bash
cd api
python manage.py migrate
python manage.py init_domains
```

### 4. Lancer le serveur

```bash
python manage.py runserver
```

### 5. Accéder à la documentation Swagger

Ouvrir dans le navigateur :
- **Swagger UI** : http://localhost:8000/api/v1/docs/
- **ReDoc** : http://localhost:8000/api/v1/redoc/

---

## 📖 Tester les Endpoints avec Swagger

### Étape 1 : Authentification

1. Aller sur http://localhost:8000/api/v1/docs/
2. Trouver l'endpoint `GET /api/v1/auth/google/url/`
3. Cliquer sur "Try it out" puis "Execute"
4. Copier l'URL retournée et l'ouvrir dans le navigateur
5. Se connecter avec Google
6. Récupérer le token JWT dans la réponse

### Étape 2 : Autoriser les requêtes

1. Cliquer sur le bouton "Authorize" en haut de la page Swagger
2. Entrer : `Bearer <votre_token_jwt>`
3. Cliquer sur "Authorize"

### Étape 3 : Tester les endpoints

Tous les endpoints sont maintenant accessibles ! Exemples :

- **GET /api/v1/users/me/** - Obtenir son profil
- **GET /api/v1/domains/** - Obtenir les 9 domaines
- **POST /api/v1/posts/create/** - Créer un post
- **GET /api/v1/posts/feed/** - Obtenir son feed

---

## 🧪 Écrire des Tests

### Structure des tests

```
api/tests/
├── conftest.py              # Fixtures pytest
├── unit/                    # Tests unitaires
│   ├── test_validators.py
│   ├── test_user_service.py
│   └── test_post_service.py
├── integration/             # Tests d'intégration
│   ├── test_auth_endpoints.py
│   ├── test_user_endpoints.py
│   └── test_post_endpoints.py
└── security/                # Tests de sécurité
    ├── test_rate_limiting.py
    └── test_permissions.py
```

### Exemple : Test unitaire pour un service

```python
# tests/unit/test_user_service.py
import pytest
from services.apps_services.user_service import UserService
from common.exceptions import NotFoundError

def test_get_user_by_id(db, user_factory):
    """Test getting a user by ID."""
    user = user_factory()
    
    result = UserService.get_user_by_id(str(user.user_id))
    
    assert result.user_id == user.user_id
    assert result.username == user.username

def test_get_user_by_id_not_found(db):
    """Test getting a non-existent user."""
    with pytest.raises(NotFoundError):
        UserService.get_user_by_id("00000000-0000-0000-0000-000000000000")

def test_block_user(db, user_factory):
    """Test blocking a user."""
    blocker = user_factory()
    blocked = user_factory()
    
    UserService.block_user(
        str(blocker.user_id),
        str(blocked.user_id),
        "127.0.0.1"
    )
    
    # Verify block was created
    blocked_users = UserService.get_blocked_users(str(blocker.user_id), 1, 20)
    assert len(blocked_users) == 1
    assert blocked_users[0].user_id == blocked.user_id
```

### Exemple : Test d'intégration pour un endpoint

```python
# tests/integration/test_user_endpoints.py
import pytest
from rest_framework.test import APIClient
from rest_framework import status

@pytest.mark.django_db
def test_get_current_user(authenticated_client, user):
    """Test GET /api/v1/users/me/"""
    response = authenticated_client.get('/api/v1/users/me/')
    
    assert response.status_code == status.HTTP_200_OK
    assert response.data['user_id'] == str(user.user_id)
    assert response.data['username'] == user.username

@pytest.mark.django_db
def test_update_profile(authenticated_client, user):
    """Test PATCH /api/v1/users/me/update/"""
    data = {
        'display_name': 'New Name',
        'bio': 'New bio'
    }
    
    response = authenticated_client.patch('/api/v1/users/me/update/', data)
    
    assert response.status_code == status.HTTP_200_OK
    assert response.data['profile']['display_name'] == 'New Name'
    assert response.data['profile']['bio'] == 'New bio'

@pytest.mark.django_db
def test_block_user(authenticated_client, user, other_user):
    """Test POST /api/v1/users/<id>/block/"""
    response = authenticated_client.post(f'/api/v1/users/{other_user.user_id}/block/')
    
    assert response.status_code == status.HTTP_204_NO_CONTENT
    
    # Verify user is blocked
    response = authenticated_client.get('/api/v1/users/me/blocked/')
    assert response.status_code == status.HTTP_200_OK
    assert len(response.data) == 1
```

### Exemple : Test de sécurité

```python
# tests/security/test_rate_limiting.py
import pytest
from rest_framework import status
import time

@pytest.mark.django_db
def test_rate_limiting_post_create(authenticated_client, subforum):
    """Test rate limiting on post creation."""
    data = {
        'title': 'Test Post',
        'content': 'Test content',
        'subforum_id': str(subforum.subforum_id)
    }
    
    # Make 10 requests (limit is 10/minute)
    for i in range(10):
        response = authenticated_client.post('/api/v1/posts/create/', data)
        assert response.status_code == status.HTTP_201_CREATED
    
    # 11th request should be rate limited
    response = authenticated_client.post('/api/v1/posts/create/', data)
    assert response.status_code == status.HTTP_429_TOO_MANY_REQUESTS

@pytest.mark.django_db
def test_banned_user_cannot_access(banned_user_client):
    """Test that banned users cannot access endpoints."""
    response = banned_user_client.get('/api/v1/users/me/')
    
    assert response.status_code == status.HTTP_403_FORBIDDEN
```

---

## 🔧 Fixtures Disponibles

Les fixtures suivantes sont disponibles dans `tests/conftest.py` :

- `user_factory` - Créer des utilisateurs
- `domain_factory` - Créer des domaines
- `forum_factory` - Créer des forums
- `subforum_factory` - Créer des sous-forums
- `post_factory` - Créer des posts
- `comment_factory` - Créer des commentaires
- `authenticated_client` - Client API authentifié
- `admin_client` - Client API admin
- `banned_user_client` - Client API utilisateur banni

---

## 🏃 Lancer les Tests

```bash
# Tous les tests
pytest

# Tests unitaires seulement
pytest tests/unit/

# Tests d'intégration seulement
pytest tests/integration/

# Tests de sécurité seulement
pytest tests/security/

# Avec couverture
pytest --cov=. --cov-report=html

# Verbose
pytest -v

# Arrêter au premier échec
pytest -x
```

---

## 📊 Couverture de Code

```bash
# Générer le rapport de couverture
pytest --cov=. --cov-report=html

# Ouvrir le rapport
open htmlcov/index.html
```

---

## ✅ Checklist des Tests à Écrire

### Services (10 fichiers)
- [ ] test_auth_service.py
- [ ] test_encryption_service.py
- [ ] test_user_service.py
- [ ] test_post_service.py
- [ ] test_comment_service.py
- [ ] test_domain_service.py
- [ ] test_forum_service.py
- [ ] test_follower_service.py
- [ ] test_message_service.py
- [ ] test_report_service.py

### Endpoints (10 fichiers)
- [ ] test_auth_endpoints.py
- [ ] test_user_endpoints.py
- [ ] test_post_endpoints.py
- [ ] test_comment_endpoints.py
- [ ] test_domain_endpoints.py
- [ ] test_forum_endpoints.py
- [ ] test_follower_endpoints.py
- [ ] test_message_endpoints.py
- [ ] test_report_endpoints.py
- [ ] test_admin_endpoints.py

### Sécurité (5 fichiers)
- [ ] test_rate_limiting.py
- [ ] test_permissions.py
- [ ] test_authentication.py
- [ ] test_validation.py
- [ ] test_encryption.py

---

## 🎯 Objectif

**Atteindre 80%+ de couverture de code** pour garantir la qualité du backend.

Bon courage ! 🚀

