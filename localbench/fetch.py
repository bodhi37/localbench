"""Download published benchmarks and normalise them into ``benchmarks/known/``.

Each benchmark becomes::

    benchmarks/known/<id>/bench.json      committed: manifest, licence, grader
    benchmarks/known/<id>/data/items.jsonl  gitignored: the dataset itself

Datasets are *fetched*, not vendored — most have their own licence and the raw
text would dominate the repository. ``bench.json` records the upstream URL and
the licence pulled from the dataset card so the provenance travels with the repo.

All prompts get the same answer-format instruction appended at ingest (except
IFEval, where any extra text would violate the very constraints being tested),
so the prompt stored in ``items.jsonl`` is byte-for-byte what the model sees.
"""
from __future__ import annotations

import json
import random
import re
import shutil
import sys
import tarfile
import urllib.request
from pathlib import Path
from typing import Callable, Optional

from .config import KNOWN_ROOT

SUFFIX_MCQ = ("\n\nSelect the single best option.\n"
              "End your response with one line of exactly this form:\n"
              "FINAL: <letter>\n")
SUFFIX_EXACT = ("\n\nEnd your response with one line of exactly this form:\n"
                "FINAL: <answer>\n")
SUFFIX_MATH = ("\n\nEnd your response with one line of exactly this form:\n"
               "FINAL: <answer>\n"
               "where <answer> is the exact numeric or symbolic answer, with no "
               "units, no derivation and no commentary.\n")
SUFFIX_CODE = ("\n\nReply with a single fenced Python code block containing your "
               "complete solution, and nothing after it.\n")
SUFFIX_IFEVAL = ""


# --------------------------------------------------------------------------- #
# small builders
# --------------------------------------------------------------------------- #

_ALPHA = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"


def _mcq_prompt(question: str, options: list[str]) -> str:
    body = [question.strip(), ""]
    for i, opt in enumerate(options):
        body.append(f"{_ALPHA[i]}) {str(opt).strip()}")
    return "\n".join(body).rstrip() + "\n"


def _alpha(idx: int) -> str:
    return _ALPHA[idx]


def _hf_download(repo: str, filename: str, subfolder: Optional[str] = None) -> Path:
    from huggingface_hub import hf_hub_download
    return Path(hf_hub_download(repo, filename, repo_type="dataset",
                                subfolder=subfolder))


def _read_parquet(path: Path) -> list[dict]:
    import pandas as pd
    df = pd.read_parquet(path)
    df = df.where(df.notna(), None)
    return json.loads(df.to_json(orient="records"))


def _hf_license(repo: str, fallback: str) -> str:
    try:
        from huggingface_hub import HfApi
        cd = HfApi().dataset_info(repo).card_data
        if isinstance(cd, dict) and cd.get("license"):
            return str(cd["license"])
    except Exception:
        pass
    return fallback


def _resolve_license(spec: Spec) -> str:
    """Licence from the HF dataset card when we can read it, else our hint."""
    src = spec["source"]
    if src.startswith("https://huggingface.co/datasets/"):
        repo = src.split("/datasets/", 1)[1]
        return _hf_license(repo, spec.get("license_hint", "unknown"))
    return spec.get("license_hint", "unknown")


def _row(idx: int, prompt: str, answer, meta: Optional[dict] = None,
         grader: Optional[str] = None) -> dict:
    d = {"id": f"{idx:05d}", "prompt": prompt, "answer": answer,
         "meta": meta or {}}
    if grader:
        d["grader"] = grader
    return d


# --------------------------------------------------------------------------- #
# per-benchmark builders  ->  list[row]
# --------------------------------------------------------------------------- #

def build_gpqa_diamond(**kw) -> list[dict]:
    import csv
    path = _hf_download("idavidrein/gpqa", "gpqa_diamond.csv")
    raw = []
    with path.open(encoding="utf-8", errors="replace") as fh:
        for r in csv.DictReader(fh):
            raw.append((r["Question"],
                        [r["Correct Answer"], r["Incorrect Answer 1"],
                         r["Incorrect Answer 2"], r["Incorrect Answer 3"]]))
    rng = random.Random(0)
    out = []
    for i, (q, opts) in enumerate(raw):
        order = list(range(4))
        rng.shuffle(order)
        shuffled = [opts[k] for k in order]
        letter = _alpha(order.index(0))          # 0 == Correct Answer
        out.append(_row(i, _mcq_prompt(q, shuffled) + SUFFIX_MCQ, letter,
                        {"options": shuffled}))
    return out


def build_mmlu_pro(**kw) -> list[dict]:
    path = _hf_download("TIGER-Lab/MMLU-Pro", "data/test-00000-of-00001.parquet")
    out = []
    for i, r in enumerate(_read_parquet(path)):
        opts = list(r.get("options") or [])
        # `answer` is the letter; `answer_index` is the same thing as an index.
        letter = str(r.get("answer") or "").strip().upper()
        if len(letter) != 1 or letter not in _ALPHA:
            idx = r.get("answer_index")
            if idx is None:
                continue
            letter = _alpha(int(idx))
        if opts and _alpha(len(opts) - 1) < letter:
            continue  # letter points past the end of the option list
        out.append(_row(i, _mcq_prompt(r["question"], opts) + SUFFIX_MCQ,
                        letter, {"category": r.get("category")}))
    return out


def build_mmlu(**kw) -> list[dict]:
    from huggingface_hub import list_repo_files
    files = [f for f in list_repo_files("cais/mmlu", repo_type="dataset")
             if "/test-" in f and f.startswith("all/")]
    if not files:
        raise RuntimeError("cais/mmlu has no all/test split")
    path = _hf_download("cais/mmlu", sorted(files)[0])
    out = []
    for i, r in enumerate(_read_parquet(path)):
        opts = r.get("choices") or []
        out.append(_row(i, _mcq_prompt(r["question"], opts) + SUFFIX_MCQ,
                        _alpha(int(r["answer"])), {"subject": r.get("subject")}))
    return out


def build_arc_challenge(**kw) -> list[dict]:
    path = _hf_download("allenai/ai2_arc", "ARC-Challenge/test-00000-of-00001.parquet")
    out = []
    for i, r in enumerate(_read_parquet(path)):
        ch = r.get("choices") or {}
        labels = [str(x) for x in (ch.get("label") or [])]
        texts = [str(x) for x in (ch.get("text") or [])]
        key = str(r.get("answerKey") or "")
        if key in labels:
            idx = labels.index(key)
        elif key.isdigit():
            idx = int(key) - 1
        else:
            idx = -1
        if idx < 0 or idx >= len(texts):
            continue
        out.append(_row(i, _mcq_prompt(r["question"], texts) + SUFFIX_MCQ,
                        _alpha(idx)))
    return out


def build_hellaswag(**kw) -> list[dict]:
    path = _hf_download("Rowan/hellaswag", "data/validation-00000-of-00001.parquet")
    out = []
    for i, r in enumerate(_read_parquet(path)):
        ctx = str(r.get("ctx") or "")
        endings = [str(e) for e in (r.get("endings") or [])]
        if not endings or r.get("label") is None:
            continue
        idx = int(r["label"])
        prompt = ctx.rstrip() + "\n\nContinuation:\n"
        for j, e in enumerate(endings):
            prompt += f"{_alpha(j)}) {e}\n"
        out.append(_row(i, prompt.rstrip() + "\n" + SUFFIX_MCQ, _alpha(idx)))
    return out


def build_truthfulqa_mc1(**kw) -> list[dict]:
    """MC1: exactly one of the offered claims is true; labels mark it."""
    path = _hf_download("truthfulqa/truthful_qa",
                        "multiple_choice/validation-00000-of-00001.parquet")
    out = []
    for i, r in enumerate(_read_parquet(path)):
        tgt = r.get("mc1_targets") or {}
        choices = [str(c) for c in (tgt.get("choices") or [])]
        labels = [int(float(x)) for x in (tgt.get("labels") or [])]
        if not choices or 1 not in labels:
            continue
        idx = labels.index(1)
        out.append(_row(i, _mcq_prompt(str(r.get("question") or ""), choices)
                        + SUFFIX_MCQ, _alpha(idx)))
    return out


def build_winogrande(**kw) -> list[dict]:
    path = _hf_download("allenai/winogrande",
                        "winogrande_xl/validation-00000-of-00001.parquet")
    out = []
    for i, r in enumerate(_read_parquet(path)):
        sent = str(r.get("sentence") or "")
        o1, o2 = str(r.get("option1") or ""), str(r.get("option2") or "")
        ans = str(r.get("answer") or "")
        if ans not in ("1", "2"):
            continue
        prompt = (sent.replace("_", "____")
                  + "\n\nFill the blank with option A or B:\n"
                  f"A) {o1}\nB) {o2}\n")
        out.append(_row(i, prompt + SUFFIX_MCQ, _alpha(int(ans) - 1)))
    return out


def build_math_500(**kw) -> list[dict]:
    path = _hf_download("HuggingFaceH4/MATH-500", "test.jsonl")
    out = []
    for i, line in enumerate(path.read_text(encoding="utf-8").splitlines()):
        if not line.strip():
            continue
        r = json.loads(line)
        out.append(_row(i, str(r["problem"]).rstrip() + "\n" + SUFFIX_MATH,
                        str(r["answer"]),
                        {"subject": r.get("subject"), "level": r.get("level")}))
    return out


def _gsm8k_answer(raw: str) -> str:
    m = re.findall(r"####\s*(.+)", raw)
    return (m[-1] if m else raw).strip()


def build_gsm8k(**kw) -> list[dict]:
    path = _hf_download("openai/gsm8k", "main/test-00000-of-00001.parquet")
    out = []
    for i, r in enumerate(_read_parquet(path)):
        out.append(_row(i, str(r["question"]).rstrip() + "\n" + SUFFIX_MATH,
                        _gsm8k_answer(str(r.get("answer") or ""))))
    return out


def build_aime_2024(**kw) -> list[dict]:
    path = _hf_download("HuggingFaceH4/aime_2024", "data/train-00000-of-00001.parquet")
    out = []
    for i, r in enumerate(_read_parquet(path)):
        out.append(_row(i, str(r["problem"]).rstrip() + "\n" + SUFFIX_MATH,
                        str(r["answer"]).strip()))
    return out


def build_humaneval_plus(**kw) -> list[dict]:
    path = _hf_download("EvalPlus/HumanEvalPlus", "test.jsonl")
    out = []
    for i, line in enumerate(path.read_text(encoding="utf-8").splitlines()):
        if not line.strip():
            continue
        r = json.loads(line)
        prompt = str(r["prompt"]) + SUFFIX_CODE
        out.append(_row(i, prompt, None, {
            "test": r.get("test"),
            "entry_point": r.get("entry_point"),
            "code_style": "humaneval",
            "upstream_task_id": r.get("task_id"),
        }))
    return out


def build_mbpp_plus(**kw) -> list[dict]:
    path = _hf_download("EvalPlus/mbppplus",
                        "data/test-00000-of-00001-d5781c9c51e02795.parquet")
    out = []
    for i, r in enumerate(_read_parquet(path)):
        prompt = str(r["prompt"]).rstrip()
        if r.get("test_imports"):
            imports = "\n".join(str(x) for x in r["test_imports"])
            prompt = f"# You may use these imports:\n{imports}\n\n{prompt}"
        out.append(_row(i, prompt + "\n" + SUFFIX_CODE, None, {
            "test": r.get("test"),
            "code_style": "mbpp",
            "upstream_task_id": r.get("task_id"),
        }))
    return out


def build_ifeval(**kw) -> list[dict]:
    path = _hf_download("google/ifeval", "ifeval_input_data.jsonl")
    out = []
    for i, line in enumerate(path.read_text(encoding="utf-8").splitlines()):
        if not line.strip():
            continue
        r = json.loads(line)
        # no suffix: the prompt already carries every constraint under test
        out.append(_row(i, str(r["prompt"]).rstrip() + "\n", None, {
            "instruction_id_list": r.get("instruction_id_list") or [],
            "kwargs": r.get("kwargs") or [],
            "upstream_key": r.get("key"),
        }))
    return out


BBH_TARBALL = ("https://github.com/suzgunmirac/BIG-Bench-Hard/"
               "archive/refs/heads/main.tar.gz")


def build_bbh(**kw) -> list[dict]:
    """27 subtasks. Letter targets grade as mcq, everything else as exact."""
    import io
    data = urllib.request.urlopen(BBH_TARBALL, timeout=120).read()
    tar = tarfile.open(fileobj=io.BytesIO(data), mode="r:gz")
    members = sorted((m for m in tar.getmembers()
                      if "/bbh/" in m.name and m.name.endswith(".json")),
                     key=lambda m: m.name)
    out, idx = [], 0
    letter_re = re.compile(r"^[\"'(\[]*([A-E])[\"')\]]*$", re.I)
    for m in members:
        sub = Path(m.name).stem
        spec = json.loads(tar.extractfile(m).read().decode())
        for ex in spec.get("examples", []):
            target = str(ex.get("target", "")).strip()
            m_letter = letter_re.match(target)
            grader = "mcq" if m_letter else "exact"
            answer = m_letter.group(1).upper() if m_letter else target
            prompt = (str(ex.get("input", "")).rstrip()
                      + "\n\nAnswer the question above.\n" + SUFFIX_EXACT)
            out.append(_row(idx, prompt, answer, {"subtask": sub}, grader))
            idx += 1
    return out


# --------------------------------------------------------------------------- #
# registry of what can be fetched
# --------------------------------------------------------------------------- #

class Spec(dict):
    pass


SPECS: dict[str, Spec] = {
    "gpqa-diamond": Spec(
        id="gpqa-diamond", name="GPQA Diamond", grader="mcq",
        source="https://huggingface.co/datasets/idavidrein/gpqa",
        license_hint="cc-by-4.0", build=build_gpqa_diamond,
        gated=True, timeout=900,
        about="198 PhD-level science questions (diamond split). Gated: accept "
              "the terms on the dataset page and export HF_TOKEN."),
    "mmlu-pro": Spec(
        id="mmlu-pro", name="MMLU-Pro", grader="mcq",
        source="https://huggingface.co/datasets/TIGER-Lab/MMLU-Pro",
        license_hint="mit", build=build_mmlu_pro, timeout=900,
        about="12k hard ten-option questions across 14 disciplines."),
    "mmlu": Spec(
        id="mmlu", name="MMLU", grader="mcq",
        source="https://huggingface.co/datasets/cais/mmlu",
        license_hint="mit", build=build_mmlu, timeout=600,
        about="14k four-option questions across 57 subjects (test split)."),
    "arc-challenge": Spec(
        id="arc-challenge", name="ARC-Challenge", grader="mcq",
        source="https://huggingface.co/datasets/allenai/ai2_arc",
        license_hint="cc-by-4.0", build=build_arc_challenge, timeout=600,
        about="1172 grade-school science questions that stump retrieval."),
    "hellaswag": Spec(
        id="hellaswag", name="HellaSwag", grader="mcq",
        source="https://huggingface.co/datasets/Rowan/hellaswag",
        license_hint="cc-by-4.0", build=build_hellaswag, timeout=600,
        about="10k sentence-completion commonsense reasoning items (validation)."),
    "truthfulqa-mc1": Spec(
        id="truthfulqa-mc1", name="TruthfulQA MC1", grader="mcq",
        source="https://huggingface.co/datasets/truthfulqa/truthful_qa",
        license_hint="cc-by-4.0", build=build_truthfulqa_mc1, timeout=600,
        about="817 questions probing whether a model repeats common misbeliefs."),
    "winogrande": Spec(
        id="winogrande", name="WinoGrande XL", grader="mcq",
        source="https://huggingface.co/datasets/allenai/winogrande",
        license_hint="cc-by-4.0", build=build_winogrande, timeout=600,
        about="Winograd-style pronoun resolution, anti-bias set (validation)."),
    "math-500": Spec(
        id="math-500", name="MATH-500", grader="math",
        source="https://huggingface.co/datasets/HuggingFaceH4/MATH-500",
        license_hint="mit", build=build_math_500, timeout=1200,
        about="500 competition-math problems spanning all seven subjects."),
    "gsm8k": Spec(
        id="gsm8k", name="GSM8K (test)", grader="math",
        source="https://huggingface.co/datasets/openai/gsm8k",
        license_hint="mit", build=build_gsm8k, timeout=600,
        about="1319 grade-school word problems (official test split)."),
    "aime-2024": Spec(
        id="aime-2024", name="AIME 2024", grader="math",
        source="https://huggingface.co/datasets/HuggingFaceH4/aime_2024",
        license_hint="cc-by-4.0", build=build_aime_2024, timeout=1800,
        about="30 olympiad problems — a small, brutally hard numeric set."),
    "humaneval-plus": Spec(
        id="humaneval-plus", name="HumanEval+", grader="code",
        source="https://huggingface.co/datasets/EvalPlus/HumanEvalPlus",
        license_hint="apache-2.0", build=build_humaneval_plus, timeout=600,
        about="164 problems graded by EvalPlus's ~80x expanded test suites."),
    "mbpp-plus": Spec(
        id="mbpp-plus", name="MBPP+", grader="code",
        source="https://huggingface.co/datasets/EvalPlus/mbppplus",
        license_hint="apache-2.0", build=build_mbpp_plus, timeout=600,
        about="378 beginner-level problems graded by expanded test suites."),
    "ifeval": Spec(
        id="ifeval", name="IFEval", grader="ifeval",
        source="https://huggingface.co/datasets/google/ifeval",
        license_hint="cc-by-4.0", build=build_ifeval, timeout=900,
        about="541 verifiable instruction-following prompts (25 constraint "
              "types, official Google checkers)."),
    "bbh": Spec(
        id="bbh", name="BIG-Bench Hard", grader="exact",
        source="https://github.com/suzgunmirac/BIG-Bench-Hard",
        license_hint="mit", build=build_bbh, timeout=900,
        about="6511 items across 27 reasoning subtasks that defeat "
              "zero-shot models."),
}


# --------------------------------------------------------------------------- #

def _write_bench(spec: Spec, dest: Path, n_items: int, license_: str,
                 seed: int) -> None:
    bench = {
        "id": spec["id"],
        "name": spec["name"],
        "grader": spec["grader"],
        "source": spec["source"],
        "license": license_,
        "about": spec.get("about", ""),
        "gated": bool(spec.get("gated")),
        "timeout": int(spec.get("timeout", 600)),
        "answer_format": _suffix_note(spec["grader"]),
        "items": n_items,
        "ingest": {
            "builder": f"localbench.fetch.build_{spec['id'].replace('-', '_')}",
            "shuffle_seed": seed,
            "note": "data/items.jsonl is shuffled with shuffle_seed at ingest; "
                    "the file order is the run order, so prefixes are stable.",
        },
    }
    (dest / "bench.json").write_text(json.dumps(bench, indent=2) + "\n",
                                     encoding="utf-8")


def _suffix_note(grader: str) -> str:
    return {
        "mcq": "FINAL: <letter>",
        "exact": "FINAL: <answer>",
        "math": "FINAL: <answer>",
        "code": "one fenced Python code block",
        "ifeval": "prompt is used verbatim — no answer-format suffix",
    }.get(grader, "")


def fetch(benchmarks: Optional[list[str]] = None, force: bool = False,
          seed: int = 0) -> int:
    wanted = benchmarks or list(SPECS)
    unknown = [b for b in wanted if b not in SPECS]
    if unknown:
        print(f"unknown benchmark(s): {', '.join(unknown)}", file=sys.stderr)
        print(f"available: {', '.join(SPECS)}", file=sys.stderr)
        return 2

    try:
        import huggingface_hub  # noqa: F401
    except ImportError:
        print("fetching needs the 'fetch' extra: "
              "pip install -e '.[fetch]'", file=sys.stderr)
        return 2

    rc = 0
    for name in wanted:
        spec = SPECS[name]
        dest = KNOWN_ROOT / name
        items = dest / "data" / "items.jsonl"
        if items.is_file() and not force:
            print(f"  = {name:16} already fetched (use --force to redo)")
            continue
        print(f"  > {name:16} building ...", flush=True)
        try:
            rows = list(spec["build"]())
        except Exception as e:
            rc = 1
            print(f"    FAILED: {type(e).__name__}: {e}", file=sys.stderr)
            if spec.get("gated"):
                print("    (this dataset is gated — accept its terms at "
                      f"{spec['source']} and set HF_TOKEN)", file=sys.stderr)
            continue
        if not rows:
            rc = 1
            print("    FAILED: builder produced no rows", file=sys.stderr)
            continue

        random.Random(seed).shuffle(rows)
        (dest / "data").mkdir(parents=True, exist_ok=True)
        with items.open("w", encoding="utf-8") as fh:
            for r in rows:
                fh.write(json.dumps(r, ensure_ascii=False) + "\n")
        _write_bench(spec, dest, len(rows), _resolve_license(spec), seed)
        print(f"    ok {len(rows)} items -> {items.relative_to(KNOWN_ROOT.parent.parent)}")
    return rc
