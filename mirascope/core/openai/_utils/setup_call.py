"""This module contains the setup_call function for OpenAI tools."""

import inspect
from typing import Any, Awaitable, Callable

from openai import AsyncAzureOpenAI, AsyncOpenAI, AzureOpenAI, OpenAI
from openai.types.chat import ChatCompletion, ChatCompletionMessageParam

from ...base import BaseTool, _utils
from ..call_params import OpenAICallParams
from ..dynamic_config import OpenAIDynamicConfig
from ..tool import OpenAITool


def setup_call(
    *,
    model: str,
    client: OpenAI | AsyncOpenAI | AzureOpenAI | AsyncAzureOpenAI | None,
    fn: Callable[..., OpenAIDynamicConfig | Awaitable[OpenAIDynamicConfig]],
    fn_args: dict[str, Any],
    dynamic_config: OpenAIDynamicConfig,
    tools: list[type[BaseTool] | Callable] | None,
    json_mode: bool,
    call_params: OpenAICallParams,
    extract: bool,
) -> tuple[
    Callable[..., ChatCompletion] | Callable[..., Awaitable[ChatCompletion]],
    str,
    list[ChatCompletionMessageParam],
    list[type[OpenAITool]] | None,
    dict[str, Any],
]:
    prompt_template, messages, tool_types, call_kwargs = _utils.setup_call(
        fn, fn_args, dynamic_config, tools, OpenAITool, call_params
    )
    if client is None:
        client = AsyncOpenAI() if inspect.iscoroutinefunction(fn) else OpenAI()
    create = client.chat.completions.create
    call_kwargs |= {"model": model, "messages": messages}
    if json_mode:
        call_kwargs["response_format"] = {"type": "json_object"}
        messages[-1]["content"] += _utils.json_mode_content(
            tool_types[0] if tool_types else None
        )
        call_kwargs.pop("tools", None)
    elif extract:
        assert tool_types, "At least one tool must be provided for extraction."
        call_kwargs["tool_choice"] = "required"

    return create, prompt_template, messages, tool_types, call_kwargs  # type: ignore
