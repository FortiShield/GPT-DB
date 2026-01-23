# gptdbs

[gptdbs](https://github.com/khulnasoft-bot/gptdbs) contains some data apps, AWEL operators, AWEL workflows, agents and resources 
which build upon the GPT-DB.

## Introduction

### Why We Need `gptdbs`

In a production-level LLM's application, there are many components that need to be
integrated, and you want to start your research and creativity quickly by using the 
existing components.

At the same time, we hope that the core components of GPT-DB keep simple and easy to
maintain, and some complex components can be developed in the form of plugins.

So, we need a plugin system to extend the capabilities of GPT-DB, and `gptdbs` is the
plugin system or a part of ecosystem of GPT-DB.

### What Is `gptdbs`

There are some concepts in `gptdbs`:
- `app`: It includes data apps, AWEL operators, AWEL workflows, agents and resources, sometimes, we
call it `gptdbs` app or `gptdbs` package.
- `repo`: It is a repository of `gptdbs` apps, you can install a `gptdbs` app from a `gptdbs` repo,
the default `gptdbs` repo is [khulnasoft-bot/gptdbs](https://github.com/khulnasoft-bot/gptdbs), you can
also create your own `gptdbs` repo or use other's `gptdbs` repo.

### How To Run `gptdbs`

1. When you install a `gptdbs` app, it will be loaded to your GPT-DB webserver automatically,
and you can use it in the GPT-DB webserver or trigger it by command line `gptdb run ...`.
2. You can also run a `gptdbs` app as a command line tool, you can use it in your terminal by
`gptdb app run ...` with `--local` option, it will run the app in your local environment.

## Quick Start

Let's install a `gptdbs` package named [awel-flow-simple-streaming-chat](https://github.com/khulnasoft-bot/gptdbs/tree/main/workflow/awel-flow-simple-streaming-chat)

```bash
gptdb app install awel-flow-simple-streaming-chat -U
```

### Run The App Locally

Then, you can run the app in your terminal:

```bash
gptdb run flow --local chat \
--name awel-flow-simple-streaming-chat \
--model "gpt-3.5-turbo" \
--messages "hello" \
--stream
```
- `gptdb run flow`: Means you want to run a AWEL workflow.
- `--local`: Means you want to run the workflow in your local environment without 
starting the GPT-DB webserver, it will find the `app` installed in your local 
environment, then run it, also, you can use `--file` to specify the python file.
- `--name`: The name of the app.
- `--model`: The LLM model you want to use,  `awel-flow-simple-streaming-chat` will 
use OpenAI LLM by default if you run it with `--local`.
- `--messages`: The messages you want to send to the LLM.
- `--stream`: Means you want to run the workflow in streaming mode.

The output will be like this:

```bash
You: hello
[~info] Chat stream started
[~info] JSON data: {"model": "gpt-3.5-turbo", "messages": "hello", "stream": true}
Bot: 
Hello! How can I assist you today?
🎉 Chat stream finished, timecost: 1.12 s
```

### Run The App In GPT-DB Webserver

After you install the `awel-flow-simple-streaming-chat` app, you can run it in the GPT-DB webserver.
Also, you can use the `gptdb` command line tool to trigger the app.

```bash
gptdb run flow chat \
--name awel-flow-simple-streaming-chat \
--model "chatgpt_proxyllm" \
--messages "hello" \
--stream
```

You just remove the `--local` option, then the command will connect to the GPT-DB webserver and run the app.
And you should modify the `--model` option to your model name in the GPT-DB webserver.

The output will be like this:

```bash
You: hello
[~info] Chat stream started
[~info] JSON data: {"model": "chatgpt_proxyllm", "messages": "hello", "stream": true, "chat_param": "1ecd35d4-a60a-420b-8943-8fc44f7f054a", "chat_mode": "chat_flow"}
Bot: 
Hello! How can I assist you today?
🎉 Chat stream finished, timecost: 0.98 s
```

## Run The App With `command` Mode

In previous examples, we run the app in `chat` mode, but not all `gptdbs` apps support `chat` mode,
some apps support `command` mode, you can run the app with `gptdb run flow cmd` command.

### Run The App Locally

```bash
gptdb run flow --local cmd \
--name awel-flow-simple-streaming-chat \
-d '
{
    "model": "gpt-3.5-turbo",
    "messages": "hello",
    "stream": true
}
'
```

We replace the `chat` mode with `cmd` mode, and use `-d` option to specify the data in JSON format.

The output will be like this:

```bash
[~info] Flow started
[~info] JSON data: {"model": "gpt-3.5-turbo", "messages": "hello", "stream": true}
Command output: 
Hello! How can I assist you today?
🎉 Flow finished, timecost: 1.35 s
```

### Run The App In GPT-DB Webserver

Just remove the `--local` option, then the command will connect to the GPT-DB webserver and run the app.

```bash
gptdb run flow cmd \
--name awel-flow-simple-streaming-chat \
-d '
{
    "model": "chatgpt_proxyllm",
    "messages": "hello",
    "stream": true
}
'
```

The output will be like this:

```bash
[~info] Flow started
[~info] JSON data: {"model": "chatgpt_proxyllm", "messages": "hello", "stream": true}
Command output: 
Hello! How can I assist you today?
🎉 Flow finished, timecost: 1.09 s
```

## `chat` Mode vs `command` Mode

In short, `chat` mode is used for chat applications, and `command` mode is used to 
trigger the app with a command.

For example, you want to load your documents to the GPT-DB, you can use `command` mode
to trigger the app to load the documents, it always runs once and the result will be
returned.

And `chat` mode is a special case of `command` mode, it provides a chat interface to
the user, and you can chat with the LLM in an interactive way.


## Run You App With Python Script

If you run app locally, it will find the app which is installed in your local environment,
also, you can run the app by providing the python file.

Let's create a python file named `simple_chat_app.py`:

```python
import os
from gptdb._private.pydantic import BaseModel, Field
from gptdb.core import ModelMessage, ModelRequest
from gptdb.core.awel import DAG, HttpTrigger, MapOperator
from gptdb.model.proxy import OpenAILLMClient
from gptdb.model.operators import LLMOperator


class TriggerReqBody(BaseModel):
    model: str = Field(..., description="Model name")
    messages: str = Field(..., description="User input")


class RequestHandleOperator(MapOperator[TriggerReqBody, ModelRequest]):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    async def map(self, input_value: TriggerReqBody) -> ModelRequest:
        messages = [ModelMessage.build_human_message(input_value.messages)]
        return ModelRequest.build_request(input_value.model, messages)


with DAG("gptdbs_simple_chat_app") as dag:
    # Receive http request and trigger dag to run.
    trigger = HttpTrigger(
        "/gptdbs/simple_chat_app", methods="POST", request_body=TriggerReqBody
    )
    llm_client = OpenAILLMClient(
        model_alias="gpt-3.5-turbo",  # or other models, eg. "gpt-4o"
        api_base=os.getenv("OPENAI_API_BASE"),
        api_key=os.getenv("OPENAI_API_KEY"),
    )
    request_handle_task = RequestHandleOperator()
    llm_task = LLMOperator(llm_client=llm_client)
    model_parse_task = MapOperator(lambda out: out.text)
    trigger >> request_handle_task >> llm_task >> model_parse_task
```

Then you can run the app by providing the python file:

```bash
gptdb run flow --local --file simple_chat_app.py \
chat \
--name gptdbs_simple_chat_app \
--model "gpt-3.5-turbo" \
--messages "hello"
```

The output will be like this:

```bash
You: hello
[~info] Chat started
[~info] JSON data: {"model": "gpt-3.5-turbo", "messages": "hello", "stream": false}
Bot: 
Hello! How can I assist you today?                                                                                                                                                       

🎉 Chat stream finished, timecost: 1.06 s
```

And you can run previous examples with `command` mode.

```bash
gptdb run flow --local --file simple_chat_app.py \
cmd \
--name gptdbs_simple_chat_app \
-d '
{
    "model": "gpt-3.5-turbo",
    "messages": "hello"
}'
```

The output will be like this:

```bash
[~info] Flow started
[~info] JSON data: {"model": "gpt-3.5-turbo", "messages": "hello"}
Command output: 
Hello! How can I assist you today?
🎉 Flow finished, timecost: 1.04 s
```

## Show Your App In GPT-DB Webserver

When you install the workflow, you can see the workflow in the GPT-DB webserver, you can open
the **AWEL Flow** page, then you can see the workflow named `awel_flow_simple_streaming_chat`.

<p align="left">
  <img src={'/img/gptdbs/awel_flow_simple_streaming_chat_1.png'} width="720px" />
</p>

Then you can click the `edit` button to see the details of the workflow.
<p align="left">
  <img src={'/img/gptdbs/awel_flow_simple_streaming_chat_2.png'} width="720px" />
</p>

Note: Not all workflows support editing, there are two types of workflows according to the
definition type: `json` and `python`, the `json` type workflow can be edited in the GPT-DB,
We will show you more details in the next sections.
