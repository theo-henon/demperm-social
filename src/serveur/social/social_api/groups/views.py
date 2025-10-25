from rest_framework.views import APIView
from rest_framework.response import Response
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi


class GroupCreateView(APIView):
    @swagger_auto_schema(
        operation_description="Crée un nouveau groupe de débat",
        tags=["Groups"],
        responses={
            201: openapi.Response(description="Groupe créé"),
            400: openapi.Response(description="Données invalides"),
            401: openapi.Response(description="Non authentifié")
        }
    )
    def post(self, request):
        # TODO

        return Response({
            "id": 10,
            "name": "Nouveau Groupe",
            "description": "Un groupe pour discuter de sujets variés",
            "membersCount": 1,
            "topics": []
        })


class GroupListView(APIView):
    @swagger_auto_schema(
        operation_description="Recherche ou liste les groupes existants",
        tags=["Groups"],
        responses={
            200: openapi.Response(description="Liste des groupes"),
            401: openapi.Response(description="Non authentifié")
        }
    )
    def get(self, request):
        # TODO

        return Response([
            {"id": 1, "name": "Numérique & IA"},
            {"id": 2, "name": "Écologie"},
            {"id": 3, "name": "Politique"}
        ])


class GroupDetailView(APIView):
    @swagger_auto_schema(
        operation_description="Récupère les informations d’un groupe et ses topics",
        tags=["Groups"],
        responses={
            200: openapi.Response(description="Détails du groupe"),
            404: openapi.Response(description="Groupe non trouvé"),
            401: openapi.Response(description="Non authentifié")
        }
    )
    def get(self, request, id):
        # TODO

        return Response({
            "id": id,
            "name": "Numérique & IA",
            "description": "Discussions autour de l'intelligence artificielle",
            "membersCount": 42,
            "topics": [
                {"id": 1, "title": "L'impact de l'IA sur la société"},
                {"id": 2, "title": "Éthique et IA"}
            ]
        })


class GroupMembersView(APIView):
    @swagger_auto_schema(
        operation_description="Liste les membres du groupe",
        tags=["Groups"],
        responses={
            200: openapi.Response(description="Liste des membres"),
            404: openapi.Response(description="Groupe non trouvé"),
            401: openapi.Response(description="Non authentifié")
        }
    )
    def get(self, request, id):
        # TODO
        return Response([
            {"id": 1, "username": "theo_henon"},
            {"id": 2, "username": "alice_dev"},
            {"id": 3, "username": "bob_ai"}
        ])
