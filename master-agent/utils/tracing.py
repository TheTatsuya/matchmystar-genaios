from abc import ABC, abstractmethod


class BaseTracer(ABC):
    @abstractmethod
    def add_trace(self, **kwargs):
        pass

    @abstractmethod
    def add_subtrace(self, field_name: str, **kwargs):
        pass


class AgentTracer(BaseTracer):
    def __init__(self):
        self._traces: list = []

    def add_trace(self, **kwargs):
        self._traces.append(kwargs)

    def add_subtrace(self, field_name: str, **kwargs):
        """
        Add subtrace to the last trace
        """
        subtraces = self._traces[-1].get(field_name)

        if not subtraces:
            self._traces[-1][field_name] = []

        self._traces[-1][field_name].append(kwargs)

    @property
    def traces(self):
        return self._traces
