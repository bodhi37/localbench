"""Graders.

Every unit — hand-built task or published benchmark item — resolves to
``(passed, detail)`` from one function in :data:`GRADERS`.

  verify    custom task's own ``verify.py`` (may grade files the agent wrote)
  mcq       multiple choice: extract a final option letter
  exact     short/structured answer: extract a final line, compare normalised
  math      numeric or symbolic answer: extract, then numeric-or-normalised match
  code      extract the model's program, run the benchmark's own test suite
  ifeval    official IFEval strict score (vendored Google checkers)

Every grader is a pure function of (response text, out_dir, unit answer/meta):
no network, no clock, no RNG, so the same response always grades the same way.
"""
from __future__ import annotations

import json
import math
import os
import re
import shutil
import signal
import subprocess
import sys
import tempfile
from pathlib import Path
from typing import Any, Callable, Optional

Result = tuple[bool, str]

MAX_DETAIL = 400


def _clip(s: Any, n: int = MAX_DETAIL) -> str:
    s = "" if s is None else str(s)
    s = " ".join(str(s).split())
    return s if len(s) <= n else s[: n - 1] + "…"


# --------------------------------------------------------------------------- #
# helpers shared by the text graders
# --------------------------------------------------------------------------- #

def _lines(text: str) -> list[str]:
    return [ln.strip() for ln in (text or "").splitlines() if ln.strip()]


def _final_line(text: str) -> Optional[str]:
    """The value on the last ``FINAL:`` line, else the last non-empty line."""
    for ln in reversed(_lines(text)):
        if ln.upper().startswith("FINAL:"):
            return ln.split(":", 1)[1].strip()
    ls = _lines(text)
    return ls[-1] if ls else None


# --------------------------------------------------------------------------- #
# verify — the custom task's own verifier
# --------------------------------------------------------------------------- #

_VERIFY_TIMEOUT = 300


def _verify_policy() -> tuple[bool, str]:
    """``(sandbox?, fatal)`` — must verifiers run under bubblewrap?

    Config-gated, because the sandbox gate is config: CI and library use have
    no ``config/local.json`` (no promise was made, and often no bubblewrap
    either), so verification runs as a plain subprocess there. When the config
    *does* ask for a sandbox this fails **closed** if bubblewrap is missing —
    verifiers are third-party code that may execute model output, and they
    must not run on the host with the host's network, secrets and filesystem
    just because a dependency is missing.
    """
    try:
        from .config import harness_cfg
        if not harness_cfg().get("sandbox", True):
            return False, ""
    except Exception:
        return False, ""
    if not shutil.which("bwrap"):
        return False, ("verification requires the sandbox but bubblewrap is "
                       "missing — install bubblewrap, or set \"sandbox\": "
                       "false under \"harness\" in config/local.json")
    return True, ""


def _verify_argv(unit, out_dir: Path, scratch: Path,
                 sandbox: bool) -> tuple[list[str], dict[str, str]]:
    """The verifier's invocation — argv and env, identical contract either way.

    The verifier contract itself never changes (``--task-dir --out-dir
    --response``); the sandbox only constrains *where* it may reach:

      * task dir   read-only  — gold answers and tests cannot be rewritten,
      * out dir    read/write — it reads ``response.txt`` and may log,
      * scratch    cwd + HOME + TMPDIR — nothing else is writable,
      * network    gone       — ``--unshare-net``, not proxy variables,
      * processes  gone       — ``--unshare-pid``: killing the verifier kills
        pid 1 of its namespace and with it every child it spawned,
      * environment scrubbed, ``PYTHONHASHSEED=0`` — same verdict per run.

    Bind order matters: anything that lives under a tmpfs-shadowed tree
    (``/tmp``, ``/home``, ``/var``) must be mounted *after* that tmpfs.
    """
    base = [sys.executable, str(unit.task_dir / "verify.py"),
            "--task-dir", str(unit.task_dir), "--out-dir", str(out_dir),
            "--response", str(out_dir / "response.txt")]
    pybin = str(Path(sys.executable).parent)
    env = {"PATH": ":".join(dict.fromkeys(
               [pybin, "/usr/local/bin", "/usr/bin", "/bin"])),
           "HOME": str(scratch), "TMPDIR": str(scratch),
           "LANG": "C.UTF-8", "LC_ALL": "C.UTF-8", "TZ": "UTC",
           "PYTHONHASHSEED": "0"}
    if not sandbox:
        return base, env

    argv = [shutil.which("bwrap") or "bwrap",
            "--unshare-net", "--unshare-pid",
            "--ro-bind", "/usr", "/usr",
            "--ro-bind", "/etc", "/etc",
            "--dev", "/dev", "--proc", "/proc",
            "--tmpfs", "/tmp", "--tmpfs", "/home", "--tmpfs", "/var",
            "--symlink", "usr/lib64", "/lib64"]
    for p in dict.fromkeys(x for x in (sys.prefix, sys.base_prefix) if x):
        if not p.startswith("/usr") and Path(p).is_dir():
            argv += ["--ro-bind", p, p]
    argv += ["--bind", str(scratch), str(scratch),
             "--ro-bind", str(unit.task_dir), str(unit.task_dir),
             "--bind", str(out_dir), str(out_dir),
             "--die-with-parent", "--new-session",
             "--chdir", str(scratch)]
    for k in ("PATH", "HOME", "TMPDIR", "LANG", "LC_ALL", "TZ",
              "PYTHONHASHSEED"):
        argv += ["--setenv", k, env[k]]
    return argv + ["--"] + base, env


def _kill_tree(proc: subprocess.Popen) -> None:
    """SIGKILL the verifier's whole process group (verify + anything it ran)."""
    try:
        os.killpg(os.getpgid(proc.pid), signal.SIGKILL)
    except (ProcessLookupError, PermissionError, OSError):
        pass


def grade_verify(unit, out_dir: Path, response: str) -> Result:
    verify = unit.task_dir / "verify.py"
    if not verify.is_file():
        return False, f"missing {verify}"
    sandbox, err = _verify_policy()
    if err:
        return False, err

    stdout = stderr = ""
    with tempfile.TemporaryDirectory(prefix="lb-verify-") as td:
        scratch = Path(td)
        argv, env = _verify_argv(unit, out_dir, scratch, sandbox)
        try:
            proc = subprocess.Popen(
                argv, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                text=True, env=env, cwd=scratch, start_new_session=True)
        except OSError as e:
            return False, f"verifier could not run: {e}"
        try:
            stdout, stderr = proc.communicate(timeout=_VERIFY_TIMEOUT)
        except subprocess.TimeoutExpired:
            _kill_tree(proc)
            try:
                proc.communicate(timeout=20)
            except Exception:
                pass
            return False, f"verifier timed out after {_VERIFY_TIMEOUT}s"

    detail, ok = _clip(stdout.strip()), proc.returncode == 0
    for line in reversed(stdout.strip().splitlines()):
        line = line.strip()
        if line.startswith("{"):
            try:
                obj = json.loads(line)
            except json.JSONDecodeError:
                break
            if "pass" in obj:
                ok = bool(obj["pass"])
                detail = _clip(obj.get("detail", detail))
            break
    if not detail:
        detail = f"verify rc={proc.returncode}" + (
            f" {stderr.strip()[:120]}" if stderr.strip() else "")
    return ok, detail


# --------------------------------------------------------------------------- #
# mcq
# --------------------------------------------------------------------------- #

_LETTER = r"([A-Z])"
_FINAL_LETTER = re.compile(rf"^FINAL:\s*[\"'(]*{_LETTER}[\"')\].,:]?\s*$", re.I)
_ANY_FINAL_LETTER = re.compile(rf"\bFINAL:\s*[\"'(]*({_LETTER})\b", re.I)
_ANSWER_LETTER = re.compile(
    rf"\b(?:answer|option|choice)\s*(?:is|:|=)\s*[\"'(]*({_LETTER})\b", re.I)
_TRAILING_LETTER = re.compile(rf"\b({_LETTER})[.\s]*$", re.I)
_MD_EMPHASIS = re.compile(r"[*_`]+")
"""Markdown emphasis — ``**B**``, ``__B__``, ``` `B` ``` are not content."""


def _extract_letter(text: str) -> Optional[str]:
    # Models wrap the answer in emphasis ("FINAL: **B**", "**Answer:** C");
    # none of the patterns below should have to know that. Emphasis marks are
    # stripped up front, which is safe here: option letters are A–Z prose.
    text = _MD_EMPHASIS.sub("", text or "")
    lines = _lines(text)
    last = lines[-1] if lines else ""
    for pat in (_FINAL_LETTER,):
        if last and (m := pat.match(last)):
            return m.group(1).upper()
    for pat in (_ANY_FINAL_LETTER, _ANSWER_LETTER):
        if (m := pat.search(last)):
            return m.group(1).upper()
    for pat in (_ANY_FINAL_LETTER, _ANSWER_LETTER):
        if (m := pat.search(text)):
            return m.group(1).upper()
    if last and (m := _TRAILING_LETTER.search(last)):
        return m.group(1).upper()
    return None


def grade_mcq(unit, out_dir: Path, response: str) -> Result:
    answer = str(unit.answer).strip().upper()
    if len(answer) != 1 or not answer.isalpha():
        return False, f"bad gold answer {unit.answer!r}"
    got = _extract_letter(response)
    if got is None:
        return False, f"no option letter found (last line: {_clip(_final_line(response))})"
    if got == answer:
        return True, f"option {got}"
    return False, f"got {got}, expected {answer}"


# --------------------------------------------------------------------------- #
# exact
# --------------------------------------------------------------------------- #

_ARTICLES = re.compile(r"^(?:a|an|the)\s+", re.I)
_TRAILING_JUNK = re.compile(r"[\s.,;:!?'\"`*_)\]}]+$")
_LEADING_JUNK = re.compile(r"^[\s(`*_\[({\"']+")


def _norm_exact(s: str) -> str:
    s = str(s).strip()
    s = s.replace("```", "").replace("`", "")
    s = re.sub(r"\*\*?", "", s)
    s = _LEADING_JUNK.sub("", s)
    s = _TRAILING_JUNK.sub("", s)
    # symmetry: unwrap one layer of quotes/brackets from both ends
    for a, b in (('"', '"'), ("'", "'"), ("(", ")"), ("[", "]"), ("{", "}")):
        if len(s) > 1 and s.startswith(a) and s.endswith(b):
            s = s[1:-1].strip()
    s = _ARTICLES.sub("", s)
    s = " ".join(s.split()).lower()
    return _TRAILING_JUNK.sub("", s).strip()


def grade_exact(unit, out_dir: Path, response: str) -> Result:
    cand = _final_line(response)
    if cand is None:
        return False, "empty response"
    if cand.upper().startswith("FINAL:"):
        cand = cand.split(":", 1)[1].strip()
    gold = _norm_exact(unit.answer)
    got = _norm_exact(cand)
    if got == gold:
        return True, _clip(got)
    return False, f"got {_clip(got)!r}, expected {_clip(gold)!r}"


# --------------------------------------------------------------------------- #
# math
# --------------------------------------------------------------------------- #

_FRAC = re.compile(r"\\[dt]?frac\{(-?\d+(?:\.\d+)?)\}\{(-?\d+(?:\.\d+)?)\}")
_NUM = re.compile(r"^-?\d+(?:\.\d+)?(?:[eE][-+]?\d+)?$")


_WRAPPERS = ("text", "mathrm", "operatorname", "mbox", "textrm", "textbf")


def _unwrap_text(s: str) -> str:
    """Flatten ``\\text{...}``/``\\mathrm{...}`` wrappers (they nest, rarely)."""
    t = str(s)
    for _ in range(4):
        new = re.sub(r"\\(?:%s)\{([^{}]*)\}" % "|".join(_WRAPPERS), r"\1", t)
        if new == t:
            break
        t = new
    return t


_MD_EDGE_LEAD = re.compile(r"^[\s*_`]+")
_MD_EDGE_TRAIL = re.compile(r"[\s*_`.]+$")


def _strip_md_ends(s: str) -> str:
    """Drop markdown emphasis wrapped around an answer: ``**6**`` → ``6``.

    Only the *ends* are touched — ``2*3`` keeps its multiplication sign, and
    ``x_1`` keeps its subscript. Without this, ``FINAL: **6**`` parses as
    nothing and a correct model is marked wrong.
    """
    s = _MD_EDGE_LEAD.sub("", str(s).strip())
    return _MD_EDGE_TRAIL.sub("", s)


def _strip_currency(s: str) -> str:
    """Drop markdown wrapping and currency markers, escaped (``\\$``) or not.

    MATH-500 stores money answers as ``\\$18.90``. A naive ``$``-stripping
    pass leaves ``\\18.90``, which parses as nothing — so the gold answer
    falls through to string comparison and the model, who answered the
    plainly correct ``18.90``, is marked wrong.
    """
    return _unwrap_text(_strip_md_ends(s)).replace("\\$", "").replace("$", "")


_MATRIX_ENV = re.compile(r"\\begin\{([A-Za-z*]+)\}(.*?)\\end\{\1\}", re.S)
_ROWSEP = re.compile(r"\\\\")
_BINOM = re.compile(r"\\binom\{([^{}]*)\}\{([^{}]*)\}")


def _canon_matrix(s: str, flat: bool = False) -> str:
    """Rewrite a LaTeX vector/matrix as a flat tuple.

    MATH-500's gold answers use ``\\begin{pmatrix} -7 \\\\ 16 \\\\ 5
    \\end{pmatrix}`` for a column vector, while a model asked for "one line"
    will very reasonably answer ``(-7, 16, 5)``. Those are the same object.

    Orientation is deliberately *not* preserved: a tuple carries no
    orientation, so insisting on one would reject every correct tuple
    answer. Element order always is, so ``(1,2)`` still fails against
    ``(2,1)``.

    ``flat`` additionally renders a 2-D matrix row-major as ``(a,b,c,d)``
    rather than ``((a,b),(c,d))``, because a model may legitimately write
    either; ``_forms`` accepts whichever the other side used. Element count
    still separates a 4-element matrix from a 2-element one.
    """

    def repl(m: re.Match) -> str:
        env, body = m.group(1), m.group(2)
        if not env.rstrip("*").endswith("matrix"):
            return m.group(0)
        rows = [[c.strip() for c in r.split("&")]
                for r in _ROWSEP.split(body)]
        rows = [r for r in rows if any(c for c in r)]
        if not rows:
            return m.group(0)
        if flat or len(rows) == 1 or all(len(r) == 1 for r in rows):
            return "(" + ",".join(c for r in rows for c in r) + ")"
        return "(" + ",".join("(" + ",".join(r) + ")" for r in rows) + ")"

    t = _MATRIX_ENV.sub(repl, str(s))
    return _BINOM.sub(lambda m: f"({m.group(1)},{m.group(2)})", t)


def _to_number(s: str) -> Optional[float]:
    """Parse a scalar answer: plain int/float, comma'd, a/b, \\frac{a}{b}, n\\pi."""
    t = _strip_currency(s)
    t = (t.replace(",", "").replace(" ", "")
          .replace("\\left", "").replace("\\right", ""))
    t = t.rstrip(".").lstrip("=")
    if not t:
        return None
    m = _FRAC.fullmatch(t)
    if m:
        d = float(m.group(2))
        return float(m.group(1)) / d if d else None
    if re.fullmatch(r"-?\d+/-?\d+", t):
        num, den = t.split("/")
        d = float(den)
        return float(num) / d if d else None
    for suffix, scale in (("\\pi", math.pi), ("pi", math.pi), ("\\%", 0.01)):
        if t.endswith(suffix):
            head = t[: -len(suffix)]
            if head in ("", "+"):
                head = "1"
            if head == "-":
                head = "-1"
            if _NUM.match(head):
                return float(head) * scale
            return None
    if _NUM.match(t):
        return float(t)
    return None


_LHS_VAR = re.compile(r"^[A-Za-z](?:_\{?[A-Za-z0-9]+\}?)?$")
"""``x``, ``y``, ``n``, ``a_1`` — the only left-hand sides we may discard."""


def _norm_symbolic(s: str, flat_matrix: bool = False) -> str:
    t = _strip_currency(s)
    t = t.replace(" ", "").replace("\\!", "").replace("\\,", "")
    t = t.replace("\\left", "").replace("\\right", "")
    t = _canon_matrix(t, flat=flat_matrix)
    t = re.sub(r"^-?0\.?0*$", "0", t)
    if "=" in t:
        # Only drop a plain ``var =`` prefix, so a model replying ``x = 5``
        # still matches a gold of ``5``. A gold stored as a full equation
        # (``5x - 7y + 11z + 4 = 0``) must keep all of it — otherwise
        # answering the bare ``0`` would be accepted as correct.
        lhs, rhs = t.split("=", 1)
        if _LHS_VAR.match(lhs):
            t = rhs
    return t.lower().strip()


def _forms(s: str) -> set[str]:
    """Every spelling of ``s`` the grader considers equivalent."""
    return {_norm_symbolic(s), _norm_symbolic(s, flat_matrix=True)}


def _boxed(response: str) -> Optional[str]:
    """Content of the last balanced ``\\boxed{...}`` in ``response``.

    A regex like ``\\boxed\\{([^{}]*)\\}`` cannot see inside
    ``\\boxed{\\frac{1}{2}}`` (inner braces), so the most conventional way to
    state a math answer was invisible to the grader. This walks braces. A
    nested box resolves to the innermost one — ``\\boxed{a \\boxed{b}}`` means
    ``b`` — and an unterminated box falls back to the previous occurrence.
    """
    boundary = len(response)
    while True:
        idx = response.rfind(r"\boxed{", 0, boundary)
        if idx < 0:
            return None
        i, depth, start = idx + len(r"\boxed{"), 1, idx + len(r"\boxed{")
        while i < len(response):
            if response[i] == "{":
                depth += 1
            elif response[i] == "}":
                depth -= 1
                if depth == 0:
                    inner = response[start:i]
                    if r"\boxed{" in inner:
                        return _boxed(inner)
                    return inner
            i += 1
        boundary = idx  # unterminated — look at the earlier \boxed


def _integral(x: float) -> bool:
    return math.isfinite(x) and x == math.trunc(x)


def grade_math(unit, out_dir: Path, response: str) -> Result:
    cand = _final_line(response)
    if cand is None:
        return False, "empty response"
    cand = _strip_md_ends(cand)
    if cand.upper().startswith("FINAL:"):
        cand = cand.split(":", 1)[1].strip()
    else:
        # fall back to the usual \boxed{...} convention
        boxed = _boxed(response)
        if boxed is not None:
            cand = boxed
    if r"\boxed{" in cand:          # FINAL: \boxed{6} — a box on the final line
        inner = _boxed(cand)
        if inner is not None:
            cand = inner
    cand = _strip_md_ends(cand)
    if not cand:
        return False, "empty answer"

    gold_n, got_n = _to_number(unit.answer), _to_number(cand)
    if gold_n is not None and got_n is not None:
        # A whole number is exact: with rel_tol=1e-6 alone, 999999 passes
        # for 1000000 (diff 1 ≤ 1e-6 · 1e6), so an integral gold — every
        # MATH-500 integer answer — compares with plain equality.
        if _integral(gold_n):
            same = gold_n == got_n
        else:
            same = math.isclose(gold_n, got_n, rel_tol=1e-6, abs_tol=1e-9)
        if same:
            return True, _clip(got_n)
        return False, f"got {_clip(cand)}, expected {_clip(unit.answer)}"

    g_forms, o_forms = _forms(unit.answer), _forms(cand)
    both = g_forms & o_forms
    if both and "" not in both:
        return True, _clip(sorted(both, key=len)[0])
    return False, f"got {_clip(cand)}, expected {_clip(unit.answer)}"


# --------------------------------------------------------------------------- #
# code
# --------------------------------------------------------------------------- #

_FENCE = re.compile(r"```(?:python|py)?\s*\n(.*?)```", re.S)
_SYNTAX_OK = "SYNTAX_OK"


def _extract_code(response: str) -> str:
    """Pull the program out of the reply.

    Leading indentation is deliberately preserved — a HumanEval reply is often
    just an indented function *body*, which only parses when concatenated with
    the benchmark's prompt.
    """
    blocks = _FENCE.findall(response or "")
    if blocks:
        return blocks[-1].strip("\n") + "\n"
    return (response or "").rstrip() + "\n"


def _sandbox_python_argv(scratch: Path) -> list[str]:
    """Run model code without network and with no view of the host filesystem.

    ``scratch`` is created under $TMPDIR, which the sandbox shadows with a
    tmpfs — so it has to be bound back in *after* that mount, exactly like the
    main harness re-binds the work dir.

    The interpreter itself usually lives under ``/usr`` (already bound), but a
    virtualenv or pyenv install puts ``sys.prefix`` somewhere else. Without it
    the sandbox cannot exec the interpreter *at all*, and the failure surfaces
    as a plain grading miss — HumanEval+ and MBPP+ would silently score zero
    while everything else looked healthy. So any prefix outside the trees we
    already mount gets bound here, in the same post-tmpfs position.
    """
    bwrap = shutil.which("bwrap")
    if not bwrap:
        return [sys.executable]
    argv = [bwrap, "--ro-bind", "/usr", "/usr",
            "--ro-bind", "/etc", "/etc",
            "--unshare-net",
            "--dev", "/dev", "--proc", "/proc",
            "--tmpfs", "/tmp", "--tmpfs", "/home", "--tmpfs", "/var",
            "--symlink", "usr/lib64", "/lib64",
            "--bind", str(scratch), str(scratch)]
    for p in dict.fromkeys(x for x in (sys.prefix, sys.base_prefix) if x):
        if not p.startswith("/usr") and Path(p).is_dir():
            argv += ["--ro-bind", p, p]
    argv += ["--die-with-parent", "--new-session",
             "--setenv", "PATH", "/usr/local/bin:/usr/bin:/bin",
             "--setenv", "HOME", str(scratch),
             "--", sys.executable]
    return argv


def _run_program(source: str, timeout: int) -> Result:
    """Return (passed, detail) for one candidate program."""
    with tempfile.TemporaryDirectory(prefix="lb-code-") as td:
        scratch = Path(td)
        script = scratch / "candidate.py"
        script.write_text(source, encoding="utf-8")
        argv = _sandbox_python_argv(scratch)
        try:
            proc = subprocess.run(
                argv + [str(script)], capture_output=True, text=True,
                timeout=timeout, cwd=scratch)
        except subprocess.TimeoutExpired:
            return False, f"timed out after {timeout}s"
        except OSError as e:
            return False, f"could not execute: {e}"
        if proc.returncode == 0:
            return True, "all tests passed"
        return False, _clip(proc.stderr.strip() or f"rc={proc.returncode}")


def _strip_code_suffix(prompt: str) -> str:
    """Remove the instruction suffix fetch.py appended to the prompt.

    ``unit.prompt`` is what the *model* saw: ``prompt + SUFFIX_CODE``. The
    suffix ("Reply with a single fenced Python code block …") is prose, not
    part of the program — composing it into HumanEval's syntactic prefix made
    every composition a SyntaxError, so a reply containing only the indented
    function body (the common case) scored zero for a harness bug.
    """
    from .fetch import SUFFIX_CODE
    s = str(prompt)
    at = s.find(SUFFIX_CODE)
    if at < 0:
        at = s.find(SUFFIX_CODE.strip())   # tolerate whitespace drift
    return s[:at] if at >= 0 else s


def grade_code(unit, out_dir: Path, response: str) -> Result:
    meta = unit.meta or {}
    test = meta.get("test")
    if not test:
        return False, "bench item has no 'test' program"
    code = _extract_code(response)
    style = meta.get("code_style", "mbpp")
    timeout = int(meta.get("test_timeout", 60))

    # HumanEval: the benchmark prompt is itself a syntactic prefix of the
    # solution, so a bare body still composes. Try the canonical composition
    # only after the self-contained program, and vice versa.
    candidates = [code]
    if style == "humaneval":
        prompt = _strip_code_suffix(unit.prompt)
        candidates.append(prompt.rstrip("\n") + "\n" + code)

    best: Optional[Result] = None
    errs: list[str] = []
    for src in candidates:
        try:
            compile(src, "<candidate>", "exec")
        except SyntaxError as e:
            errs.append(f"syntax error: {e.msg} (line {e.lineno})")
            continue
        ok, detail = _run_program(src + "\n\n" + test, timeout)
        if ok:
            return True, "all tests passed"
        # a candidate that *ran* and failed outranks any syntax note: the
        # real failure detail must not be clobbered by the other candidate
        best = False, detail
    if best is not None:
        return best
    if errs:
        return False, f"model output is not valid Python — {errs[0]}"
    return False, "no candidate ran"


# --------------------------------------------------------------------------- #
# ifeval
# --------------------------------------------------------------------------- #

def grade_ifeval(unit, out_dir: Path, response: str) -> Result:
    try:
        from .vendor.ifeval import INSTRUCTION_DICT
    except ImportError as e:
        return False, ("IFEval checkers unavailable — install their deps with "
                       f"`pip install -e .` ({e})")

    meta = unit.meta or {}
    ids = meta.get("instruction_id_list") or []
    kwargs = meta.get("kwargs") or []
    if not ids:
        return False, "bench item has no instruction_id_list"
    if not (response or "").strip():
        return False, "empty response"

    failed: list[str] = []
    try:
        for idx, iid in enumerate(ids):
            ins = INSTRUCTION_DICT[iid](iid)
            ins.build_description(**kwargs[idx])
            args = ins.get_instruction_args()
            if args and "prompt" in args:
                ins.build_description(prompt=unit.prompt)
            if not ins.check_following(response):
                failed.append(iid)
    except KeyError:
        return False, f"unknown instruction id {iid!r}"
    except Exception as e:  # a broken checker must not sink the whole run
        return False, f"checker error: {type(e).__name__}: {e}"

    if failed:
        return False, f"{len(failed)}/{len(ids)} instructions violated: " + _clip(", ".join(failed))
    return True, f"all {len(ids)} instructions satisfied"


GRADERS: dict[str, Callable[..., Result]] = {
    "verify": grade_verify,
    "mcq": grade_mcq,
    "exact": grade_exact,
    "math": grade_math,
    "code": grade_code,
    "ifeval": grade_ifeval,
}


def grade(unit, out_dir: Path, response: Optional[str] = None) -> Result:
    fn = GRADERS.get(unit.grader)
    if fn is None:
        return False, f"unknown grader {unit.grader!r}"
    if response is None:
        path = out_dir / "response.txt"
        response = path.read_text(encoding="utf-8", errors="replace") if path.is_file() else ""
    try:
        return fn(unit, out_dir, response)
    except Exception as e:  # never let a grader crash the run
        return False, f"grader error: {type(e).__name__}: {e}"
