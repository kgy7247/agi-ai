from __future__ import annotations

from dataclasses import dataclass


GAP_RULES = {
    "missing_test": {
        "critique_terms": ["test", "tests", "테스트"],
        "plan_terms": ["test", "tests", "unittest", "pytest", "테스트"],
        "revision": "Add a failing test that captures the criticized behavior before changing the implementation.",
    },
    "missing_artifact": {
        "critique_terms": ["artifact", "patch", "code", "아티팩트", "코드", "패치"],
        "plan_terms": ["artifact", "patch", "code", "file", "path", ".py", "tests/", "아티팩트", "코드", "패치"],
        "revision": "Name the concrete artifact path that will be changed or added.",
    },
    "missing_failure_criteria": {
        "critique_terms": ["failure", "criteria", "pass/fail", "fail", "실패", "기준"],
        "plan_terms": ["failure", "criteria", "pass/fail", "fail when", "실패", "기준"],
        "revision": "Define pass/fail criteria so reviewers can reject a weak result.",
    },
    "missing_verification": {
        "critique_terms": ["verify", "verification", "evidence", "reproduce", "검증", "근거", "재현"],
        "plan_terms": ["verify", "verification", "evidence", "reproduce", "검증", "근거", "재현"],
        "revision": "Record the command and evidence needed for independent verification.",
    },
}


@dataclass(frozen=True)
class SelfCorrectionResult:
    original_plan: list[str]
    critique: str
    revised_plan: list[str]
    detected_gaps: list[str]
    addressed_gaps: list[str]
    score: int
    passed: bool


def revise_plan_after_critique(plan_steps: list[str], critique: str) -> SelfCorrectionResult:
    clean_plan = [step.strip() for step in plan_steps if step.strip()]
    if not clean_plan:
        raise ValueError("plan_steps must contain at least one non-empty step")
    critique_text = critique.strip()
    if not critique_text:
        raise ValueError("critique is required")

    detected_gaps = detect_gaps(clean_plan, critique_text)
    revised_plan = list(clean_plan)
    for gap in detected_gaps:
        revision = GAP_RULES[gap]["revision"]
        if not contains_any(revised_plan, [revision]):
            revised_plan.append(revision)

    addressed_gaps = [gap for gap in detected_gaps if plan_addresses_gap(revised_plan, gap)]
    score = score_revision(detected_gaps, addressed_gaps)
    return SelfCorrectionResult(
        original_plan=clean_plan,
        critique=critique_text,
        revised_plan=revised_plan,
        detected_gaps=detected_gaps,
        addressed_gaps=addressed_gaps,
        score=score,
        passed=bool(detected_gaps) and score == 100,
    )


def detect_gaps(plan_steps: list[str], critique: str) -> list[str]:
    gaps = []
    for gap, rule in GAP_RULES.items():
        critique_mentions_gap = contains_any([critique], rule["critique_terms"])
        plan_already_covers_gap = plan_addresses_gap(plan_steps, gap)
        if critique_mentions_gap and not plan_already_covers_gap:
            gaps.append(gap)
    return gaps


def plan_addresses_gap(plan_steps: list[str], gap: str) -> bool:
    rule = GAP_RULES[gap]
    return contains_any(plan_steps, rule["plan_terms"])


def score_revision(detected_gaps: list[str], addressed_gaps: list[str]) -> int:
    if not detected_gaps:
        return 100
    return round(100 * len(set(addressed_gaps)) / len(set(detected_gaps)))


def contains_any(values: list[str], terms: list[str]) -> bool:
    haystack = "\n".join(values).lower()
    return any(term.lower() in haystack for term in terms)
