# GenAI CLI
This is the CLI for GenAI infrastructure. It allows you to register, create and run agent files

# 🛠️ Installation
## ⬇️ Download pre-built binary

### 🐧 Linux/ 🍏 Mac OS:
Run `./install_cli.sh`, enter your OS user's password when prompted - to copy the binary file into the `/usr/local/bin` and make it executable globally on your unix machine

⌨️ To test that `genai` was installed successfully - run:

`genai --help`, it should return:
```
                                                                                                                                                                                                                    
 Usage: genai [OPTIONS] COMMAND [ARGS]...                                                                                                                                                                            
                                                                                                                                                                                                                     
 GenAI CLI app                                                                                                                                                                                                       
                                                                                                                                                                                                                     
╭─ Options ─────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────╮
│ --install-completion          Install completion for the current shell.                                                                                                                                           │
│ --show-completion             Show completion for the current shell, to copy it or customize the installation.                                                                                                    │
│ --help                        Show this message and exit.                                                                                                                                                         │
╰───────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────╯
╭─ Commands ────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────╮
│ login                                                                                                                                                                                                             │
│ signup                                                                                                                                                                                                            │
│ logout                                                                                                                                                                                                            │
│ list_agents                                                                                                                                                                                                       │
│ register_agent                                                                                                                                                                                                    │
│ delete_agent                                                                                                                                                                                                      │
│ generate_agent                                                                                                                                                                                                    │
│ run_agents                                                                                                                                                                                                        │
╰───────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────╯
```
## Windows
Set env variable with github_token: `[Environment]::SetEnvironmentVariable("GITHUB_TOKEN", "your_token_here", "User")` in powershell
Then download genai cli executable via `.\install_cli.ps1`
**TODO: remove this after monorepo content is public**

Use `genai`: `.\genai.exe --help`

### 🤖 Building from source
### 🐧 Linux/ 🍏 Mac OS:
Simpliest way to build the binary of CLI with `pyinstaller` - use `./build_cli.sh`

Otherwise, you need to ensure that `python3.12`, `uv` are installed. If that's the case, run - `uv run pyinstaller --onefile --name genai.bin cli.py`

### Windows
Simpliest way to build the binary of CLI for Windows - use `./build_cli.ps1`. 
`./build_cli.ps1` uses `Nuitka` to translate the Python modules into a C level program that then uses libpython and static C files of its own to execute in the same way as CPython does. By using `Nuitka` - Windows Defender won't recognize `genai.exe` as a malware, as it will with `genai.exe` built with `pyinstaller` 


---

# ⌨️ CLI Usage
👤 GenAI infrastructure is sharing one user entity across all of the GenAI infrastructure.

GenAI CLI is built on [`Typer`](https://typer.tiangolo.com/) framework, which supports [`Rich`](https://github.com/Textualize/rich) color scheme CLI outputs and static typing features.

To list all available commands:
```sh
genai --help
```
Which will return the data about all supported commands.

If you already had a user created in `front-end` or `back-end` apps and haven't logged in to the CLI, run - `genai login -u <your_username> -p <your_password>`

⚠️ **All of the commands related to the agent require you to be logged in as `genai` user.** ⚠️

GenAI CLI will create a `~/.genai/credentials` file with your user's JWT token. This token is validated every time you request any of the agent related commands

If this is your first time using `genai` - proceed with registering your GenAI user - `genai register -u my_new_user`


## ✍️ Working with agents:
🤖 Agents are concidered valid when `python` syntax inside of the file is valid, GenAI infrastructure is used correctly and your agent's `python` dependencies (packages like `requests`) were installed correctly.

Do not worry - CLI is here to help you.

### 🤖 Creating your first 🤖 agent

⚠️ Make sure you're logged in with your GenAI user. ⚠️

Run `genai register_agent --name my_cool_agent --description 'this cool agent does something amazing` where `--name` and `--description` are the required fields. The more descriptive `name` and `description` are, the better accuracy of agent invocation you'll get ☝️🤓

As a result the following event flow happens - metadata of your agent is created in the database and the agent's python file is created in the `agents/` folder. 

When you've registered your agent - it is getting a JWT token from the back-end. By checking this JWT back-end knows if the agent is registered/active in the system or not. **Do not modify this JWT token or your agent will be always inactive**

Before running this agent, you need to create a virtual environment with the dependencies of the agent. The simpliest way to do so - change directory to `agents/<your_agent_name>` -> `uv venv` -> `uv sync`.

*Even though `uv` is recommended to use with `genai` infrastructure, you can achieve the same results with plain `python3 -m venv venv` or other virtual environment managers.*

### 🏃‍➡️ Running your agents
Now you should have at least one agent. There is no hard limit on the amount of agents you can create locally. Sky is the limit!

⁉️ But now were getting to the following problem: 

⚠️ **Your agents are isolated `python` files/processes, which might have different dependencies that are necessary to start `python` process.** ⚠️

When you've created the agents via `register_agent` or `generate_agent`, *`pyproject.toml`* file was added for you. 

This is a file that lists the minimal amount of dependencies needed to run the agent in the GenAI infrastructure, we recommend using uv to manage your agent dependencies.

⚠️ `genai run_agents` command expects every agent within `agents/` folder to have a virtual environment folder named `venv` or `.venv`. These virtual environments are gonna be used to run your agents. ⚠️

❌ If no `.venv` folder was found within the agent's folder, `genai` will fallback to parent `agents/` folder and will try to find an virtual environment there. If no virtual environment was found - `genai` will return an error message that no virtual environments were found. ❌

✅ You've created the agents, you've created virtual environments, in that case `genai run_agents` will run all available agents from the `agents/` folder. These agents will start up in the terminal window and will be ready to roll! ✅

### Registering the Agents via API and generating the agents afterwards:
For some reason `register_agent` command did not satisfy your needs and you want to register your agent yourself before generating the file for it.

To do so - visit `http://localhost:8000/docs` -> login/register a user (if not done previously) -> login in swagger docs -> make a POST request to `/api/agents/register` endpoint via `Swagger` docs or HTTP request manager of choice (like `Postman`). Submit the necessary information for your agent. If your request fails, please resolve any error messages returned in the response.
⚠️ **NOTE: if you've created an agent and specified the `input_parameters` manually, `input_parameters` will be overwritten with the agent's metadata whenever you're gonna run the agent for the first time.**

If you've successfully registered the agent via API, you're gonna the following response:
```json
{
  "name": "my_cool_agent",
  "description": "my cool agent that does something great",
  "id": "df82f8a0-052a-4f9d-b33c-2ada03619631",
  "input_parameters": {},
  "output_parameters": {},
  "created_at": "2025-05-02T16:05:19.973773",
  "updated_at": "2025-05-02T16:05:19.973773",
  "jwt": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJkZjgyZjhhMC0wNTJhLTRmOWQtYjMzYy0yYWRhMDM2MTk2MzEiLCJleHAiOjI1MzQwMjMwMDc5OSwidXNlcl9pZCI6ImNkYjczZjJlLTBlMGMtNDQzMC05ZTVjLTQ4NWUwNjAxZTVlNCJ9.XUfmUsUab3ViHFOHcVY7fPPxlBSI9nMbSEeBSeEIRGU"
}
```
Notice the `jwt` field. You need to paste this token into the agent's file. Like so: 

```python
session = GenAISession(
    jwt_token="eyJzdWIiOiJkZjgyZjhhMC0wNTJhLTRmOWQtYjMzYy0yYWRhMDM2MTk2MzEiLCJleHAiOjI1MzQwMjMwMDc5OSwidXNlcl9pZCI6ImNkYjczZjJlLTBlMGMtNDQzMC05ZTVjLTQ4NWUwNjAxZTVlNCJ9.XUfmUsUab3ViHFOHcVY7fPPxlBSI9nMbSEeBSeEIRGU",
)
```
This is gonna be the identifier for your agent. 

Now you need to generate the agent body - run: `genai generate_agent --id df82f8a0-052a-4f9d-b33c-2ada03619631`. This is the `id` from the previous step.

If you've provided the correct id during `generate_agent` step, you should see your agent being created in the `agents/` folder in the root of the monorepo.

It will have the following structure:
**Replace the value of `AGENT_JWT` with the JWT token you've received from the API**
```python
import asyncio
from typing import Annotated
from genai_session.session import GenAISession
from genai_session.utils.context import GenAIContext

AGENT_JWT = "eyJzdWIiOiJkZjgyZjhhMC0wNTJhLTRmOWQtYjMzYy0yYWRhMDM2MTk2MzEiLCJleHAiOjI1MzQwMjMwMDc5OSwidXNlcl9pZCI6ImNkYjczZjJlLTBlMGMtNDQzMC05ZTVjLTQ4NWUwNjAxZTVlNCJ9.XUfmUsUab3ViHFOHcVY7fPPxlBSI9nMbSEeBSeEIRGU" # noqa: E501
session = GenAISession(jwt_token=AGENT_JWT)


@session.bind(
    name="my_cool_agent",
    description="my cool agent that does something great"
)
async def my_cool_agent(
    agent_context: GenAIContext,
    test_arg: Annotated[
        str,
        "This is a test argument. Your agent can have as many parameters as you want. Feel free to rename or adjust it to your needs.",  # noqa: E501
    ],
):
    """my cool agent that does something great"""
    return "Hello, World!"


async def main():
    print(f"Agent with token '{AGENT_JWT}' started")
    await session.process_events()

if __name__ == "__main__":
    asyncio.run(main())

```

This is a template for your agents in `python`. Feel free to do whatever you like with it. 

✅ Do not forget about building a venv for your agent, but now you're ready to start your agent with `python my_agent` or `genai run_agents` ✅

