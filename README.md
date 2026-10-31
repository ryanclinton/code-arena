# CodeArena

A local, LeetCode-style coding practice app. Solve problems in **Python** or **Java** in a
browser editor, **Run** your code against sample cases, then **Submit** against the full hidden
suite (edge cases and large inputs), with runtime and memory measured.

```bash
python3 -m venv .venv                     # one-time setup
.venv/bin/pip install -r requirements.txt # currently a no-op; ready for future packages
.venv/bin/python server.py                # then open http://127.0.0.1:8000
```

Requirements: Python 3.10+ (the app itself uses only the standard library). Java support needs a
JDK (`java` + `javac`) on your `PATH`.

Your Python solutions run with the same interpreter as the server. Anything you install
into `.venv` (for example `sortedcontainers`) can be imported from your solutions too. The editor (Monaco) and Markdown renderer load from a CDN; offline, the app falls
back to a plain text editor.

## Features

- Problem list with search, difficulty/status filters and a progress tracker
- **Group by** topic, tag or difficulty, with a solved count per group; click a group header to collapse it
- Monaco editor with reset to starter code
- **Progress is saved automatically** (see [Saving progress](#saving-progress))
- **Run**: runs the editable test cases (add your own; expected output comes from the reference solution)
- **Submit**: runs every test, stops at the first failure and shows that input, your output and the expected output
- Verdicts: Accepted, Wrong Answer, Runtime Error, Compile Error, Time Limit Exceeded
- Runtime (time inside your function, summed over all tests), peak memory, slowest test, and a
  comparison with the reference solution in the same language
- `print` / `System.out` output captured per test
- **Solution** tab: explanation plus reference code in each language, with "Copy to editor"
- Submission history per problem; click one to load its code back into the editor
- Shortcuts: `Ctrl/⌘ + '` runs, `Ctrl/⌘ + Enter` submits, `Ctrl/⌘ + S` saves now

## Saving progress

Everything you do is saved on the server in `data/codearena.db` (a single SQLite file):

- your code for every problem and language, saved shortly after you stop typing,
  when you run or submit, when you switch problems and when you close the tab
  (`Ctrl/⌘ + S` saves immediately; the toolbar shows *Saved ✓*)
- your custom test cases
- every submission, with verdict, runtime, memory and the code you submitted
- solved / attempted status, which is derived from your submissions

Because it lives on disk rather than in the browser, it survives clearing browser data and works
from any browser. **Back up or move your progress by copying `data/codearena.db`**. Set
`CODEARENA_DB=/path/to/file.db` to keep it somewhere else. Theme, layout and preferred language stay
per-browser. Progress saved in the browser by earlier versions is imported automatically on first load.

## Project layout

```
server.py                    HTTP server + JSON API (stdlib only)
judge/
  types.py                   language-neutral type grammar (int, string[], list<list<int>>, ...)
  challenges.py              discovers and loads challenges/
  compare.py                 answer comparison modes
  runner.py                  compiles, runs, enforces time limits, measures memory, grades
  storage.py                 saved code, test cases and submissions (SQLite)
  languages/                 one plugin per language (auto-discovered)
    base.py                  Language base class
    python.py, java.py
  harness/                   per-language test harnesses that call the user's Solution
  testgen.py                 random tree generators for tests.py files
challenges/<id>/             one folder per challenge
static/                      front end (index.html, app.js, style.css)
data/codearena.db            your saved progress (created on first run)
tools/check_challenges.py    submits every reference solution to verify a challenge
```

## Adding a challenge

Create `challenges/<id>/` (the folder name is the id) with:

| File | Purpose |
|---|---|
| `problem.json` | title, difficulty, order, tags, signature, compare mode, time limit |
| `description.md` | the problem statement (Markdown) |
| `tests.py` | `SAMPLE` list and `hidden(rng)` function |
| `solutions/solution.py` | Python reference (**required**: it computes expected outputs) |
| `solutions/Solution.java` | Java reference (shown in the Solution tab, used for runtime comparison) |
| `solutions/README.md` | explanation shown in the Solution tab |
| `validator.py` | optional, for problems with several correct answers |
| `starters/<file>` | optional hand-written starter code (otherwise generated from the signature) |

**`problem.json`**

```json
{
  "title": "Two Sum",
  "difficulty": "Easy",
  "order": 1,
  "category": "Hash Table",
  "tags": ["Array", "Hash Table"],
  "signature": {
    "method": "twoSum",
    "params": [{"name": "nums", "type": "int[]"}, {"name": "target", "type": "int"}],
    "returns": "int[]"
  },
  "compare": "exact",
  "time_limit_ms": 1500
}
```

- **`category`:** the main topic, used by *Group by topic* (for example `Linked List`, `Tree`,
  `Graph`, `Binary Search`). It defaults to the first tag. `tags` can list several; *Group by tag*
  shows a problem under each of them.
- **Types:** `int`, `long`, `double`, `boolean`, `char`, `string`, `void`, arrays `T[]`, lists `list<T>`,
  and the node types `ListNode` and `TreeNode`. Starter code for every language is generated from these.
- **Node types:** in tests (and in the UI) a `ListNode` is written as an array, `[1,2,3]`, and a
  `TreeNode` in LeetCode's level order with `null` for missing children, `[1,null,2]`. `[]` is an empty
  list or tree. The harnesses build real nodes before calling the solution and turn the returned nodes
  back into arrays, so `tests.py` and the expected outputs only deal with plain lists. The classes are
  predefined in every language (`judge/harness/python/prelude.py`, `judge/harness/java/ListNode.java`
  and `TreeNode.java`), so solutions don't define them. A returned list or tree with a cycle is
  reported as a Runtime Error.
- **Graphs** don't need a special type: use edge lists (`int[][]`), adjacency lists or grids (`char[][]`).
- **In-place problems:** use `"returns": "void"` with `"output_arg": 0` to grade the mutated argument.
- **`compare`:** `exact` (doubles compared within 1e-5), `unordered` (outer list order ignored),
  `unordered_nested` (order ignored at both levels), or `validator`.
- **`time_limit_ms`:** total time for all tests in Java. Each language scales it (Python × 4).

**`tests.py`**

```python
SAMPLE = [                       # shown as examples and used by Run
    {"args": [[2, 7, 11, 15], 9]},
]

def hidden(rng):                 # rng is a random.Random seeded with the challenge id
    cases = [{"name": "minimum length", "args": [[1, 2], 3]}]   # named edge cases
    for _ in range(20):
        nums = [rng.randint(-50, 50) for _ in range(rng.randint(2, 20))]
        cases.append({"args": [nums, nums[0] + nums[1]]})
    return cases
```

Omit `"expected"` and it is computed by the Python reference solution, so large generated inputs
cost nothing to write. A `"name"` is shown when that test fails.

For tree inputs, `judge/testgen.py` has generators that return the level-order form:
`random_tree`, `random_bst`, `skewed_tree` (deep chains), `zigzag_tree` and `level_order`.

```python
from judge.testgen import random_tree, skewed_tree

def hidden(rng):
    return [{"name": "deep chain", "args": [skewed_tree(list(range(5000)))]},
            {"args": [random_tree(rng, 10_000)]}]
```

**`validator.py`** (when `"compare": "validator"`):

```python
def validate(args, expected, actual):
    return True                  # or (False, "explanation shown to the user")
```

Then verify it:

```bash
python3 tools/check_challenges.py <id>
```

New challenges show up after a server restart.

## Adding a language

1. Create `judge/languages/<lang>.py` with a `Language` subclass decorated with `@register`. It sets
   `id`, `name`, `monaco_language` and `solution_filename`, and implements:
   - `type_name(t)` and `starter_code(sig)`: map the type grammar to the language
   - `prepare(workdir, code)`: write the code and compile it, returning a `PrepareResult`
   - `run_command(workdir, job_path, results_path)`: the command that runs your harness
2. Write a harness in `judge/harness/<lang>/` that reads the job JSON
   (`method`, `param_types`, `output_arg`, `tests`), calls `Solution().<method>(...)` on each test with
   a fresh instance, and writes one JSON line per test. Arguments and results of type `ListNode` /
   `TreeNode` arrive and leave as arrays (see *Node types*), so the harness converts them:
   `{"i": 0, "status": "ok", "output": ..., "time_ns": 1234, "stdout": ""}` or
   `{"i": 0, "status": "error", "error": "...", "stdout": ""}`
   (or a single `{"fatal": "..."}` line if the code can't be loaded).
3. Add `solutions/<solution_filename>` to challenges as you go.

The judge handles timeouts, memory measurement, grading and the UI. The Java harness
(`Main.java` + `Json.java`) is a good template: it uses reflection, so it never needs code
generation per problem.

## Notes

- Your code runs as a local process with your user's permissions. That's fine for personal
  practice, but don't expose the server to untrusted users.
- Memory is the peak resident size of the whole process, so it includes the Python interpreter's
  or the JVM's baseline. Compare against the reference numbers, not against LeetCode's.
