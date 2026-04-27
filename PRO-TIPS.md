# pro tips

high-leverage habits to apply right after the workshop.
each tip is in the format: `why` -> `command` -> `gotcha` -> `escape hatch`.

## tl;dr

1. alias `c` so launching claude is one keystroke in the CLI (intended for claude code CLI users)
2. switch models per task: sonnet default, opus for hard thinking, haiku for cheap iteration
3. plan your subagent orchestration before you start coding
4. dispatch independent work in parallel from a single message
5. lean on built-in skills instead of reinventing workflows

---

## 1. the `c` alias for fast claude code launching

### why
you will run `claude` hundreds of times. shaving it to one character matters more than it sounds. adding `--dangerously-skip-permissions` lets claude operate without per-action prompts, which is the difference between "babysitting an agent" and "letting it work."

### setup

zsh (macOS default):

```sh
echo 'alias c="claude --dangerously-skip-permissions"' >> ~/.zshrc
source ~/.zshrc
```

bash (most linux distros):

```sh
echo 'alias c="claude --dangerously-skip-permissions"' >> ~/.bashrc
source ~/.bashrc
```

fish:

```sh
echo 'alias c "claude --dangerously-skip-permissions"' >> ~/.config/fish/config.fish
source ~/.config/fish/config.fish
```

windows powershell (add to your `$PROFILE`):

```powershell
# open the profile in notepad
notepad $PROFILE

# then add one of these lines and save:
Set-Alias c claude

# or, if you want flags, use a function instead of an alias:
function c { claude --dangerously-skip-permissions @args }
```

reload powershell or run `. $PROFILE`.

windows cmd does not support real aliases. use a `c.bat` on your `PATH`:

```bat
@echo off
claude --dangerously-skip-permissions %*
```

### gotcha
`--dangerously-skip-permissions` is named that way for a reason. it disables the per-action permission prompts. that is fine on a sandbox repo, an isolated worktree, or a fresh project. it is NOT fine when:

- you are in a repo with prod credentials, secret files, or deploy hooks
- you do not trust the prompt you are about to give it
- you are running on a machine where claude can reach private infra (cloud accounts, k8s, internal tools)

if any of those apply, drop the flag.

### escape hatch
keep prompts on, just shorter:

```sh
alias c="claude"
```

or run claude raw without an alias. the alias is convenience, not a requirement.

---

## 2. switching models on the fly

### why
not every task needs the same model. 
- opus is great at reasoning but slow and expensive.
- haiku is fast and cheap, perfect for search-heavy work and simple edits.
- sonnet is the balanced default.

picking right per-task can 10x your throughput and cut spend. 
*this is important since you've got only $20 in credits for this workshop unless you've just got it like that. but unless you're mr. moneybags then try using smaller/cheaper models for smaller, simpler, isolated, or one-off tasks.*

### in an interactive session

```
/model
```

picks the default model for the current session. the picker shows the available options.

### one-shot model selection

start a session pinned to a specific model:

```sh
claude --model claude-opus-4-7
claude --model claude-sonnet-4-7
claude --model claude-haiku-4-5
```

run a single prompt against a specific model without entering interactive mode:

```sh
claude --model claude-opus-4-7 -- "explain the data flow in src/pipeline.ts"
```

### when to use which

- **sonnet** (default): general work, refactors, most coding tasks, balanced cost and speed. start here.
- **opus**: hard reasoning, architecture decisions, planning, debugging gnarly bugs, anything where being wrong is expensive. switch up when sonnet keeps getting it wrong.
- **haiku**: cheap fast iteration, simple edits, large codebase exploration, search and grep heavy work, batch dispatching to many subagents. switch down when the task is mechanical.

### gotcha
do not leave opus on for grunt work. you will burn budget on tasks haiku could do for a fraction of the cost. equally, do not try to force haiku through a task that needs real reasoning -- you will waste time on a model that cannot get there and end up rerunning on opus anyway.

### escape hatch
if you are not sure, default to sonnet. it is the right answer 70% of the time.

---

## 3. subagent orchestration: plan first, then implement

### why
the biggest mistake people make after the workshop is jumping straight into implementation with one giant claude session. subagents let you parallelize, isolate context, and keep the main session focused. but only if you decide your orchestration BEFORE you start.

### the pattern

1. **sketch the agents you need.** typical breakdown:
   - a researcher / explorer that scans the codebase
   - a planner that writes the spec
   - one or more implementers that actually write code
   - a reviewer that verifies before you merge
2. **decide task delegation.** which agent owns what? where do they hand off? what context does each one need?
3. **decide progress tracking.** are you using `TodoWrite` for the main session, status files in a scratch dir, or both?
4. **decide parallel vs sequential.** independent tasks go in parallel. tasks with shared state or order dependencies go sequential.
5. **THEN start the work.**

### built-in subagent types

dispatch these via the `Agent` tool inside a claude session:

- `Plan` -- design phase, writes specs and plans without touching code
- `Explore` -- codebase scans, "where does X live", "what calls Y"
- `general-purpose` -- arbitrary work, the catch-all

### parallel dispatch

for independent tasks, fire them off in a single message with multiple `Agent` tool calls. they run concurrently. one message, n agents, n results.

bad pattern (sequential, slow):

```
agent 1: read files in src/
... wait ...
agent 2: read files in tests/
... wait ...
agent 3: read files in scripts/
```

good pattern (parallel, fast):

```
single message with three Agent tool calls:
- agent A reads src/
- agent B reads tests/
- agent C reads scripts/
```

### useful skills

if you have superpowers installed, these wrap the orchestration patterns above:

- `superpowers:writing-plans` -- turns a spec into a written plan before any code
- `superpowers:executing-plans` -- runs a written plan with review checkpoints
- `superpowers:subagent-driven-development` -- delegates implementation to subagents
- `superpowers:dispatching-parallel-agents` -- the canonical "fan out independent work" pattern

invoke a skill via the `Skill` tool inside a session, or ask claude something like "use the writing-plans skill on this spec."

### gotcha
parallel only works for INDEPENDENT tasks. if agent B needs agent A's output, dispatching them in parallel just means B fails or guesses. when in doubt, sequential is safer; when correctness depends on shared state, sequential is required.

### escape hatch
when you are stuck, drop subagents entirely and run a single sonnet session. orchestration is a force multiplier, not a substitute for clear thinking.

---

## 4. parallel by default for independent work

### why
this is a corollary of tip 3, but it deserves its own callout because most users default to sequential out of habit. the rule: if two pieces of work do not share state and do not depend on each other's output, run them in parallel. always.

### examples that should be parallel

- reading three different directories
- running tests in three different packages
- searching for three different patterns across the repo
- ingesting five raw documents into a wiki
- generating three independent files

### how
inside a claude session, send a single message containing multiple tool calls. the harness will run them concurrently. claude will see all results and synthesize.

outside a session, run multiple `claude --model haiku --print "..."` invocations in shell parallelism (`&` and `wait`, or `xargs -P`).

### gotcha
parallel writes to the same file or same directory state will fight each other. parallel git commits in the same repo will fight each other. parallel writes to the same wiki page will fight each other. if work touches shared state, serialize it.

### escape hatch
if you cannot tell whether tasks share state, run sequentially. correctness beats speed.

---

## 5. lean on skills, do not reinvent

### why
skills are pre-built workflows. writing plans, executing plans, dispatching parallel agents, doing test-driven development, debugging systematically -- these are all shipped as skills. using them is faster and more reliable than rebuilding the same patterns by hand each time.

### the pattern

before you start a task, ask: "is there a skill for this?" common ones to know:

- `superpowers:brainstorming` -- before any creative or feature work, explore intent and design first
- `superpowers:writing-plans` -- turn a spec into a step-by-step plan
- `superpowers:executing-plans` -- run a plan with checkpoints
- `superpowers:test-driven-development` -- before you write any feature, write the failing test
- `superpowers:systematic-debugging` -- structured root cause analysis instead of guess-and-check
- `superpowers:verification-before-completion` -- run the verify step before you claim done
- `superpowers:requesting-code-review` -- send your branch for review against your own spec

invoke a skill by name in your prompt: "use the test-driven-development skill to add feature X."

### gotcha
skills can drift if you upgrade the plugin and your project notes still reference an old name. if a skill name does not work, list available skills (the harness shows them in the system prompt) and pick the current one.

### escape hatch
you can always do the work without a skill. they are accelerators, not gatekeepers.

---

## quick reference card

```sh
# launch claude fast
c

# launch with a specific model
claude --model claude-opus-4-7
claude --model claude-haiku-4-5

# one-shot prompt against opus
claude --model claude-opus-4-7 -- "your prompt here"

# inside an interactive session
/model              # change default model
/agents             # list configured subagents
```

orchestration mantra: plan -> delegate -> parallel where independent -> verify -> done.
