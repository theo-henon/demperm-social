# 🎯 Services Métier Implémentés

## Vue d'ensemble

Tous les services métier critiques ont été implémentés dans `api/services/apps_services/`. Ces services contiennent la logique métier complète et sont prêts à être utilisés par les endpoints API.

## Services Implémentés ✅

### 1. **AuthService** (`auth_service.py`)
Service d'authentification Google OAuth2 + JWT.

**Fonctionnalités :**
- `get_google_auth_url()` - Génère l'URL d'authentification Google
- `exchange_code_for_token()` - Échange le code d'autorisation contre un token
- `get_google_user_info()` - Récupère les infos utilisateur depuis Google
- `authenticate_with_google()` - Authentification complète
- `generate_tokens()` - Génère les tokens JWT (access + refresh)

### 2. **EncryptionService** (`encryption_service.py`)
Service de chiffrement E2E pour la messagerie.

**Fonctionnalités :**
- `generate_rsa_keypair()` - Génère une paire de clés RSA-2048
- `encrypt_message()` - Chiffre un message avec AES-256 + RSA
- `decrypt_message()` - Déchiffre un message

**Algorithmes :**
- AES-256-CBC pour le contenu
- RSA-2048 pour les clés de chiffrement
- Double chiffrement (sender + receiver)

### 3. **UserService** (`user_service.py`) ⭐ NOUVEAU
Service de gestion des utilisateurs.

**Fonctionnalités :**
- `get_user_by_id()` - Récupère un utilisateur par ID
- `get_current_user_profile()` - Profil complet de l'utilisateur connecté
- `update_user_profile()` - Met à jour le profil (username, bio, privacy, etc.)
- `update_user_settings()` - Met à jour les paramètres (notifications, langue)
- `search_users()` - Recherche d'utilisateurs par username
- `block_user()` - Bloquer un utilisateur
- `unblock_user()` - Débloquer un utilisateur
- `get_blocked_users()` - Liste des utilisateurs bloqués
- `get_bulk_users()` - Récupère plusieurs utilisateurs
- `can_view_profile()` - Vérifie les permissions de visualisation

**Validations :**
- Username unique
- Bio sanitisée
- Exclusion des utilisateurs bloqués dans les recherches
- Respect de la privacy (public/private)

### 4. **PostService** (`post_service.py`) ⭐ NOUVEAU
Service de gestion des posts.

**Fonctionnalités :**
- `create_post()` - Créer un post avec signature HMAC
- `get_post_by_id()` - Récupérer un post avec vérification des permissions
- `delete_post()` - Supprimer un post (owner ou admin)
- `like_post()` - Liker un post
- `unlike_post()` - Retirer son like
- `get_post_likes()` - Liste des utilisateurs ayant liké
- `get_feed()` - Fil d'actualité personnalisé (posts des followings)
- `get_discover()` - Découverte de posts populaires

**Validations :**
- Titre et contenu validés et sanitisés
- Signature de contenu (HMAC-SHA256)
- Vérification des permissions (privacy, blocks)
- Compteurs atomiques (like_count, comment_count)

### 5. **CommentService** (`comment_service.py`) ⭐ NOUVEAU
Service de gestion des commentaires.

**Fonctionnalités :**
- `create_comment()` - Créer un commentaire (avec support de threading)
- `get_comment_by_id()` - Récupérer un commentaire
- `delete_comment()` - Supprimer un commentaire (owner ou admin)
- `get_post_comments()` - Liste des commentaires d'un post
- `get_comment_replies()` - Réponses à un commentaire

**Validations :**
- Contenu validé et sanitisé
- Support des commentaires imbriqués (parent_comment_id)
- Tri par date ou popularité

### 6. **DomainService** (`domain_service.py`) ⭐ NOUVEAU
Service de gestion des domaines et sous-forums.

**Fonctionnalités :**
- `get_all_domains()` - Liste des 9 domaines politiques
- `get_domain_by_id()` - Récupérer un domaine
- `get_domain_by_name()` - Récupérer un domaine par nom
- `get_domain_subforums()` - Sous-forums d'un domaine
- `create_subforum_in_domain()` - Créer un sous-forum dans un domaine
- `get_subforum_by_id()` - Récupérer un sous-forum

**Validations :**
- Nom et description validés
- Incrémentation du compteur de sous-forums

### 7. **ForumService** (`forum_service.py`) ⭐ NOUVEAU
Service de gestion des forums.

**Fonctionnalités :**
- `create_forum()` - Créer un forum (créateur auto-ajouté comme modérateur)
- `get_forum_by_id()` - Récupérer un forum
- `get_all_forums()` - Liste de tous les forums
- `search_forums()` - Recherche de forums par nom
- `join_forum()` - Rejoindre un forum
- `leave_forum()` - Quitter un forum (sauf créateur)
- `get_user_forums()` - Forums dont l'utilisateur est membre

**Validations :**
- Nom et description validés
- Créateur ne peut pas quitter son forum
- Compteurs de membres mis à jour

### 8. **FollowerService** (`follower_service.py`) ⭐ NOUVEAU
Service de gestion des followers.

**Fonctionnalités :**
- `follow_user()` - Suivre un utilisateur (auto-accepté si public, pending si private)
- `unfollow_user()` - Ne plus suivre un utilisateur
- `accept_follow_request()` - Accepter une demande de suivi
- `reject_follow_request()` - Rejeter une demande de suivi
- `get_followers()` - Liste des followers
- `get_following()` - Liste des utilisateurs suivis
- `get_pending_requests()` - Demandes de suivi en attente

**Logique :**
- Profils publics : follow auto-accepté
- Profils privés : follow en attente d'acceptation
- Statuts : pending, accepted, rejected

### 9. **MessageService** (`message_service.py`) ⭐ NOUVEAU
Service de messagerie E2E chiffrée.

**Fonctionnalités :**
- `send_message()` - Envoyer un message chiffré E2E
- `decrypt_message()` - Déchiffrer un message
- `get_conversation()` - Conversation avec un utilisateur
- `get_conversations()` - Liste des conversations
- `delete_conversation()` - Supprimer une conversation (TODO)

**Sécurité :**
- Chiffrement E2E avec AES-256 + RSA-2048
- Double chiffrement (sender + receiver peuvent déchiffrer)
- Vérification des blocks
- Marquage automatique comme lu

### 10. **ReportService** (`report_service.py`) ⭐ NOUVEAU
Service de signalement et modération.

**Fonctionnalités :**
- `create_report()` - Signaler un post/comment/user
- `get_report_by_id()` - Récupérer un signalement
- `get_all_reports()` - Liste des signalements (admin)
- `update_report_status()` - Mettre à jour le statut (admin)
- `ban_user()` - Bannir un utilisateur (admin)
- `unban_user()` - Débannir un utilisateur (admin)

**Validations :**
- Raison entre 10 et 500 caractères
- Vérification de l'existence de la cible
- Permissions admin pour modération
- Statuts : pending, under_review, resolved, rejected

## Caractéristiques Communes

Tous les services implémentent :

✅ **Transactions atomiques** - Utilisation de `@transaction.atomic`
✅ **Validation des données** - Utilisation de `Validator`
✅ **Audit logging** - Toutes les actions critiques sont loggées
✅ **Gestion des erreurs** - Exceptions personnalisées
✅ **Permissions** - Vérification des droits d'accès
✅ **Compteurs atomiques** - Utilisation de `F()` pour éviter les race conditions

## Prochaines Étapes

Pour compléter l'API, il faut maintenant :

1. **Créer les endpoints API** - Implémenter les views et serializers pour chaque service
2. **Créer les DTOs** - Objets de transfert de données (optionnel avec DRF)
3. **Écrire les tests** - Tests unitaires et d'intégration pour chaque service
4. **Documenter avec Swagger** - Ajouter les annotations `@swagger_auto_schema`

Consultez `TEMPLATES.md` pour des templates de views/serializers/tests.

