from enum import Enum
from typing import Mapping, Type, Union

import requests
from rest_framework import mixins, status
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.serializers import BaseSerializer

from generics.services import BaseDirectService, BaseService

session = requests.Session()
session.trust_env = False


class MethodActionType(str, Enum):
    GET = "read"
    POST = "create"
    PUT = "update"
    PATCH = "partial_update"
    DELETE = "delete"


class MultipleSerializersMixin:
    request: Request
    serializer_classes: Mapping[str, BaseSerializer]

    def get_serializer_class(self):
        try:
            action: MethodActionType = getattr(
                MethodActionType, self.request.method
            )  # noqa
            return self.serializer_classes[action.value]
        except KeyError as error:
            raise Exception(
                "Key %s not found in serializer_classes mapping."
                % action.value
            ) from error
        except AttributeError:
            methods = map(lambda a: a.name, MethodActionType)
            assert self.request.method not in methods, (
                "Expected one of the following methods: %s. Got: %s"
                % (", ".join(methods), self.request.method),
            )


class ServiceMixin:
    service: Type[BaseService | BaseDirectService]

    def get_service(
        self, *args, **kwargs
    ) -> Union[BaseService, BaseDirectService]:
        assert self.service is not None, (
            "'%s' should either include a `service` attribute, "
            "or override the `get_service()` method." % self.__class__.__name__
        )

        return self.service(*args, **kwargs)


class ServiceCreateModelMixin(ServiceMixin, mixins.CreateModelMixin):
    def create(self, request, *args, **kwargs):
        service = self.get_service()
        service.context.update({"request": request})
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data, status = service.execute(serializer)
        return Response(data, status=status)


class ServiceListModelMixin(ServiceMixin):
    def list(self, request: Request, *args, **kwargs):
        service = self.get_service()
        service.context.update({"request": request})
        queryset = self.get_queryset()  # type:ignore
        serializer = self.get_serializer(queryset, many=True)  # type:ignore
        data = service.execute(serializer)  # type:ignore
        return Response(data, status=status.HTTP_200_OK)


class ServiceModelMixin(ServiceMixin):
    def list(self, request: Request, *args, **kwargs):
        service = self.get_service()
        service.context.update({"request": request})
        queryset = self.get_queryset()  # type:ignore
        serializer = self.get_serializer(queryset)  # type:ignore
        data, status = service.execute(serializer)  # type:ignore
        return Response(data, status=status)


class ServiceRequestMixin(ServiceMixin):
    def list(self, request: Request, *args, **kwargs):
        service = self.get_service()
        service.context.update({"request": request})
        data, status = service.execute()  # type:ignore
        return Response(data, status=status)

    def create(self, request, *args, **kwargs):
        service = self.get_service()
        service.context.update({"request": request})
        data, status = service.execute()
        return Response(data, status=status)


class FetchDataMixin:
    def _fetch_data(self, url: str, query_params: dict) -> tuple:
        try:
            response = session.post(url, params=query_params)
            data = response.json()
            return data, status.HTTP_200_OK
        except Exception as e:
            return (
                {"message": response.text, "error_message": str(e)},
                response.status_code,
            )


class ServiceListMixin(ServiceMixin):
    def list(self, request: Request, *args, **kwargs):
        service = self.get_service()
        service.context.update({"request": request})
        queryset = self.get_queryset().last()  # type:ignore
        serializer = self.get_serializer(queryset)  # type:ignore
        data = service.execute(serializer)  # type:ignore
        return Response(data, status=status.HTTP_200_OK)
