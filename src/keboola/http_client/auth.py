import inspect
from abc import ABC, abstractmethod
from typing import Callable, Union, Dict

from requests.auth import AuthBase, HTTPBasicAuth


class AuthBuilderError(Exception):
    pass


class AuthMethodBase(ABC):
    """
    Base class to implement the authentication method. To mark secret constructor parameters prefix them with secret__
    e.g. __init__(self, username, secret__password)
    """

    @abstractmethod
    def login(self):
        """
        Perform steps to login and returns requests.aut.AuthBase callable that modifies the request.

        """
        pass


class AuthMethodBuilder:
    SECRET_PREFIX = "secret__"

    @classmethod
    def build(cls, method_name: str, **parameters):
        """

        Args:
            method_name:
            **parameters: dictionary of named parameters.
            Note that parameters prefixed # will be converted to prefix secret__. e.g. #password -> secret__password
            argument in the AuthMethod

        Returns:

        """
        supported_actions = cls.get_methods()

        if method_name not in list(supported_actions.keys()):
            raise AuthBuilderError(f'{method_name} is not supported auth method, '
                                   f'supported values are: [{list(supported_actions.keys())}]')
        parameters = cls._convert_secret_parameters(supported_actions[method_name], **parameters)
        cls._validate_method_arguments(supported_actions[method_name], **parameters)

        return supported_actions[method_name](**parameters)

    @staticmethod
    def _validate_method_arguments(method: object, **args):

        arguments = [p for p in inspect.signature(method.__init__).parameters if p != 'self']
        missing_arguments = []
        for p in arguments:
            if p not in args:
                missing_arguments.append(p.replace(AuthMethodBuilder.SECRET_PREFIX, '#'))
        if missing_arguments:
            raise AuthBuilderError(f'Some arguments of method {method.__name__} are missing: {missing_arguments}')

    @staticmethod
    def _convert_secret_parameters(method: object, **parameters):
        new_parameters = {}
        for p in parameters:
            new_parameters[p.replace('#', AuthMethodBuilder.SECRET_PREFIX)] = parameters[p]
        return new_parameters

    @staticmethod
    def get_methods() -> Dict[str, Callable]:
        supported_actions = {}
        for c in AuthMethodBase.__subclasses__():
            supported_actions[c.__name__] = c
        return supported_actions

    @classmethod
    def get_supported_methods(cls):
        return list(cls.get_methods().keys())


# ########### SUPPORTED AUTHENTICATION METHODS

class BasicHttp(AuthMethodBase):

    def __init__(self, username, secret__password):
        self.username = username
        self.password = secret__password

    def login(self) -> Union[AuthBase, Callable]:
        return HTTPBasicAuth(username=self.username, password=self.password)

    def __eq__(self, other):
        return all([
            self.username == getattr(other, 'username', None),
            self.password == getattr(other, 'password', None)
        ])
