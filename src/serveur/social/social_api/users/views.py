from rest_framework.views import APIView
from rest_framework.response import Response
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
        operation_description="Met à jour le profil de l’utilisateur connecté",
        tags=["Users"],
        responses={
            200: openapi.Response(description="Groupes trouvés"),
            404: openapi.Response(description="Utilisateur ou groupes non trouvés"),
            401: openapi.Response(description="Non authentifié")
        }
    )
    def patch(self, request):
        return Response({"message": "Profil mis à jour (mock)"})


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


class UserGroupsView(APIView):
    @swagger_auto_schema(
        operation_description="Liste les groupes rejoints par l’utilisateur",
        tags=["Users"],
        responses={
            200: openapi.Response(description="Groupes trouvés"),
            404: openapi.Response(description="Utilisateur ou groupes non trouvés"),
            401: openapi.Response(description="Non authentifié")
        }
    )
    def get(self, request, id):
        # TODO

        return Response([
            {"id": 3, "name": "Écologie"},
            {"id": 4, "name": "Technologie"},
            {"id": 5, "name": "Politique"}
        ])
