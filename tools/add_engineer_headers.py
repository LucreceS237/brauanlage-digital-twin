"""One-off script to add/update Responsible Engineer headers in Python files."""

from __future__ import annotations

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

ENGINEER = {
    "backend": "Engineer D",
    "ap2": "Engineer A",
    "ap3": "Engineer A, Engineer D (Engineer B left)",
    "ap4": "Engineer C",
    "ap5": "Engineer D",
    "ap6": "Engineer E",
    "shared": "Engineer A, Engineer D (Engineer B left)",
    "project_root": "Engineer D",
    "tests": "Engineer D",
}

PURPOSES = {
    ("project", "__init__.py"): "Root package marker for work packages AP2–AP6.",
    ("project", "shared", "__init__.py"): "Shared modules used by multiple work packages.",
    ("project", "shared", "simulation", "__init__.py"): "FSM-aligned process simulator shared by AP2 and AP3.",
    ("project", "shared", "simulation", "payload_builder.py"): "Build MQTT-compatible SPS payloads with a consistent envelope.",
    ("project", "shared", "simulation", "process_simulator.py"): "Time-driven brewing process simulator for demo and fake SPS mode.",
    ("project", "shared", "simulation", "scenarios.py"): "Selectable simulation fault scenarios for demo runs.",
}


def rel_parts(path: Path) -> tuple[str, ...]:
    return path.relative_to(ROOT).parts


def work_package(path: Path) -> str:
    parts = rel_parts(path)
    if not parts:
        return "project"
    if parts[0] == "backend":
        return "backend"
    if parts[0] == "tests":
        return "tests"
    if parts[0] == "project" and len(parts) >= 2:
        return parts[1]
    return "project"


def engineer_for(path: Path) -> str:
    parts = rel_parts(path)
    if not parts:
        return ENGINEER["project_root"]
    if parts[0] == "backend":
        return ENGINEER["backend"]
    if parts[0] == "tests":
        return ENGINEER["tests"]
    if parts[0] == "project":
        if len(parts) >= 2 and parts[1] == "shared":
            return ENGINEER["shared"]
        if len(parts) >= 2 and parts[1] in ENGINEER:
            return ENGINEER[parts[1]]
        return ENGINEER["project_root"]
    return ENGINEER["project_root"]


def work_package_label(path: Path) -> str:
    wp = work_package(path)
    if wp.startswith("ap"):
        return wp.upper()
    return wp


def default_purpose(path: Path) -> str:
    parts = rel_parts(path)
    key = parts
    if key in PURPOSES:
        return PURPOSES[key]
    name = path.stem
    wp = work_package(path)
    if name == "__init__":
        return f"Package marker for {wp}."
    if wp == "ap4":
        return f"AP4 FSM module: {name}."
    if wp == "ap2":
        return f"AP2 MQTT publisher module: {name}."
    if wp == "ap3":
        return f"AP3 backend module: {name}."
    if wp == "ap5":
        return f"AP5 integration/anomaly module: {name}."
    if wp == "tests":
        return f"Tests for {name.replace('test_', '')}."
    if wp == "backend":
        return f"Backend orchestration module: {name}."
    return f"Module: {name}."


def extract_purpose(text: str) -> str:
    m = re.match(r'"""(.*?)"""', text, re.DOTALL)
    if not m:
        return ""
    body = m.group(1).strip("\n")
    lines = [ln.rstrip() for ln in body.splitlines()]
    purpose_lines: list[str] = []
    in_purpose = False
    for ln in lines:
        if ln.strip().lower().startswith("purpose:"):
            in_purpose = True
            rest = ln.split(":", 1)[1].strip()
            if rest and rest != "Module: " + body.split("File:")[-1].splitlines()[0].strip() if "File:" in body else True:
                if not rest.startswith("Module:"):
                    purpose_lines.append(rest)
            continue
        if in_purpose:
            if ln.startswith(("File:", "Work Package:", "Responsible Engineer:")):
                break
            if ln.strip() == "":
                if purpose_lines:
                    break
                continue
            purpose_lines.append(ln.strip())
    if purpose_lines:
        joined = " ".join(purpose_lines)
        if joined.startswith("Module:"):
            return ""
        return joined
    for ln in reversed(lines):
        if ln.strip() and not ln.startswith(
            ("File:", "Work Package:", "Responsible Engineer:", "Additional")
        ):
            text_val = ln.strip().strip('"')
            if not text_val.startswith("Module:"):
                return text_val
    return ""


def build_header(path: Path, purpose: str) -> str:
    purpose = purpose or default_purpose(path)
    return (
        '"""\n'
        f"File: {path.name}\n"
        f"Work Package: {work_package_label(path)}\n"
        f"Responsible Engineer: {engineer_for(path)}\n"
        f"Purpose: {purpose}\n"
        '"""\n'
    )


def main() -> None:
    updated: list[str] = []
    for path in sorted(ROOT.rglob("*.py")):
        rel = path.relative_to(ROOT)
        if any(p == "__pycache__" for p in rel.parts) or rel.parts[0] == "tools":
            continue
        text = path.read_text(encoding="utf-8")
        purpose = extract_purpose(text)
        header = build_header(path, purpose)

        if text.startswith('"""'):
            rest = re.sub(r'^""".*?"""\n', "", text, count=1, flags=re.DOTALL)
            new_text = header + rest.lstrip("\n")
        else:
            new_text = header + "\n" + text

        if new_text != text:
            path.write_text(new_text, encoding="utf-8", newline="\n")
            updated.append(rel.as_posix())

    print(f"Updated {len(updated)} files")
    for u in updated:
        print(u)


if __name__ == "__main__":
    main()
