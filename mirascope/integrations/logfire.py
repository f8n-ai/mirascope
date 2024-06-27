"""Mirascope x Logfire Integration."""

import inspect
from contextlib import contextmanager
from functools import wraps
from string import Formatter
from typing import (
    Any,
    AsyncIterable,
    Awaitable,
    Callable,
    Generator,
    Iterable,
    ParamSpec,
    TypeVar,
    overload,
)

import logfire
from pydantic import BaseModel

from ..core.base import BaseAsyncStream, BaseCallResponse, BaseStream
from .utils import middleware

_P = ParamSpec("_P")
_R = TypeVar("_R", bound=BaseCallResponse | BaseStream | BaseModel | BaseAsyncStream)


@overload
def with_logfire(fn: Callable[_P, _R]) -> Callable[_P, _R]: ...


@overload
def with_logfire(fn: Callable[_P, Awaitable[_R]]) -> Callable[_P, Awaitable[_R]]: ...


def with_logfire(
    fn: Callable[_P, _R] | Callable[_P, Awaitable[_R]],
) -> Callable[_P, _R] | Callable[_P, Awaitable[_R]]:
    """Wraps a Mirascope function with Logfire tracing."""

    @contextmanager
    def custom_context_manager() -> Generator[logfire.LogfireSpan, Any, None]:
        with logfire.with_settings(custom_scope_suffix="mirascope").span(
            fn.__name__
        ) as logfire_span:
            yield logfire_span

    def handle_call_response(
        result: BaseCallResponse, logfire_span: logfire.LogfireSpan | None
    ):
        if logfire_span is None:
            return
        output: dict[str, Any] = {}
        span_data = {
            "async": True,
            "call_params": result.call_params,
            "model": result.model,
            "provider": result.provider,
            "prompt_template": result.prompt_template,
            "template_variables": result.fn_args,
            "output": output,
            "messages": result.messages,
            "response_data": result.model_dump(),
        }

        if tools := result.tools:
            tool_calls = [
                {
                    "function": {
                        "arguments": tool.model_dump_json(exclude={"tool_call"}),
                        "name": tool.name(),
                    }
                }
                for tool in tools
            ]
            output["tool_calls"] = tool_calls
        if cost := result.cost:
            output["cost"] = cost
        if input_tokens := result.input_tokens:
            output["input_tokens"] = input_tokens
        if output_tokens := result.output_tokens:
            output["output_tokens"] = output_tokens
        if content := result.content:
            output["content"] = content
        logfire_span.set_attributes(span_data)

    def handle_stream(
        stream: BaseStream,
        logfire_span: logfire.LogfireSpan | None,
    ):
        stream_dict = {k: v for k, v in vars(stream).items() if not k.startswith("_")}
        if logfire_span is not None:
            logfire_span.set_attributes(stream_dict)

    def handle_base_model(result: BaseModel, logfire_span: logfire.LogfireSpan | None):
        print("baz")

    async def handle_call_response_async(
        result: BaseCallResponse, logfire_span: logfire.LogfireSpan | None
    ):
        if logfire_span is None:
            return
        output: dict[str, Any] = {}
        span_data = {
            "async": True,
            "call_params": result.call_params,
            "model": result.model,
            "provider": result.provider,
            "prompt_template": result.prompt_template,
            "template_variables": result.fn_args,
            "output": output,
            "messages": result.messages,
            "response_data": result.model_dump(),
        }

        if tools := result.tools:
            tool_calls = [
                {
                    "function": {
                        "arguments": tool.model_dump_json(exclude={"tool_call"}),
                        "name": tool.name(),
                    }
                }
                for tool in tools
            ]
            output["tool_calls"] = tool_calls
        if cost := result.cost:
            output["cost"] = cost
        if input_tokens := result.input_tokens:
            output["input_tokens"] = input_tokens
        if output_tokens := result.output_tokens:
            output["output_tokens"] = output_tokens
        if content := result.content:
            output["content"] = content
        logfire_span.set_attributes(span_data)

    async def handle_stream_async(
        stream: BaseStream,
        logfire_span: logfire.LogfireSpan | None,
    ):
        handle_stream(stream, logfire_span)

    return middleware(
        fn,
        custom_context_manager=custom_context_manager,
        handle_call_response=handle_call_response,
        handle_call_response_async=handle_call_response_async,
        handle_stream=handle_stream,
        handle_stream_async=handle_stream_async,
        handle_base_model=handle_base_model,
        # handle_base_model_async=handle_base_model_async,
    )
