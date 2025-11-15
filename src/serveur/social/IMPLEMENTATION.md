# Backend Social - Documentation d'Implémentation

**Version:** 1.0  
**Date:** Novembre 2025  
**Framework:** Django 5.2.7 + Django REST Framework  
**Base de données:** SQLite (dev) / PostgreSQL (production recommandée)

---

## Vue d'ensemble

Cette implémentation suit rigoureusement les spécifications définies dans `Specifications.md`. Le backend est conçu avec une approche **security-first**, utilisant des UUIDs pour tous les identifiants publics, une authentification JWT robuste, et des contrôles de confidentialité stricts.

### Choix de schéma de base de données

Après analyse de `db.md` et de la section 5 de `Specifications.md`, nous avons choisi le schéma de `Specifications.md` car il offre:

- **UUIDs publics** pour tous les identifiants exposés via API (anti-énumération)
- **Champs de confidentialité** intégrés au modèle User
- **Soft delete** pour les posts et conversations (conformité RGPD)
- **Signature HMAC** pour l'intégrité du contenu
- **AuditLog append-only** pour la traçabilité
- **Token refresh avec révocation** pour la sécurité JWT

---

## Architecture

### Structure du projet

```
social_api/
├── core/                          # Application principale (nouveau)
│   ├── models.py                  # Tous les modèles de données
│   ├── serializers.py             # Sérialiseurs DRF avec validation
│   ├── permissions.py             # Permissions personnalisées
│   ├── validators.py              # Validation et sanitisation
│   ├── middleware.py              # Rate limiting
│   ├── authentication.py          # Backend JWT personnalisé
│   ├── auth_views.py              # Endpoints d'authentification
│   ├── views_users.py             # Endpoints utilisateurs
│   ├── views_followers.py         # Endpoints followers/following
│   ├── views_posts.py             # Endpoints posts
│   ├── views_messages.py          # Endpoints messages
│   ├── views_forums.py            # Endpoints forums/tags
│   ├── urls.py                    # Configuration des URLs
│   └── admin.py                   # Configuration Django Admin
│
├── social_api/                    # Configuration Django
│   ├── settings.py                # Paramètres (JWT, Redis, etc.)
│   └── urls.py                    # URLs principales
│
└── manage.py
```

### Modèles de données

Tous les modèles utilisent des **UUIDs v4** comme identifiants publics (`public_uuid`) pour prévenir l'énumération. Les IDs auto-incrémentaux restent utilisés en interne (clés primaires).

#### Modèles principaux

1. **User** (extension de `AbstractUser`)
   - Champs: `username`, `email`, `display_name`, `bio`, `avatar_url`
   - Confidentialité: `profile_visibility`, `posts_visibility`, `allow_messages_from`
   - Rôles: `roles` (JSON field: `['user', 'moderator', 'admin', 'elected_official']`)

2. **FollowerRequest**
   - Demandes de suivi (pending/accepted/refused)
   - Contraintes: pas d'auto-follow, unicité requester+target

3. **Follower**
   - Relations de suivi validées (après acceptation)
   - Contraintes: pas d'auto-follow, unicité follower+following

4. **Post**
   - Champs: `title`, `content`, `visibility`, `subforum`, `tags`
   - Intégrité: `version`, `signature` (HMAC-SHA256)
   - Soft delete: `deleted_at`, `deleted_by`

5. **Conversation**
   - Messages 1:1 entre deux utilisateurs
   - Contraintes: ordre canonique (participant1 < participant2)

6. **Message**
   - Messages dans une conversation
   - Champs: `content`, `is_read`, `sent_at`

7. **Forum**
   - Forums/sous-forums pour discussions
   - Visibilité: public/private

8. **Tag**
   - Tags pour catégoriser les posts
   - Contraintes: lowercase, alphanumeric + underscore

9. **AuditLog**
   - Journal d'audit append-only
   - Traçabilité: `event_type`, `actor`, `target_type`, `ip_address`

10. **RefreshToken**
    - Tokens de rafraîchissement avec révocation

---

## Sécurité

### Authentification JWT

**Implémentation:**
- **Access Token**: 15 minutes, contient `user_id`, `roles`, `exp`
- **Refresh Token**: 7 jours, stocké en DB avec révocation
- **Rotation**: nouveau refresh token à chaque utilisation

**Endpoints:**
```
POST /api/v1/auth/login       → access_token + refresh_token
POST /api/v1/auth/refresh     → nouveau access_token + refresh_token
POST /api/v1/auth/logout      → révoque le refresh_token
POST /api/v1/auth/register    → crée un compte + retourne tokens
```

**Backend d'authentification:**
```python
# Dans settings.py
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'core.authentication.JWTAuthentication',
    ],
}
```

**Header requis:**
```
Authorization: Bearer <access_token>
```

### Permissions

Permissions personnalisées implémentées dans `core/permissions.py`:

1. **IsOwner**: vérifie que l'utilisateur est propriétaire de la ressource
2. **IsOwnerOrModerator**: propriétaire OU modérateur/admin
3. **IsParticipant**: vérifie participation à une conversation
4. **PrivacyGuard**: applique les politiques de confidentialité (profils, posts)
5. **IsModerator**: modérateurs et admins uniquement
6. **IsAdmin**: admins uniquement

**Exemple d'utilisation:**
```python
class PostDeleteView(APIView):
    permission_classes = [IsAuthenticated, IsOwnerOrModerator]
    
    def delete(self, request, uuid):
        # Check permission automatically via DRF
        ...
```

### Confidentialité

**PrivacyGuard** implémente la logique de visibilité:

**Profils utilisateurs:**
- `private`: uniquement owner et modérateurs
- `followers`: followers + owner + modérateurs
- `public`: tout le monde authentifié

**Posts:**
- `hidden`: uniquement auteur et modérateurs
- `followers`: followers de l'auteur + auteur + modérateurs
- `public`: tout le monde authentifié

**Graphe social:**
- Toujours caché (`social_graph_visibility='hidden'` non modifiable)
- Endpoints `/followers/me` et `/following/me` accessibles uniquement par l'owner
- Pas de `/users/{uuid}/followers` (n'existe pas)

### Anti-énumération

Mesures implémentées:

1. **UUIDs**: impossibles à deviner/énumérer
2. **Messages génériques**: "Ressource non disponible" pour 403/404 identiques
3. **Temps de réponse constant**: padding temporel dans `/users/search` et `/followers/request`
4. **Validation minimale**: requêtes < 3 chars retournent `[]` sans erreur

**Exemple:**
```python
# POST /api/v1/followers/{uuid}/request
# Retourne TOUJOURS 200 "Demande traitée" même si UUID inexistant
def post(self, request, uuid):
    start_time = time.time()
    # ... logique ...
    self._pad_response_time(start_time, 0.12)  # Temps constant
    return Response({'message': 'Demande traitée'}, status=200)
```

### Validation et sanitisation

Implémentées dans `core/validators.py`:

**Validation:**
- Username: `^[a-zA-Z0-9_]{3,30}$`, pas de mots réservés
- Post title: `^[\w\s.,!?'\-]{1,200}$`
- Post content: 1-10000 chars
- Message: 1-2000 chars, pas de HTML
- Tag: `^[a-z0-9_]{3,30}$` (lowercase)

**Sanitisation HTML:**
- Bio: autorise `<b>`, `<i>`, `<a>` uniquement
- Post content: autorise `<p>`, `<br>`, `<b>`, `<i>`, `<ul>`, `<ol>`, `<li>`, `<a>`
- Strip: `<script>`, `<iframe>`, `on*` attributes, `javascript:` URLs

**Détection de spam:**
```python
def detect_spam(content):
    # Vérifie: URLs excessives, ALL CAPS, répétitions
    ...
```

### Rate Limiting

Implémenté via middleware Redis (`core/middleware.py`):

**Limites configurées (requêtes/période):**
```python
'POST:/api/v1/auth/login': (5, 900),           # 5 / 15 min
'POST:/api/v1/posts/create': (10, 3600),       # 10 / heure
'GET:/api/v1/users/search': (100, 3600),       # 100 / heure
'POST:/api/v1/messages/': (50, 3600),          # 50 / heure
# ... voir middleware.py pour liste complète
```

**Headers de réponse:**
```
X-RateLimit-Limit: 100
X-RateLimit-Remaining: 42
X-RateLimit-Reset: 1699876543
```

**Réponse 429:**
```json
{
  "error": "Rate limit exceeded",
  "retry_after": 3600
}
```

**Violations:** loggées dans `AuditLog` pour analyse.

### Intégrité du contenu

Signature HMAC-SHA256 pour les posts:

```python
# Génération à la création
def generate_signature(self, secret_key):
    payload = f"{self.content}|{self.created_at}|{self.author_id}|{self.version}"
    return hmac.new(secret_key.encode(), payload.encode(), hashlib.sha256).hexdigest()

# Vérification
def verify_signature(self, secret_key):
    expected = self.generate_signature(secret_key)
    return hmac.compare_digest(self.signature, expected)
```

**Utilisation:**
- Signature générée automatiquement à la création/modification
- Incluse dans toutes les réponses API
- Permet de détecter modifications non autorisées

---

## API Endpoints

### Authentification

| Méthode | Endpoint | Description | Auth |
|---------|----------|-------------|------|
| POST | `/api/v1/auth/register` | Créer un compte | Public |
| POST | `/api/v1/auth/login` | Se connecter | Public |
| POST | `/api/v1/auth/refresh` | Rafraîchir access token | Public |
| POST | `/api/v1/auth/logout` | Se déconnecter | JWT |

### Utilisateurs

| Méthode | Endpoint | Description | Permissions |
|---------|----------|-------------|-------------|
| GET | `/api/v1/users/me` | Mon profil complet | IsAuthenticated |
| PATCH | `/api/v1/users/me` | Modifier mon profil | IsAuthenticated |
| PATCH | `/api/v1/users/me/settings` | Modifier confidentialité | IsAuthenticated |
| GET | `/api/v1/users/{uuid}` | Profil public d'un user | IsAuthenticated + PrivacyGuard |
| GET | `/api/v1/users/search?query=...` | Rechercher users | IsAuthenticated |
| GET | `/api/v1/users/bulk?ids=...` | Récupérer plusieurs users | IsAuthenticated |
| GET | `/api/v1/users/discover` | Découvrir users | IsAuthenticated |

### Followers

| Méthode | Endpoint | Description | Permissions |
|---------|----------|-------------|-------------|
| GET | `/api/v1/followers/me` | Mes followers | IsAuthenticated |
| GET | `/api/v1/following/me` | Qui je suis | IsAuthenticated |
| GET | `/api/v1/followers/requests` | Demandes reçues | IsAuthenticated |
| POST | `/api/v1/followers/{uuid}/request` | Envoyer demande | IsAuthenticated |
| POST | `/api/v1/followers/{uuid}/accept` | Accepter demande | IsAuthenticated + IsOwner |
| POST | `/api/v1/followers/{uuid}/refuse` | Refuser demande | IsAuthenticated + IsOwner |
| DELETE | `/api/v1/following/{uuid}/unfollow` | Se désabonner | IsAuthenticated |

### Posts

| Méthode | Endpoint | Description | Permissions |
|---------|----------|-------------|-------------|
| POST | `/api/v1/posts/create` | Créer un post | IsAuthenticated |
| GET | `/api/v1/posts/{uuid}` | Détails d'un post | IsAuthenticated + PrivacyGuard |
| PATCH | `/api/v1/posts/{uuid}/update` | Modifier son post | IsAuthenticated + IsOwner |
| DELETE | `/api/v1/posts/{uuid}/delete` | Supprimer post | IsAuthenticated + IsOwnerOrModerator |
| GET | `/api/v1/posts/feed` | Fil personnalisé | IsAuthenticated |
| GET | `/api/v1/posts/discover` | Découvrir posts publics | IsAuthenticated |

### Messages

| Méthode | Endpoint | Description | Permissions |
|---------|----------|-------------|-------------|
| GET | `/api/v1/messages/` | Mes conversations | IsAuthenticated |
| GET | `/api/v1/messages/{uuid}` | Messages d'une conv | IsAuthenticated + IsParticipant |
| POST | `/api/v1/messages/{uuid}/create` | Envoyer message | IsAuthenticated |
| DELETE | `/api/v1/messages/{uuid}/delete` | Masquer conversation | IsAuthenticated + IsParticipant |

### Forums

| Méthode | Endpoint | Description | Permissions |
|---------|----------|-------------|-------------|
| GET | `/api/v1/forums/` | Lister forums publics | IsAuthenticated |
| POST | `/api/v1/forums/create` | Créer un forum | IsAuthenticated + IsAdmin |
| GET | `/api/v1/forums/{uuid}` | Détails d'un forum | IsAuthenticated |
| POST | `/api/v1/subscriptions/forums/{uuid}` | S'abonner | IsAuthenticated |
| DELETE | `/api/v1/subscriptions/forums/{uuid}/unsubscribe` | Se désabonner | IsAuthenticated |

### Tags

| Méthode | Endpoint | Description | Permissions |
|---------|----------|-------------|-------------|
| GET | `/api/v1/tags/` | Lister tous les tags | IsAuthenticated |
| POST | `/api/v1/tags/create` | Créer un tag | IsAuthenticated + IsModerator |
| POST | `/api/v1/tags/assign/{post_uuid}` | Assigner tags à post | IsAuthenticated + IsOwner |
| POST | `/api/v1/tags/unassign/{post_uuid}` | Retirer tags | IsAuthenticated + IsOwner |
| DELETE | `/api/v1/tags/delete` | Supprimer tag | IsAuthenticated + IsAdmin |

---

## Installation et déploiement

### Prérequis

- Python 3.12+
- Redis (pour rate limiting et cache)
- PostgreSQL (production) ou SQLite (dev)

### Installation

```bash
cd src/serveur/social

# Installer les dépendances
pip install -e .

# Ou avec uv
uv pip install -e .
```

### Configuration

1. **Secrets de production:**

Dans `settings.py`, générer une nouvelle `SECRET_KEY` pour production:
```python
# NE PAS utiliser la clé par défaut en production!
SECRET_KEY = os.environ.get('DJANGO_SECRET_KEY', 'changeme')
```

2. **Base de données:**

Pour PostgreSQL en production:
```python
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': os.environ.get('DB_NAME'),
        'USER': os.environ.get('DB_USER'),
        'PASSWORD': os.environ.get('DB_PASSWORD'),
        'HOST': os.environ.get('DB_HOST', 'localhost'),
        'PORT': os.environ.get('DB_PORT', '5432'),
    }
}
```

3. **Redis:**

```python
CACHES = {
    'default': {
        'BACKEND': 'django_redis.cache.RedisCache',
        'LOCATION': os.environ.get('REDIS_URL', 'redis://127.0.0.1:6379/1'),
        ...
    }
}
```

### Migrations

```bash
cd social_api

# Créer les migrations
python manage.py makemigrations core

# Appliquer les migrations
python manage.py migrate

# Créer un superutilisateur
python manage.py createsuperuser
```

### Démarrage

```bash
# Développement
python manage.py runserver

# Production (avec gunicorn)
pip install gunicorn
gunicorn social_api.wsgi:application --bind 0.0.0.0:8000
```

### Premier utilisateur admin

```python
python manage.py shell

from core.models import User
user = User.objects.create_user(
    username='admin',
    email='admin@example.com',
    password='changeme'
)
user.roles = ['user', 'admin', 'moderator']
user.is_staff = True
user.is_superuser = True
user.save()
```

---

## Tests

### Créer des données de test

```python
python manage.py shell

from core.models import User, Tag, Forum, Post

# Créer utilisateurs
alice = User.objects.create_user('alice', 'alice@example.com', 'password123')
bob = User.objects.create_user('bob', 'bob@example.com', 'password123')

alice.display_name = 'Alice Dupont'
alice.profile_visibility = 'public'
alice.save()

# Créer tags
tag1 = Tag.objects.create(name='politique')
tag2 = Tag.objects.create(name='environnement')

# Créer forum
forum = Forum.objects.create(
    name='Débat Public',
    description='Forum de discussion générale',
    created_by=alice,
    visibility='public'
)

# Créer post
post = Post.objects.create(
    author=alice,
    title='Mon premier post',
    content='Contenu du post...',
    visibility='public'
)
post.tags.add(tag1)
```

### Tester l'authentification

```bash
# Créer un compte
curl -X POST http://localhost:8000/api/v1/auth/register \
  -H "Content-Type: application/json" \
  -d '{"username": "testuser", "email": "test@example.com", "password": "testpass123", "password_confirm": "testpass123"}'

# Se connecter
curl -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username": "testuser", "password": "testpass123"}'

# Utiliser le token
export TOKEN="<access_token>"

curl -X GET http://localhost:8000/api/v1/users/me \
  -H "Authorization: Bearer $TOKEN"
```

### Tests unitaires

À implémenter (non inclus dans cette version):
- Tests de permissions
- Tests de validation
- Tests de rate limiting
- Tests d'intégrité de contenu

---

## Conformité RGPD

### Données personnelles

**Collectées:**
- Email (obligatoire, vérification recommandée)
- Username (public)
- Display name (optionnel)
- Bio (optionnel)
- IP addresses (audit logs uniquement)

**Non collectées:**
- Données sensibles (religion, orientation politique explicite)
- Données de localisation précise

### Droit à l'oubli

**Soft delete implémenté:**
- Posts: `deleted_at` (masqués, non supprimés)
- Conversations: table `ConversationDeletion` (masquées par utilisateur)

**Procédure de suppression complète:**
1. Anonymiser les `AuditLog` (remplacer `actor_id` par `NULL`)
2. Supprimer physiquement les posts/messages après période de rétention
3. Supprimer l'utilisateur

**À implémenter:**
- Endpoint `/api/v1/users/me/delete-account` (demande de suppression)
- Tâche cron pour anonymisation après 30 jours

### Audit Trail

**AuditLog conservé 2 ans minimum.**

Types d'événements loggés:
- `auth.*`: login, logout, register, failed login
- `post.*`: create, update, delete
- `message.send`
- `follower.*`: request, accept, refuse, unfollow
- `rate_limit.exceeded`

**Requête exemple:**
```python
# Logs d'un utilisateur
AuditLog.objects.filter(actor=user).order_by('-created_at')

# Logs d'un type d'événement
AuditLog.objects.filter(event_type='post.delete')
```

---

## Optimisations recommandées

### Indexation

Tous les index critiques sont définis dans les modèles:
```python
class Meta:
    indexes = [
        models.Index(fields=['public_uuid']),
        models.Index(fields=['author', '-created_at']),
        ...
    ]
```

### Caching

**À implémenter:**
- Cache des listes following/followers (Redis)
- Cache du feed personnalisé (5 minutes)
- Cache des profils publics (10 minutes)

**Exemple:**
```python
from django.core.cache import cache

def get_user_following(user):
    cache_key = f'following:{user.id}'
    following = cache.get(cache_key)
    if not following:
        following = list(Follower.objects.filter(follower=user).values_list('following_id', flat=True))
        cache.set(cache_key, following, 300)  # 5 min
    return following
```

### Pagination

**Cursor-based pagination configurée:**
```python
REST_FRAMEWORK = {
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.CursorPagination',
    'PAGE_SIZE': 20,
}
```

**Avantages:**
- Performance constante
- Pas de duplication avec données changeantes
- Pas de "page shift" lors d'ajouts

### Requêtes N+1

**Utiliser select_related/prefetch_related:**
```python
# Dans les vues
posts = Post.objects.filter(...).select_related('author').prefetch_related('tags')
conversations = Conversation.objects.filter(...).select_related('participant1', 'participant2')
```

---

## Sécurité en production

### Checklist

- [ ] Changer `SECRET_KEY` (variable d'environnement)
- [ ] Changer `CONTENT_INTEGRITY_SECRET` (séparé de SECRET_KEY)
- [ ] `DEBUG = False`
- [ ] Configurer `ALLOWED_HOSTS`
- [ ] Utiliser HTTPS uniquement (TLS 1.3+)
- [ ] Configurer CORS correctement
- [ ] Limiter accès admin à IPs spécifiques
- [ ] Activer logging vers fichiers/Sentry
- [ ] Backup régulier de la DB et Redis
- [ ] Monitoring rate limiting (alertes si violations massives)
- [ ] Rotation des secrets (tokens, clés)

### Headers de sécurité

```python
# settings.py
SECURE_SSL_REDIRECT = True
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
SECURE_HSTS_SECONDS = 31536000
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True
X_FRAME_OPTIONS = 'DENY'
SECURE_CONTENT_TYPE_NOSNIFF = True
```

### Monitoring

**Métriques recommandées:**
- Nombre de violations rate limit par endpoint
- Temps de réponse p95/p99
- Tentatives de login échouées par IP
- Nombre de posts/messages créés par heure
- Taille de la base de données
- Utilisation Redis

**Outils:**
- Django Debug Toolbar (dev)
- Sentry (erreurs)
- Prometheus + Grafana (métriques)
- ELK Stack (logs)

---

## Différences avec l'implémentation existante

L'ancienne implémentation (apps `users`, `posts`, `messages`, etc.) utilisait:
- IDs auto-incrémentaux exposés (énumération possible)
- Pas de JWT (Basic Auth)
- Pas de rate limiting
- Pas de privacy guards
- Pas de validation HTML
- Pas d'audit logs

La nouvelle implémentation (`core`) corrige tous ces problèmes tout en gardant la compatibilité des URLs (préfixe `/api/v1/`).

**Migration recommandée:**
1. Tester la nouvelle API en parallèle
2. Migrer les clients progressivement
3. Supprimer les anciennes apps après validation complète

---

## Support et contribution

### Structure de commit recommandée

```
feat(auth): add JWT token rotation
fix(posts): sanitize HTML in content
security(rate-limit): add IP-based throttling
docs(api): update endpoint documentation
```

### Issues connues

- [ ] Pagination cursor dans toutes les vues (actuellement simplifiée)
- [ ] Tests unitaires complets
- [ ] Documentation OpenAPI/Swagger à jour
- [ ] Notifications temps réel (WebSocket/SSE)
- [ ] Export RGPD des données personnelles
- [ ] Modération avancée (système de signalement)

---

## Licence

Voir fichier `LICENSE` à la racine du projet.

---

**Fin du document d'implémentation**
