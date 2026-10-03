from pathlib import Path

from localbench.graders import (
    grade_code, grade_ifeval, grade_exact, grade_math, grade_mcq, grade_verify,
)
from localbench.registry import Unit


def unit(**kw) -> Unit:
    base = dict(uid="x", suite="known", benchmark="b", kind="item",
                ref="0", prompt="prompt", timeout=60, grader="mcq",
                task_dir=None, answer=None, meta={})
    base.update(kw)
    return Unit(**base)


# --------------------------------------------------------------------------- #
# mcq
# --------------------------------------------------------------------------- #

def test_mcq_final_line():
    assert grade_mcq(unit(answer="B"), Path("."), "reasoning\nFINAL: B")[0]


def test_mcq_last_line_letter_only():
    assert grade_mcq(unit(answer="C"), Path("."), "I pick C")[0]


def test_mcq_answer_is_form():
    assert grade_mcq(unit(answer="A"), Path("."), "The answer is (A).")[0]


def test_mcq_wrong_letter_rejected():
    ok, detail = grade_mcq(unit(answer="B"), Path("."), "FINAL: D")
    assert not ok and "D" in detail and "B" in detail


def test_mcq_no_letter_rejected():
    ok, detail = grade_mcq(unit(answer="B"), Path("."), "I am not sure.")
    assert not ok


def test_mcq_tenth_option_m():
    assert grade_mcq(unit(answer="J"), Path("."), "FINAL: J")[0]


# --------------------------------------------------------------------------- #
# exact
# --------------------------------------------------------------------------- #

def test_exact_normalises_case_articles_punct():
    assert grade_exact(unit(answer="The Salmon"), Path("."), "FINAL: salmon.")[0]


def test_exact_unwraps_parens():
    assert grade_exact(unit(answer="(A)"), Path("."), "FINAL: A")[0]


def test_exact_whole_line_without_final():
    assert grade_exact(unit(answer="yes"), Path("."), "blah blah\nYes")[0]


def test_exact_wrong_rejected():
    ok, _ = grade_exact(unit(answer="42"), Path("."), "FINAL: 43")
    assert not ok


# --------------------------------------------------------------------------- #
# math
# --------------------------------------------------------------------------- #

def test_math_integer():
    assert grade_math(unit(answer="1234"), Path("."), "work...\nFINAL: 1234")[0]


def test_math_comma_separated():
    assert grade_math(unit(answer="1000000"), Path("."), "FINAL: 1,000,000")[0]


def test_math_negative_float_tolerance():
    assert grade_math(unit(answer="-0.5"), Path("."), "FINAL: -0.5000000001")[0]


def test_math_fraction_equivalence():
    assert grade_math(unit(answer="0.5"), Path("."), "FINAL: 1/2")[0]


def test_math_latex_frac():
    assert grade_math(unit(answer="3/4"), Path("."), r"FINAL: \frac{3}{4}")[0]


def test_math_boxed_fallback():
    assert grade_math(unit(answer="17"), Path("."), r"so it is $\boxed{17}$")[0]


def test_math_wrong_rejected():
    ok, _ = grade_math(unit(answer="17"), Path("."), "FINAL: 18")
    assert not ok


# --------------------------------------------------------------------------- #
# the two false negatives the first live run caught
# --------------------------------------------------------------------------- #

def test_math_latex_escaped_currency():
    """MATH-500 stores money as ``\\$18.90``; ``$``-stripping alone left
    ``\\18.90``, unparseable — so a correct ``18.90`` was graded wrong."""
    ok, detail = grade_math(unit(answer=r"\$18.90"), Path("."), "FINAL: 18.90")
    assert ok, detail


def test_math_currency_inside_text_wrapper():
    assert grade_math(unit(answer=r"\text{\$3.50}"), Path("."),
                      "FINAL: 3.50")[0]


def test_math_pmatrix_gold_vs_tuple_answer():
    """Gold is a column vector; the model answered the same numbers as a
    tuple. Element order matches, so this must pass."""
    gold = r"\begin{pmatrix} -7 \\ 16 \\ 5 \end{pmatrix}"
    ok, detail = grade_math(unit(answer=gold), Path("."), "FINAL: (-7, 16, 5)")
    assert ok, detail


def test_math_tuple_gold_vs_pmatrix_answer():
    """The same equivalence, other direction: the model echoes the LaTeX."""
    gold = "(-7, 16, 5)"
    got = r"\begin{pmatrix} -7 \\ 16 \\ 5 \end{pmatrix}"
    assert grade_math(unit(answer=gold), Path("."), f"FINAL: {got}")[0]


def test_math_pmatrix_row_vector_matches_its_own_order():
    gold = r"\begin{pmatrix} 16/49 & 48/49 \end{pmatrix}"
    assert grade_math(unit(answer=gold), Path("."),
                      "FINAL: (16/49, 48/49)")[0]


def test_math_matrix_element_order_still_matters():
    """Flattening orientation must not make every permutation correct."""
    gold = r"\begin{pmatrix} 1 \\ 2 \end{pmatrix}"
    ok, _ = grade_math(unit(answer=gold), Path("."), "FINAL: (2, 1)")
    assert not ok


def test_math_two_d_matrix_accepts_either_nesting():
    """A model may write ``((1,2),(3,4))`` or the row-major ``(1,2,3,4)``."""
    gold = r"\begin{pmatrix} 1 & 2 \\ 3 & 4 \end{pmatrix}"
    assert grade_math(unit(answer=gold), Path("."),
                      "FINAL: ((1,2),(3,4))")[0]
    assert grade_math(unit(answer=gold), Path("."),
                      "FINAL: (1, 2, 3, 4)")[0]


def test_math_two_d_matrix_wrong_element_count_rejected():
    gold = r"\begin{pmatrix} 1 & 2 \\ 3 & 4 \end{pmatrix}"
    ok, _ = grade_math(unit(answer=gold), Path("."), "FINAL: (1, 2)")
    assert not ok


def test_math_binom_matches_tuple():
    assert grade_math(unit(answer=r"\binom{5}{2}"), Path("."),
                      "FINAL: (5, 2)")[0]


def test_math_wrapped_wrong_answer_still_rejected():
    gold = r"\begin{pmatrix} -7 \\ 16 \\ 5 \end{pmatrix}"
    ok, _ = grade_math(unit(answer=gold), Path("."), "FINAL: (-7, 16, 6)")
    assert not ok


def test_math_variable_assignment_stripped_from_both_sides():
    """``x = 5`` and ``5`` are the same answer to "find x"."""
    assert grade_math(unit(answer="5"), Path("."), "FINAL: x = 5")[0]
    assert grade_math(unit(answer="x=5"), Path("."), "FINAL: 5")[0]


def test_math_full_equation_gold_is_not_satisfied_by_its_constant():
    """Gold ``5x - 7y + 11z + 4 = 0`` is an *equation*, not the number 0.

    Splitting on every ``=`` normalised it to ``0`` and would have accepted
    a bare ``0`` as a correct answer to a "find the equation" question.
    """
    gold = "5x - 7y + 11z + 4 = 0"
    ok, _ = grade_math(unit(answer=gold), Path("."), "FINAL: 0")
    assert not ok, "the bare constant must not satisfy an equation gold"
    assert grade_math(unit(answer=gold), Path("."),
                      "FINAL: 5x - 7y + 11z + 4 = 0")[0]
    ok, _ = grade_math(unit(answer=gold), Path("."), "FINAL: 0 = 0")
    assert not ok


def test_math_equation_gold_accepts_rearranged_form():
    gold = "y = 2x + 3"
    assert grade_math(unit(answer=gold), Path("."),
                      "FINAL: 2x + 3")[0]


# --------------------------------------------------------------------------- #
# code
# --------------------------------------------------------------------------- #

GOOD = "```python\ndef add(a, b):\n    return a + b\n```"
BAD = "```python\ndef add(a, b):\n    return a - b\n```"
TEST = "assert add(1, 2) == 3\nassert add(0, 0) == 0\n"


def test_code_pass(tmp_path):
    u = unit(grader="code", meta={"test": TEST, "code_style": "mbpp"})
    assert grade_code(u, tmp_path, GOOD)[0]


def test_code_fail(tmp_path):
    u = unit(grader="code", meta={"test": TEST, "code_style": "mbpp"})
    ok, detail = grade_code(u, tmp_path, BAD)
    assert not ok and "AssertionError" in detail


def test_code_humaneval_bare_body_composes(tmp_path):
    """HumanEval prompts are a syntactic prefix, so a body-only reply works."""
    u = unit(grader="code",
             prompt="def add(a, b):\n    \"\"\"Add.\"\"\"\n",
             meta={"test": TEST, "code_style": "humaneval"})
    assert grade_code(u, tmp_path, "    return a + b")[0]


def test_code_invalid_python_rejected(tmp_path):
    u = unit(grader="code", meta={"test": TEST, "code_style": "mbpp"})
    ok, detail = grade_code(u, tmp_path, "```python\nthis is not python@@\n```")
    assert not ok


# --------------------------------------------------------------------------- #
# ifeval
# --------------------------------------------------------------------------- #

IFEVAL_ITEM = dict(
    instruction_id_list=["punctuation:no_comma"],
    kwargs=[{}],
)


def test_ifeval_pass(tmp_path):
    u = unit(grader="ifeval", prompt="Write a sentence.",
             meta=dict(IFEVAL_ITEM))
    assert grade_ifeval(u, tmp_path, "This sentence has no comma at all.")[0]


def test_ifeval_fail_lists_violation(tmp_path):
    u = unit(grader="ifeval", prompt="Write a sentence.",
             meta=dict(IFEVAL_ITEM))
    ok, detail = grade_ifeval(u, tmp_path, "Yes, it does have a comma.")
    assert not ok and "no_comma" in detail


def test_ifeval_empty_response(tmp_path):
    u = unit(grader="ifeval", prompt="p", meta=dict(IFEVAL_ITEM))
    assert not grade_ifeval(u, tmp_path, "")[0]


# --------------------------------------------------------------------------- #
# verify (a real custom task, graded by its own verify.py)
# --------------------------------------------------------------------------- #

def test_verify_grades_a_real_custom_task(tmp_path):
    from localbench.registry import discover_custom
    spec = next(d for d in discover_custom() if d["ref"] == "math-arithmetic-001")
    u = Unit(uid="task/math-arithmetic-001", suite="custom", benchmark="math",
             kind="task", ref="math-arithmetic-001",
             prompt=(spec["task_dir"] / "prompt.md").read_text(),
             timeout=60, grader="verify", task_dir=spec["task_dir"],
             meta=spec["meta"])

    good = tmp_path / "response.txt"
    good.write_text("working...\nFINAL: batches=19 cost_cents=9215\n")
    assert grade_verify(u, tmp_path, good.read_text())[0]

    bad = tmp_path / "bad"
    bad.mkdir()
    (bad / "response.txt").write_text("FINAL: batches=18 cost_cents=9215\n")
    assert not grade_verify(u, bad, (bad / "response.txt").read_text())[0]
