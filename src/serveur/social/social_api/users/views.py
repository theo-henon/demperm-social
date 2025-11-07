from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi


class UserMeView(APIView):
    @swagger_auto_schema(
        operation_description="Récupère les informations du profil connecté",
        tags=["Users"],
        responses={
            200: openapi.Response(description="Profil trouvé"),
            404: openapi.Response(description="Utilisateur non trouvé"),
            401: openapi.Response(description="Non authentifié")
        }
    )
    def get(self, request):
        # TODO

        return Response({
            "id": 1,
            "username": "theo.henon",
            "bio": "Développeur engagé",
            "followers": 42,
            "following": 17,
            "groups": [
                {"id": 1, "name": "Numérique & IA"},
                {"id": 2, "name": "Social"},
                {"id": 3, "name": "Environnement"},
            ],
            "topics": [
                {"id": 1, "title": "L'impact de l'IA sur la société et l'environnement"}
            ],
            "subscriptions": {
                "users": 10,
                "topics": 5,
                "groups": 3
            }
        })

    @swagger_auto_schema(
        operation_description="Met à jour le profil connecté",
        tags=["Users"],
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'username': openapi.Schema(type=openapi.TYPE_STRING),
                'bio': openapi.Schema(type=openapi.TYPE_STRING),
            }
        ),
        responses={
            200: openapi.Response(description="Profil mis à jour"),
            400: openapi.Response(description="Requête invalide"),
            401: openapi.Response(description="Non authentifié")
        }
    )
    def patch(self, request):
        data = request.data or {}
        username = data.get('username', 'theo.henon')
        bio = data.get('bio', 'Développeur engagé')

        updated = {
            "id": 1,
            "username": username,
            "bio": bio,
            "followers": 42,
            "following": 17,
            "groups": [
                {"id": 1, "name": "Numérique & IA"},
                {"id": 2, "name": "Social"},
                {"id": 3, "name": "Environnement"},
            ],
            "topics": [
                {"id": 1, "title": "L'impact de l'IA sur la société et l'environnement"}
            ],
            "subscriptions": {
                "users": 10,
                "topics": 5,
                "groups": 3
            }
        }

        return Response(updated, status=status.HTTP_200_OK)


class UserDetailView(APIView):
    @swagger_auto_schema(
        operation_description="Affiche le profil public d’un utilisateur",
        tags=["Users"],
        responses={
            200: openapi.Response(description="Profil trouvé"),
            404: openapi.Response(description="Utilisateur non trouvé"),
            401: openapi.Response(description="Non authentifié")
        }
    )
    def get(self, request, id):
        # TODO

        return Response({
            "id": id,
            "username": "utilisateur_" + str(id),
            "bio": "Utilisateur actif de la plateforme",
            "followers": 120,
            "following": 75,
            "groups": [
                {"id": 3, "name": "Écologie"},
                {"id": 4, "name": "Technologie"}
            ],
            "topics": [
                {"id": 7, "title": "Transition énergétique"},
                {"id": 8, "title": "Nouvelles technologies"}
            ],
            "subscriptions": {
                "users": 20,
                "topics": 8,
                "groups": 4
            }
        })


class UserSearchView(APIView):
    @swagger_auto_schema(
        operation_description="Recherche utilisateur par username",
        tags=["Users"],
        manual_parameters=[
            openapi.Parameter(
                'username',
                openapi.IN_QUERY,
                description="Nom d'utilisateur à rechercher",
                type=openapi.TYPE_STRING,
                required=True
            )
        ],
        responses={
            200: openapi.Response(description="Résultats de recherche"),
            401: openapi.Response(description="Non authentifié")
        }
    )
    def get(self, request):
        username = request.GET.get('username', '')
        # TODO: Implémenter la recherche réelle
        
        return Response([
            {
                "id": 1,
                "username": username,
                "bio": "Utilisateur trouvé"
            }
        ])


class UserPostsView(APIView):
    @swagger_auto_schema(
        operation_description="Posts d'un utilisateur",
        tags=["Posts"],
        responses={
            200: openapi.Response(description="Liste des posts"),
            404: openapi.Response(description="Utilisateur non trouvé"),
            401: openapi.Response(description="Non authentifié")
        }
    )
    def get(self, request, id):
        # TODO: Implémenter la récupération des posts
        
        return Response([
            {
                "id": 1,
                "title": "Mon premier post",
                "content": "Contenu du post",
                "author_id": id,
                "created_at": "2025-01-15T10:30:00Z"
            },
            {
                "id": 2,
                "title": "Deuxième post",
                "content": "Autre contenu",
                "author_id": id,
                "created_at": "2025-01-16T14:20:00Z"
            }
        ])


class UserDiscoverView(APIView):
    @swagger_auto_schema(
        operation_description="Découvrir des utilisateurs (découverte)",
        tags=["Users"],
        responses={
            200: openapi.Response(description="Utilisateurs découverts"),
            401: openapi.Response(description="Non authentifié")
        }
    )
    def get(self, request):
        # TODO: Implémenter la logique réelle de découverte
        return Response([
            {
                "id": 10,
                "username": "discover_alice",
                "bio": "Bio d'Alice",
                "joined_at": "2025-10-01T09:00:00Z"
            },
            {
                "id": 11,
                "username": "discover_bob",
                "bio": "Bio de Bob",
                "joined_at": "2025-10-02T10:00:00Z"
            }
        ], status=status.HTTP_200_OK)
