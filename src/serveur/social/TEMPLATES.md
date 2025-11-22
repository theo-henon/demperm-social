# 📝 Templates pour continuer le développement

Ce fichier contient des templates pour créer rapidement les composants manquants.

## Template : Service

```python
"""
Service pour [DOMAIN].
"""
from typing import Optional, List
from db.repositories.[domain]_repository import [Domain]Repository
from db.repositories.message_repository import AuditLogRepository
from common.exceptions import NotFoundError, ValidationError
from common.validators import Validator


class [Domain]Service:
    """Service pour la gestion des [domain]."""
    
    @staticmethod
    def create_[entity](user_id: str, **kwargs) -> [Entity]:
        """
        Créer un nouveau [entity].
        
        Args:
            user_id: ID de l'utilisateur
            **kwargs: Données de l'entité
            
        Returns:
            L'entité créée
        """
        # Validation
        # ... utiliser Validator
        
        # Création
        entity = [Domain]Repository.create(user_id=user_id, **kwargs)
        
        # Audit log
        AuditLogRepository.create(
            user_id=user_id,
            action_type='[entity]_created',
            resource_type='[entity]',
            resource_id=str(entity.[entity]_id)
        )
        
        return entity
    
    @staticmethod
    def get_[entity](entity_id: str) -> [Entity]:
        """Récupérer un [entity] par ID."""
        entity = [Domain]Repository.get_by_id(entity_id)
        if not entity:
            raise NotFoundError(f"[Entity] {entity_id} not found")
        return entity
    
    @staticmethod
    def update_[entity](entity_id: str, user_id: str, **kwargs) -> [Entity]:
        """Mettre à jour un [entity]."""
        entity = [Domain]Service.get_[entity](entity_id)
        
        # Vérifier les permissions
        if str(entity.user_id) != user_id:
            raise PermissionDeniedError("Not authorized")
        
        # Mise à jour
        entity = [Domain]Repository.update(entity_id, **kwargs)
        
        # Audit log
        AuditLogRepository.create(
            user_id=user_id,
            action_type='[entity]_updated',
            resource_type='[entity]',
            resource_id=entity_id
        )
        
        return entity
```

## Template : Serializer

```python
"""
Serializers pour [domain].
"""
from rest_framework import serializers


class [Entity]Serializer(serializers.Serializer):
    """Serializer pour [Entity]."""
    
    [entity]_id = serializers.UUIDField(read_only=True)
    user_id = serializers.UUIDField(read_only=True)
    # ... autres champs
    created_at = serializers.DateTimeField(read_only=True)
    updated_at = serializers.DateTimeField(read_only=True)


class Create[Entity]Serializer(serializers.Serializer):
    """Serializer pour créer un [entity]."""
    
    # ... champs requis
    
    def validate_[field](self, value):
        """Valider [field]."""
        # Utiliser Validator
        return value


class Update[Entity]Serializer(serializers.Serializer):
    """Serializer pour mettre à jour un [entity]."""
    
    # ... champs optionnels
```

## Template : View

```python
"""
Views pour [domain].
"""
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

from services.apps_services.[domain]_service import [Domain]Service
from common.permissions import IsAuthenticated
from common.rate_limiters import rate_limit_general
from common.exceptions import NotFoundError
from .serializers import [Entity]Serializer, Create[Entity]Serializer


class [Entity]ListView(APIView):
    """Liste des [entities]."""
    
    permission_classes = [IsAuthenticated]
    
    @swagger_auto_schema(
        operation_description="Récupérer la liste des [entities]",
        responses={200: [Entity]Serializer(many=True)}
    )
    @rate_limit_general
    def get(self, request):
        """Récupérer la liste."""
        entities = [Domain]Service.get_all()
        serializer = [Entity]Serializer(entities, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class [Entity]CreateView(APIView):
    """Créer un [entity]."""
    
    permission_classes = [IsAuthenticated]
    
    @swagger_auto_schema(
        operation_description="Créer un nouveau [entity]",
        request_body=Create[Entity]Serializer,
        responses={201: [Entity]Serializer}
    )
    @rate_limit_general
    def post(self, request):
        """Créer un [entity]."""
        serializer = Create[Entity]Serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        entity = [Domain]Service.create_[entity](
            user_id=str(request.user.user_id),
            **serializer.validated_data
        )
        
        response_serializer = [Entity]Serializer(entity)
        return Response(response_serializer.data, status=status.HTTP_201_CREATED)


class [Entity]DetailView(APIView):
    """Détails d'un [entity]."""
    
    permission_classes = [IsAuthenticated]
    
    @swagger_auto_schema(
        operation_description="Récupérer les détails d'un [entity]",
        responses={200: [Entity]Serializer}
    )
    def get(self, request, entity_id):
        """Récupérer les détails."""
        try:
            entity = [Domain]Service.get_[entity](entity_id)
            serializer = [Entity]Serializer(entity)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except NotFoundError as e:
            return Response(
                {'error': {'code': 'NOT_FOUND', 'message': str(e)}},
                status=status.HTTP_404_NOT_FOUND
            )
```

## Template : URLs

```python
"""
URL configuration pour [domain].
"""
from django.urls import path
from .views import (
    [Entity]ListView,
    [Entity]CreateView,
    [Entity]DetailView,
)

app_name = '[domain]'

urlpatterns = [
    path('', [Entity]ListView.as_view(), name='[entity]-list'),
    path('create/', [Entity]CreateView.as_view(), name='[entity]-create'),
    path('<uuid:entity_id>/', [Entity]DetailView.as_view(), name='[entity]-detail'),
]
```

## Template : Test

```python
"""
Tests pour [domain] service.
"""
import pytest
from services.apps_services.[domain]_service import [Domain]Service
from common.exceptions import NotFoundError


@pytest.mark.unit
class Test[Domain]Service:
    """Tests pour [Domain]Service."""
    
    def test_create_[entity](self, test_user):
        """Test création d'un [entity]."""
        entity = [Domain]Service.create_[entity](
            user_id=str(test_user.user_id),
            # ... données
        )
        
        assert entity is not None
        assert str(entity.user_id) == str(test_user.user_id)
    
    def test_get_[entity]_not_found(self):
        """Test récupération d'un [entity] inexistant."""
        with pytest.raises(NotFoundError):
            [Domain]Service.get_[entity]('00000000-0000-0000-0000-000000000000')
```

## Exemple d'utilisation

Pour créer le service User :

1. Remplacer `[Domain]` par `User`
2. Remplacer `[domain]` par `user`
3. Remplacer `[Entity]` par `User`
4. Remplacer `[entity]` par `user`
5. Adapter les champs et la logique métier

