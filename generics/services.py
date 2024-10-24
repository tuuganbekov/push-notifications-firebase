from typing import Any, Dict

from django.db.models import Model
from rest_framework.serializers import BaseSerializer


class BaseService:
    model: Model
    context: Dict[str, Any]

    def __init__(self):
        self.context = dict()

    def execute(self, serializer: BaseSerializer):
        raise NotImplementedError(
            "%s must implement `execute` method." % self.__class__.__name__
        )


class BaseDirectService:
    """
    execute method without serializer parameter
    """

    model: Model
    context: Dict[str, Any]

    def __init__(self):
        self.context = dict()

    def execute(self):
        raise NotImplementedError(
            "%s must implement `execute` method." % self.__class__.__name__
        )
