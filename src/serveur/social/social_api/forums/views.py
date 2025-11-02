from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi


class ForumListView(APIView):
    @swagger_auto_schema(
        operation_description="Liste des forums",
        tags=["Forums"],
        responses={
            200: openapi.Response(description="Liste des forums"),
            401: openapi.Response(description="Non authentifié")
        }
    )
    def get(self, request):
        # TODO: Implémenter la récupération des forums
        
        return Response([
            {"id": 1, "name": "Forum général", "description": "Discussions générales"},
            {"id": 2, "name": "Actualités", "description": "L'actualité du jour"}
        ], status=status.HTTP_200_OK)


class ForumCreateView(APIView):
    @swagger_auto_schema(
        operation_description="Créer un forum",
        tags=["Forums"],
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'name': openapi.Schema(type=openapi.TYPE_STRING, description="Nom du forum"),
                'description': openapi.Schema(type=openapi.TYPE_STRING, description="Description du forum")
            },
            required=['name']
        ),
        responses={
            201: openapi.Response(description="Forum créé"),
            400: openapi.Response(description="Données invalides"),
            401: openapi.Response(description="Non authentifié")
        }
    )
    def post(self, request):
        # TODO: Implémenter la création de forum
        name = request.data.get('name', '')
        description = request.data.get('description', '')
        
        return Response({
            "id": 10,
            "name": name,
            "description": description
        }, status=status.HTTP_201_CREATED)


class ForumDetailView(APIView):
    @swagger_auto_schema(
        operation_description="Détails d'un forum",
        tags=["Forums"],
        responses={
            200: openapi.Response(description="Forum trouvé"),
            404: openapi.Response(description="Forum non trouvé"),
            401: openapi.Response(description="Non authentifié")
        }
    )
    def get(self, request, id):
        # TODO: Implémenter la récupération d'un forum
        
        return Response({
            "id": id,
            "name": "Forum général",
            "description": "Discussions générales",
            "subscribers_count": 150
        }, status=status.HTTP_200_OK)


class ForumMeView(APIView):
    @swagger_auto_schema(
        operation_description="Forums suivis par l'utilisateur",
        tags=["Forums"],
        responses={
            200: openapi.Response(description="Liste des forums suivis"),
            401: openapi.Response(description="Non authentifié")
        }
    )
    def get(self, request):
        # TODO: Implémenter la récupération des forums suivis
        
        return Response([
            {"id": 1, "name": "Forum général"},
            {"id": 3, "name": "Technologie"}
        ], status=status.HTTP_200_OK)


class ForumSearchView(APIView):
    @swagger_auto_schema(
        operation_description="Recherche de forums",
        tags=["Forums"],
        manual_parameters=[
            openapi.Parameter(
                'query',
                openapi.IN_QUERY,
                description="Terme de recherche",
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
        query = request.GET.get('query', '')
        # TODO: Implémenter la recherche
        
        return Response([
            {"id": 1, "name": f"Forum contenant '{query}'"}
        ], status=status.HTTP_200_OK)


class ForumSubforumsView(APIView):
    @swagger_auto_schema(
        operation_description="Liste des sous-forums",
        tags=["Forums"],
        responses={
            200: openapi.Response(description="Liste des sous-forums"),
            404: openapi.Response(description="Forum non trouvé"),
            401: openapi.Response(description="Non authentifié")
        }
    )
    def get(self, request, id):
        # TODO: Implémenter la récupération des sous-forums
        
        return Response([
            {"id": 1, "name": "Sous-forum 1", "forum_id": id},
            {"id": 2, "name": "Sous-forum 2", "forum_id": id}
        ], status=status.HTTP_200_OK)


class ForumSubforumCreateView(APIView):
    @swagger_auto_schema(
        operation_description="Créer un sous-forum",
        tags=["Forums"],
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
            404: openapi.Response(description="Forum non trouvé")
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
            "forum_id": id
        }, status=status.HTTP_201_CREATED)
