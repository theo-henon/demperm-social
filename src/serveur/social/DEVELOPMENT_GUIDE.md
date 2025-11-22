# Guide de Développement - Backend Demperm Social

## 📋 État d'avancement du projet

### ✅ Complété

1. **Structure du projet** - Arborescence complète créée
2. **Configuration de base**
   - `pyproject.toml` avec toutes les dépendances
   - `.env.example` avec toutes les variables d'environnement
   - `.python-version` (Python 3.12)
   - `README.md` avec instructions

3. **Configuration Django**
   - `django/settings.py` complet (DB, Redis, JWT, CORS, etc.)
   - `conf/wsgi.py`, `conf/asgi.py`, `conf/urls.py`
   - `manage.py`

4. **Couche Base de Données (db/)**
   - ✅ Toutes les entités Django ORM créées :
     - `user_entity.py` (User, UserProfile, UserSettings, Block, Follow)
     - `domain_entity.py` (Domain, Forum, Subforum, Membership)
     - `post_entity.py` (Post, Comment, Like, Tag, PostTag, ForumTag)
     - `message_entity.py` (Message, Report, AuditLog)
   - ✅ Tous les repositories créés :
     - `user_repository.py`
     - `post_repository.py`
     - `domain_repository.py`
     - `message_repository.py`

5. **Utilitaires Communs (common/)**
   - ✅ `exceptions.py` - Exceptions personnalisées et handler
   - ✅ `validators.py` - Validation et sanitisation des entrées
   - ✅ `permissions.py` - Permissions personnalisées
   - ✅ `rate_limiters.py` - Rate limiting
   - ✅ `utils.py` - Fonctions utilitaires

6. **Docker**
   - ✅ `Dockerfile`
   - ✅ `docker-compose.yml` (PostgreSQL, Redis, API)
   - ✅ `docker-entrypoint.sh`

7. **Management Commands**
   - ✅ `init_domains.py` - Initialisation des 9 domaines

### 🚧 À compléter

Les éléments suivants doivent être implémentés pour avoir une API fonctionnelle :

#### 1. DTOs (Data Transfer Objects) - `api/dto/`

Créer les DTOs pour chaque entité :
- `user_dto.py`
- `post_dto.py`
- `comment_dto.py`
- `domain_dto.py`
- `forum_dto.py`
- `message_dto.py`
- etc.

#### 2. Modèles de Domaine - `api/domains/models/`

Créer les modèles métier (business logic) :
- `user.py`
- `post.py`
- `comment.py`
- etc.

#### 3. Services Métier - `api/services/apps_services/`

Implémenter les services pour chaque domaine :
- `auth_service.py` - Authentification OAuth2 + JWT
- `user_service.py` - Gestion des utilisateurs
- `post_service.py` - Gestion des posts
- `comment_service.py` - Gestion des commentaires
- `encryption_service.py` - Chiffrement E2E pour messages
- `domain_service.py` - Gestion des domaines
- `forum_service.py` - Gestion des forums
- `message_service.py` - Messagerie
- `report_service.py` - Signalements
- etc.

#### 4. Mappers - `api/services/mappers/`

Créer les mappers pour convertir entre DTO ↔ Domain ↔ Entity :
- `user_mapper.py`
- `post_mapper.py`
- etc.

#### 5. Applications Django (Endpoints) - `api/apps/`

Implémenter les views et serializers pour chaque app :

**apps/auth/**
- `serializers.py` - Serializers pour auth
- `views.py` - Views OAuth2 (login, callback, refresh, logout)
- `urls.py` - Routes

**apps/users/**
- `serializers.py`
- `views.py` - GET /me, PATCH /me, GET /{id}, POST /{id}/block, etc.
- `urls.py`

**apps/domains/**
- `serializers.py`
- `views.py` - GET /, GET /{id}, GET /{id}/subforums, POST /{id}/subforums/create
- `urls.py`

**apps/forums/**
- `serializers.py`
- `views.py` - GET /, POST /create, GET /{id}, GET /search, etc.
- `urls.py`

**apps/posts/**
- `serializers.py`
- `views.py` - POST /create, GET /{id}, DELETE /{id}/delete, POST /{id}/like, etc.
- `urls.py`

**apps/comments/**
- `serializers.py`
- `views.py` - GET /posts/{id}/comments, POST /posts/{id}/comments/create, etc.
- `urls.py`

**apps/likes/**
- `serializers.py`
- `views.py`
- `urls.py`

**apps/followers/**
- `serializers.py`
- `views.py` - GET /me, POST /{id}/request, POST /{id}/accept, etc.
- `urls.py`

**apps/tags/**
- `serializers.py`
- `views.py`
- `urls.py`

**apps/messages/**
- `serializers.py`
- `views.py` - GET /, GET /{user_id}, POST /{user_id}/create (avec E2E)
- `urls.py`

**apps/reports/**
- `serializers.py`
- `views.py` - POST /create
- `urls.py`

**apps/admin_panel/**
- `serializers.py`
- `views.py` - GET /reports, POST /reports/{id}/resolve, POST /users/{id}/ban, etc.
- `urls.py`

#### 6. Tests - `api/tests/`

Créer les tests :
- `unit/` - Tests unitaires pour services, validators, etc.
- `integration/` - Tests d'intégration pour les endpoints
- `security/` - Tests de sécurité (rate limiting, permissions, etc.)

#### 7. CI/CD - `.github/workflows/`

Créer le workflow GitHub Actions :
- `ci.yml` - Build, tests, linting

## 🔧 Prochaines étapes recommandées

### Étape 1 : Créer les DTOs et Serializers

Commencez par créer les DTOs et serializers Django REST Framework pour structurer les données.

### Étape 2 : Implémenter le service d'authentification

Le service d'authentification est critique. Implémentez :
1. `auth_service.py` avec les méthodes OAuth2
2. `apps/auth/views.py` avec les endpoints
3. Testez l'authentification Google

### Étape 3 : Implémenter les services de base

Dans cet ordre :
1. User service
2. Domain service
3. Forum service
4. Post service
5. Comment service
6. Message service (avec encryption_service)

### Étape 4 : Créer les endpoints

Pour chaque service, créez les endpoints correspondants dans les apps.

### Étape 5 : Tests

Écrivez les tests au fur et à mesure de l'implémentation.

## 📝 Notes importantes

1. **Chiffrement E2E** : Pour la messagerie, utilisez la bibliothèque `cryptography` :
   - AES-256 pour chiffrer le contenu
   - RSA-2048 pour chiffrer les clés symétriques
   - Stocker les clés chiffrées pour sender et receiver

2. **Rate Limiting** : Utilisez les décorateurs dans `common/rate_limiters.py`

3. **Validation** : Utilisez les validators dans `common/validators.py`

4. **Permissions** : Utilisez les permissions dans `common/permissions.py`

5. **Audit Logging** : Loggez toutes les actions critiques dans AuditLog

## 🚀 Démarrage rapide

```bash
# Copier .env.example vers .env et configurer
cp .env.example .env

# Lancer avec Docker
docker-compose up -d

# Ou en local
uv venv
source .venv/bin/activate
uv pip install -e ".[dev]"
cd api
python manage.py migrate
python manage.py init_domains
python manage.py runserver
```

