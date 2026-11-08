# Side Passage: The Sandbox Tide Pool (Floor 2 Sidequest)

[Back to Floor 2](../floor-2.md) | [All encounters](README.md) | [Dungeon map](../README.md) <!-- floor-nav -->

Files on this side passage: [`encounters/floor-2-sandbox-tide-pool/tide_pool.py`](../../encounters/floor-2-sandbox-tide-pool/tide_pool.py) <!-- floor-files -->

<!-- cordula-log -->
> <img src="../../images/cards/cast-cordula-640x640.webp" alt="Cordula" width="28" height="28"> **CORDULA'S LOG, SIDE PASSAGE OFF FLOOR 2.** On the bonus floor I let Kiro the Doomsday Scripter cast a scroll on my own gear, and I stood next to the approval prompt the whole time with a finger on the key. It worked. It also made me a very tired safety officer. In the eelgrass there is a better answer: a tide pool the size of a bathtub, rock walls, nothing in it that matters. You put the explosive in the pool. If it goes off, the pool gets a new rock. Barnaby lowered himself in to test the depth. "Sergeant, I submit that this is the first sensible arrangement we have been offered."
<!-- /cordula-log -->

> <img src="../../images/icons/system-ai-96x96.webp" alt="System AI" width="28" height="28"> **System AI:** "Sidequest: the Sandbox Tide Pool. Kiro the Doomsday Scripter, a crawler who treats code as demolition magic, will detonate things in a container instead of on your machine. The viewers are disappointed. The insurers are thrilled."

## The Brief

| | |
|---|---|
| type | sidequest |
| starts from | [Floor 2](../floor-2.md), finished, and its [bonus room](../floor-2.md#bonus-room-the-multi-tool-challenge-optional) if you did it: the same Kiro, the same Fibonacci scroll |
| you build | a Docker sandbox for the pool and an agent that works inside it, with no tool list at all |
| teaches | [`strands.sandbox.docker`](https://strandsagents.com/docs/api/python/strands.sandbox.docker/), [`strands.sandbox.posix_shell`](https://strandsagents.com/docs/api/python/strands.sandbox.posix_shell/) |
| time | about 15 minutes |
| model | Amazon Nova 2 Lite, as on every floor |

What you need installed: [Docker](https://docs.docker.com/get-started/get-docker/), running, with the `docker` command on your path. No extra Python package: the sandbox classes ship in the SDK you already have. The pool is the public [`python:3.13-slim`](https://hub.docker.com/_/python) image, roughly 50 megabytes the first time you pull it.

A sandbox is the place an agent's commands and files go. By default that place is your own machine. Give the agent a [sandbox](https://strandsagents.com/docs/user-guide/sdk/sandbox/) and the sandbox-aware tools route through it instead. `DockerSandbox` points at a container that is already running and sends each command there with `docker exec`. It is a `PosixShellSandbox`, the base class for any place where all you can do is run a shell command: that class builds file reads, file writes and code runs out of shell commands, so a new kind of sandbox only has to say how to run one command. See [Available Sandboxes](https://strandsagents.com/docs/user-guide/sdk/sandbox/available-sandboxes/).

The agent's tools come with it. A `DockerSandbox` vends two tools, `sandbox_shell` and `sandbox_file_editor`, and the agent registers them by itself. That is why the agent in this file has no `tools=` line.

How you know it worked: Kiro's `whoami` answers `nobody`, which is not you; the scroll prints from inside the pool; and the last line of the run says there is no `scroll.py` in your folder on your machine.

Start the pool, then go to the encounter folder:

```bash
docker run -d --name tide-pool python:3.13-slim sleep infinity
cd aiRPG-seattle-dungeon-crawl/encounters/floor-2-sandbox-tide-pool
```

`sleep infinity` keeps the container alive with nothing in it, which is all a pool needs to do.

## Step 1: Import the Sandbox Classes

```python
# TODO: Step 1 - Import DockerSandbox from strands.sandbox.docker and PosixShellSandbox from strands.sandbox.posix_shell
```

`DockerSandbox` is the pool. `PosixShellSandbox` is what the given `check_pool` function tests it against, so a wrong kind of object fails with a plain message instead of in the middle of a run. `DockerSandbox` is not exported from `strands.sandbox` itself; import it from its own module.

<details>
<summary>Show me the code for Step 1</summary>

```python
# TODO: Step 1 - Import DockerSandbox from strands.sandbox.docker and PosixShellSandbox from strands.sandbox.posix_shell
from strands.sandbox.docker import DockerSandbox
from strands.sandbox.posix_shell import PosixShellSandbox
```

</details>

## Step 2: Build the Pool

```python
# TODO: Step 2 - Build a DockerSandbox for the CONTAINER, with working_dir "/tmp" and user "nobody", as pool
pool = None
```

`DockerSandbox(container, working_dir=..., user=...)` takes the name of a running container. `working_dir` is where commands start and it must exist and be writable by the user; `/tmp` is both. `user` is who the commands run as: `nobody` is a user with no home and no power, so even a scroll that behaves badly cannot do much to the container. Without it, commands run as whoever the image is set to run as, often root.

> <img src="../../images/cards/cast-cordula-640x640.webp" alt="Cordula" width="28" height="28"> **CORDULA:** Two walls on the pool, not one. The container is the first wall: the scroll can only touch what is inside it. The user is the second: inside the container it still carries nothing. Nobody asked for a belt and braces. A crew chief puts a second strap on any load she would hate to lose.

<details>
<summary>Show me the code for Step 2</summary>

```python
# TODO: Step 2 - Build a DockerSandbox for the CONTAINER, with working_dir "/tmp" and user "nobody", as pool
pool = DockerSandbox(CONTAINER, working_dir="/tmp", user="nobody")
```

Trap: the container has to exist and be running before the agent's first tool call, not before the import. Build the sandbox without a container and nothing complains until Kiro tries to cast. If you see `No such container`, you skipped the `docker run` above.

</details>

## Step 3: Give the Agent the Pool

```python
# TODO: Step 3 - Give the agent the pool as its sandbox
```

`Agent` takes a `sandbox` parameter. When it has one, the agent registers the sandbox's own tools, named for the container so the model knows where they run. The prompt names them, `sandbox_file_editor` and `sandbox_shell`, so Kiro reaches for those and not for something it remembers from the bonus floor.

<details>
<summary>Show me the code for Step 3</summary>

```python
        # TODO: Step 3 - Give the agent the pool as its sandbox
        sandbox=pool,
```

</details>

## Step 4: Read the Scroll Back from the Pool

```python
# TODO: Step 4 - Read the scroll back from inside the pool with pool.read_text (an async method: run it with asyncio.run) and print it
```

Sandbox methods are async, because a sandbox may be a container, a server across the network or a cloud runtime. `asyncio.run(...)` runs one to completion from plain code. `read_text` goes through the same `docker exec` as everything else, so what it returns is what is in the pool, not what is on your disk.

> <img src="../../images/cards/cast-cordula-640x640.webp" alt="Cordula" width="28" height="28"> **CORDULA:** The last line of the run is the one I care about. It asks whether a `scroll.py` landed in my folder. It did not. Everything Kiro wrote is in the pool and nowhere else, which means I can drain the pool and the scroll is gone, with no cleanup list. Barnaby said it is the only cleanup he has ever approved of.

<details>
<summary>Show me the code for Step 4</summary>

```python
    # TODO: Step 4 - Read the scroll back from inside the pool with pool.read_text (an async method: run it with asyncio.run) and print it
    print(f"\nThe scroll, read from inside the pool:\n{asyncio.run(pool.read_text(SCROLL))}")
```

</details>

## Run It

```bash
python tide_pool.py
```

Check: Kiro narrates the scroll, the Fibonacci numbers, and the user. Your wording will differ; this is an example:

```
Kiro: The scroll is inscribed and cast. It printed 0 1 1 2 3 5 8 13 21 34 and did not detonate. Inside the pool I am nobody, which is the safest thing I have ever been.

The scroll, read from inside the pool:
a, b = 0, 1
for _ in range(10):
    print(a)
    a, b = b, a + b

A scroll.py in this folder on your machine? False
```

When you are done, drain the pool:

```bash
docker rm -f tide-pool
```

| you see | it means | fix |
|---|---|---|
| `docker is not installed or not on PATH` | the `docker` command was not found | install Docker and open a new terminal |
| `No such container: tide-pool` | the pool is not running | run the `docker run` command above |
| `TypeError: expected a PosixShellSandbox` | `pool` is still `None` or the wrong object | finish Step 2 |
| `Permission denied` in the tool result | the user cannot write where Kiro tried | keep scrolls under `/tmp`, the `working_dir` |
| Kiro uses `shell` and runs on your machine | the prompt or tools are from the bonus floor | this file lists no tools; remove any `tools=` you added |
| `AccessDeniedException` or `ExpiredToken` | the model call failed | [Floor 0, Step 7](../floor-0.md#step-7-check-your-pass-to-the-model-aws) |

## Pool Against Prompt

The bonus room guarded the shell with a person: every call stopped and waited for a yes. The pool guards it with a place: the call runs, and what it can reach is small. They answer different questions. The prompt asks whether this particular call should happen at all. The pool asks how much damage any call can do. A careful setup uses both, and [The Policy Gatekeeper](policy-gatekeeper.md) is where they meet.

A sandbox is not a guarantee. The container shares your machine's kernel, it can reach the network unless you start it with `--network none`, and a pool that mounts your folders lets a scroll reach them. This pool mounts nothing, which is why it is a good one; add `--network none` to the `docker run` line if the scrolls do not need the internet.

## What It Costs

Docker and the image are free. The model side is about 5 calls at roughly 2,000 input tokens each, 10,000 input tokens at $0.30 per million, $0.003, plus about 800 output tokens at $2.50 per million, $0.002. About half a cent a run. See [What a Turn Costs](../floor-1.md#what-a-turn-costs).

## Encounter Clear

Loot you're keeping:

- `DockerSandbox`: a running container as the place an agent's commands and files go
- `PosixShellSandbox`: why one method, run a command, is enough to make a sandbox
- The agent's `sandbox` parameter, and the tools a sandbox brings with it
- Running commands as a user with no power, inside a container with no mounts

> <img src="../../images/icons/achievement-96x96.webp" alt="Achievement" width="28" height="28"> **NEW ACHIEVEMENT UNLOCKED!**
>
> **[BATHTUB DEMOLITION]**
>
> Reward: You received a [Silver Box]. Inside: a pair of safety goggles, a lid for the tide pool, and one spare rock.

Back to [Floor 2](../floor-2.md#floor-clear), or on to [The Policy Gatekeeper](policy-gatekeeper.md).
