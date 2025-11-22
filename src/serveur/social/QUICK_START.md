# 🚀 Quick Start - Backend Demperm Social

## Démarrage rapide en 5 minutes

### 1. Prérequis

Assurez-vous d'avoir installé :
- Docker et docker-compose
- Git

### 2. Configuration

```bash
# Copier le fichier d'environnement
cp .env.example .env

# Éditer .env et configurer au minimum :
# - DJANGO_SECRET_KEY (générer une clé aléatoire)
# - GOOGLE_CLIENT_ID (obtenir depuis Google Cloud Console)
# - GOOGLE_CLIENT_SECRET (obtenir depuis Google Cloud Console)
nano .env
```

### 3. Lancer l'application

```bash
# Lancer tous les services (PostgreSQL, Redis, API)
docker-compose up -d

# Vérifier que tout fonctionne
docker-compose logs -f api
```

### 4. Initialiser la base de données

```bash
# Les migrations et l'initialisation des domaines se font automatiquement
# au démarrage du conteneur via docker-entrypoint.sh

# Pour vérifier que les 9 domaines sont créés :
docker-compose exec api python manage.py shell
>>> from db.entities.domain_entity import Domain
>>> Domain.objects.count()
9
>>> exit()
```

### 5. Tester l'API

L'API est maintenant accessible sur :
- **API Base URL** : http://localhost:8000/api/v1/
- **Swagger UI** : http://localhost:8000/api/v1/docs/
- **ReDoc** : http://localhost:8000/api/v1/redoc/

### 6. Tester l'authentification

```bash
# Obtenir l'URL d'authentification Google
curl -X POST http://localhost:8000/api/v1/auth/google/url/ \
  -H "Content-Type: application/json" \
  -d '{"redirect_uri": "http://localhost:3000/auth/callback"}'

# Réponse :
# {
#   "auth_url": "https://accounts.google.com/o/oauth2/v2/auth?...",
#   "state": "..."
# }
```

## 🔧 Développement local (sans Docker)

### 1. Installer les dépendances

```bash
# Installer uv
curl -LsSf https://astral.sh/uv/install.sh | sh

# Créer l'environnement virtuel
uv venv
source .venv/bin/activate

# Installer les dépendances
uv pip install -e ".[dev]"
```

### 2. Lancer PostgreSQL et Redis

```bash
# Avec Docker
docker-compose up -d postgres redis

# Ou installer localement
# PostgreSQL : https://www.postgresql.org/download/
# Redis : https://redis.io/download
```

### 3. Configurer et lancer

```bash
# Copier .env
cp .env.example .env

# Éditer .env avec les bonnes valeurs
nano .env

# Appliquer les migrations
cd api
python manage.py migrate

# Initialiser les domaines
python manage.py init_domains

# Lancer le serveur
python manage.py runserver
```

## 🧪 Lancer les tests

```bash
# Tous les tests
pytest

# Avec couverture
pytest --cov

# Tests spécifiques
pytest api/tests/unit/
pytest -m unit
```

## 📝 Prochaines étapes

1. **Lire la documentation** :
   - `README.md` - Vue d'ensemble
   - `DEVELOPMENT_GUIDE.md` - Guide de développement détaillé
   - `IMPLEMENTATION_STATUS.md` - État d'avancement

2. **Compléter l'implémentation** :
   - Implémenter les services métier manquants
   - Créer les endpoints REST pour chaque app
   - Écrire les tests

3. **Configurer Google OAuth2** :
   - Créer un projet sur Google Cloud Console
   - Activer l'API Google+ 
   - Créer des credentials OAuth2
   - Ajouter les redirect URIs autorisés

## 🆘 Problèmes courants

### Le conteneur API ne démarre pas

```bash
# Vérifier les logs
docker-compose logs api

# Reconstruire l'image
docker-compose build api
docker-compose up -d api
```

### Erreur de connexion à PostgreSQL

```bash
# Vérifier que PostgreSQL est bien démarré
docker-compose ps postgres

# Redémarrer PostgreSQL
docker-compose restart postgres
```

### Erreur de migration

```bash
# Réinitialiser la base de données
docker-compose down -v
docker-compose up -d
```

## 📚 Ressources

- **Django Documentation** : https://docs.djangoproject.com/
- **DRF Documentation** : https://www.django-rest-framework.org/
- **Google OAuth2** : https://developers.google.com/identity/protocols/oauth2
- **Specifications3.md** : Spécifications complètes du projet

