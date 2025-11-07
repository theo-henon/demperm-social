from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi


class DomainListView(APIView):
    @swagger_auto_schema(
        operation_description="Liste des domaines",
        tags=["Domains"],
        responses={
            200: openapi.Response(description="Liste des domaines"),
            401: openapi.Response(description="Non authentifié")
        }
    )
    def get(self, request):
        # TODO: Implémenter la récupération des domaines
        
        return Response([
            {"id": 1, "name": "Politique", "description": "Discussions politiques"},
            {"id": 2, "name": "Économie", "description": "Débats économiques"},
            {"id": 3, "name": "Écologie", "description": "Environnement et transition"}
        ], status=status.HTTP_200_OK)


class DomainDetailView(APIView):
    @swagger_auto_schema(
        operation_description="Détails d'un domaine",
        tags=["Domains"],
        responses={
            200: openapi.Response(description="Domaine trouvé"),
            404: openapi.Response(description="Domaine non trouvé"),
            401: openapi.Response(description="Non authentifié")
        }
    )
    def get(self, request, id):
        # TODO: Implémenter la récupération d'un domaine
        
        return Response({
            "id": id,
            "name": "Politique",
            "description": "Discussions politiques",
            "subforums_count": 5
        }, status=status.HTTP_200_OK)


class DomainSubforumsView(APIView):
    @swagger_auto_schema(
        operation_description="Liste des sous-forums d'un domaine",
        tags=["Domains"],
        responses={
            200: openapi.Response(description="Liste des sous-forums"),
            404: openapi.Response(description="Domaine non trouvé"),
            401: openapi.Response(description="Non authentifié")
        }
    )
    def get(self, request, id):
        # TODO: Implémenter la récupération des sous-forums
        
        return Response([
            {"id": 1, "name": "Élections", "domain_id": id},
            {"id": 2, "name": "Institutions", "domain_id": id}
        ], status=status.HTTP_200_OK)


class DomainSubforumCreateView(APIView):
    @swagger_auto_schema(
        operation_description="Créer un sous-forum dans un domaine",
        tags=["Domains"],
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'name': openapi.Schema(type=openapi.TYPE_STRING, description="Nom du sous-forum"),
                'description': openapi.Schema(type=openapi.TYPE_STRING, description="Description du sous-forum")
            },
            required=['name']
        ),
        responses={
            201: openapi.Response(description="Sous-forum créé"),
            400: openapi.Response(description="Données invalides"),
            401: openapi.Response(description="Non authentifié"),
            404: openapi.Response(description="Domaine non trouvé")
        }
    )
    def post(self, request, id):
        # TODO: Implémenter la création de sous-forum
        name = request.data.get('name', '')
        description = request.data.get('description', '')
        
        return Response({
            "id": 10,
            "name": name,
            "description": description,
            "domain_id": id
        }, status=status.HTTP_201_CREATED)
