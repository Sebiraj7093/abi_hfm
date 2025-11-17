import inspect
from functools import wraps
from types import FunctionType

from hf_yaml_loader.yaml import YamlLoader
from opentelemetry import trace
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
from opentelemetry.propagate import set_global_textmap
from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.trace.propagation.tracecontext import TraceContextTextMapPropagator

from configuration import APPLICATION_NAME
from configuration import ROOT

tracing_config = YamlLoader(ROOT).load("tracing/tracing_config.yaml")


otlp_exporter = OTLPSpanExporter(
    endpoint=f"{tracing_config['JAEGER_HOST']}:{tracing_config['JAEGER_PORT']}", insecure=True
)

trace.set_tracer_provider(
    TracerProvider(resource=Resource(attributes={"service.name": APPLICATION_NAME}))
)

span_processor = BatchSpanProcessor(otlp_exporter)
trace.get_tracer_provider().add_span_processor(span_processor)
tracer = trace.get_tracer(__name__)

propagator = TraceContextTextMapPropagator()
set_global_textmap(propagator)


def tracing_wrapper(method):
    @wraps(method)
    def wrapped(*args, **kwargs):
        att_args = {f"arg.{i}": str(v) for i, v in enumerate(args[1:])}
        att_kwargs = {f"arg.{k}": str(v) for k, v in kwargs.items()}
        with tracer.start_as_current_span(
            method.__qualname__,
            attributes=dict(caller=str(args[0]), **att_args, **att_kwargs),
        ):
            return method(*args, **kwargs)

    return wrapped


def async_tracing_wrapper(method):
    @wraps(method)
    async def wrapped(*args, **kwargs):
        att_args = {f"arg.{i}": str(v) for i, v in enumerate(args[1:])}
        att_kwargs = {f"arg.{k}": str(v) for k, v in kwargs.items()}
        with tracer.start_as_current_span(
            method.__qualname__,
            attributes=dict(caller=str(args[0]), **att_args, **att_kwargs),
        ):
            return await method(*args, **kwargs)

    return wrapped


class TracerMixin(type):
    def __new__(cls, class_name, bases, class_dict):
        new_class_dict = {}
        for attribute_name, attribute in class_dict.items():
            if isinstance(attribute, FunctionType) and not (
                attribute_name.startswith("__") and attribute_name.endswith("__")
            ):
                if inspect.iscoroutinefunction(attribute):
                    attribute = async_tracing_wrapper(attribute)
                else:
                    attribute = tracing_wrapper(attribute)

            new_class_dict[attribute_name] = attribute
        return type.__new__(cls, class_name, bases, new_class_dict)
