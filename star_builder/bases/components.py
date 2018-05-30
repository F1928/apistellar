import typing
import inspect

from toolkit.singleton import Singleton
from toolkit.frozen import FrozenSettings
from toolkit.settings import SettingsLoader
from apistar import Route, exceptions, Component as _Component

from .service import Service


class Component(_Component, metaclass=Singleton):

    def resolve(self, *args, **kwargs):
        raise NotImplementedError()

    def can_handle_parameter(self, parameter: inspect.Parameter):
        """重写这个方法是为了增加typing.Union类型的判定"""
        return_annotation = inspect.signature(self.resolve).return_annotation
        if return_annotation is inspect.Signature.empty:
            msg = (
                'Component "%s" must include a return annotation on the '
                '`resolve()` method, or override `can_handle_parameter`'
            )
            raise exceptions.ConfigurationError(msg % self.__class__.__name__)
        return type(return_annotation) == typing._Union and \
               parameter.annotation in return_annotation.__args__ or \
               parameter.annotation is return_annotation


class ServiceComponent(Component):
    """
    注入Service
    """
    def resolve(self, route: Route) -> Service:
        return route.service


class SettingsComponent(Component):
    """
    注入Settings
    """
    settings_path = None

    def __init__(self):
        self.settings = SettingsLoader().load(self.settings_path or "settings")

    def resolve(self) -> FrozenSettings:
        return self.settings

    @classmethod
    def register_path(cls, settings_path):
        cls.settings_path = settings_path
