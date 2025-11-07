# Demperm - Social

## Structure du projet

```plaintext
demperm/src/serveur/social
│   .gitignore
│   .python-version
│   pyproject.toml
│   README.md
│   uv.lock
│   Dockerfile
│
│
└───api
    │   manage.py
    │   __init__.py
    │
    ├─── apps
    │   │
    │   ├─── comments
    │   │       urls.py
    │   │       views.py
    │   │       __init__.py
    │   │
    │   ├─── domains
    │   │       urls.py
    │   │       views.py
    │   │       __init__.py
    │   │
    │   ├───followers
    │   │       urls.py
    │   │       views.py
    │   │       __init__.py
    │   │
    │   ├───forums
    │   │       urls.py
    │   │       views.py
    │   │       __init__.py
    │   │
    │   ├───messages
    │   │       urls.py
    │   │       views.py
    │   │       __init__.py
    │   │
    │   ├─── posts
    │   │       urls.py
    │   │       views.py
    │   │       __init__.py
    │   │
    │	├───subscriptions
    │   │       urls.py
    │   │       views.py
    │   │       __init__.py
    │   │
    │   ├───tags
    │   │       urls.py
    │   │       views.py
    │   │       __init__.py
    │   │
    │   ├───users
    │   │       urls.py
    │   │       views.py
    │   │       __init__.py
    │
    ├─── django
    │       settings.py
    │
    ├───conf
    │       asgi.py
    │       urls.py
    │       wsgi.py
    │       __init__.py
    │
    ├─── domains
    │   │
    │   ├───models
    │
    ├─── db
    │   │
    │   ├───entities
    │   │   │
    │   │   ├───…
    │   ├───config
    │   ├───...
    │
    ├─── services
    │   │
    │   ├───apps_services
    │   │   
    │   ├───mappers
    │
    ├─── dto
    │
    ├───common
    │       utils.py
    │       permissions.py
    │       …
    │
    ├─── tests
        │
        ├───apps
            │
            ├───...

```

---

## Explications de l’architecture

### 1. Organisation générale 

Le projet est conçu sous forme de **micro-services** et de **micro-apps**, afin d’assurer :
- une meilleure **scalabilité** (chaque service peut évoluer indépendamment),
- une **modularité accrue** (chaque couche a une responsabilité claire),
- une **maintenabilité** renforcée.

### 2. Dossier `demperm/src/serveur/social`
Ce dossier est le dossier racine du projet serveur social, il contient le .gitignore, le Dockerfile, ce README et des fichiers de configuration:
- `.python-version` → Configure la version de Python utilisé.
- `uv.lock` → Gère les dépendances Python.
- `pyproject.toml` → Permet de générer, installer et construire le projet.

### 3. Dossier `api`
Ce dossier contient les dossiers concernant les différent aspects de l’API, un manage.py permettant de gérer le serveur et  un __init__.py pour être sur que Python  reconnaisse tout le travail à l’intérieur de ce dossier comme un même package.


### 4. Dossier `api/apps`
Ce dossier contient les dossiers dédié à toutes les modules du serveurs (posts,followers,forums,subscriptions, tags, subforums et users) afin de rendre l'archi plus propre et compréhensible.
Chaque sous-dossiers ont ces fichiers en commun:

- `urls.py` → Permet de définir pour Django les URLs qui seront utilisé pour chaque modules.
- `views.py` → Permet de définir le comportement du serveur lorsqu'il reçoit une requête et comment y répondre.
- `__init__.py` → Permet d'initialiser le package correspondant au module.


### 5. Dossier `django`
Ce dossier contient `settings.py` qui définit les paramètres Django du projet.

### 6. Dossier `conf`
Ce dossier  contient les différentes configurations et de paramétrages nécessaires pour le projet:
- `asgi.py` → Fichier de configuration d'ASGI.
- `urls.py` → Configure les URLs utilisés par le serveur.
- `wsgi.py` → Point d'entrée du déploiement.
- `__init__.py` → Regroupe a configuration dans un package.

### 6. Dossier `domains`
Ce dossier contient tout les modèles nécessaire aux modules.


### 7. Dossier `db`
Contient la configuration de la base de données, les entités, les accès et tout ce qui concerne la persistence des données.

### 8. Dossier `dto`
Dossier contenant les objets de transfert de données entre le serveur et l’API.

### 9. Dossier `services\apps_services`
Définit les services liés aux différents modules.

### 10. Dossier `services\mappers`
Définit les mappers entre les dto et les modèles.

### 11. Dossier `common`
Dossier contenant les éléments en commun entre les différentes parties de l’API pour éviter les duplications:

- `utils.py` → Fichiers contenant des fonctions réutilisées à plusieurs endroits du projet.
- `permissions.py` → Permet de définirs les permissions des différents rôles.

### 12. Dossier `tests`
Dossiers servant à créer et exécuter les tests.

---

## 🚀 Technologies utilisées

| Élément | Technologie / Outil | Description |
|----------|-----------|-------------|
| **Base de données** | MongoDB| Permet de facilement créer une base de données reliant les utilisateurs|
| **Framework API** | Django | Permet de créer des endpoints REST facilement |
| **Architecture** | Micro-services | Découpage logique, indépendant et maintenable |
| **CI/CD** | GitHub Actions | Intégration continue, tests automatisés, déploiement simplifié |
---

## En résumé

Cette architecture met en avant :
- 🔹 Une **structure modulaire et propre** (Clean Architecture)
- 🔹 Une **modélisation simples** des relations grâce à MongoDB
- 🔹 Une **intégration continue fiable** avec GitHub Actions


## Create development environment
```bash
uv venv .venv
source .venv/bin/activate
uv sync --dev
```

### Launch social server
```bash
python ./social_api/manage.py runserver 8000
```

You can now access to the API specification on the [Swagger page](http://127.0.0.1:8000/api/v1/swagger/).
