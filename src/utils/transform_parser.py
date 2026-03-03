from __future__ import annotations

from pathlib import Path
from typing import Any, Dict, List

from models.transform import TransformTemplate


def _tokenize(text: str) -> List[str]:
    text = text.replace("(", " ( ").replace(")", " ) ")
    return [t for t in text.split() if t]


def _parse(tokens: List[str]) -> Any:
    if not tokens:
        raise ValueError("Unexpected EOF while parsing")

    tok = tokens.pop(0)
    if tok == "(":
        out = []
        while tokens and tokens[0] != ")":
            out.append(_parse(tokens))
        if not tokens:
            raise ValueError("Missing ')'")
        tokens.pop(0)  # consume ')'
        return out
    if tok == ")":
        raise ValueError("Unexpected ')'")
    return tok


def _pairs_to_dict(node: Any, label: str, *, file_hint: str) -> Dict[str, int]:
    if not (isinstance(node, list) and node and node[0] == label):
        raise ValueError(f"{file_hint}: Expected ({label} ...), got: {node!r}")

    out: Dict[str, int] = {}
    for pair in node[1:]:
        if not (isinstance(pair, list) and len(pair) == 2):
            raise ValueError(f"{file_hint}: Expected (Resource Amount) in {label}, got: {pair!r}")
        res, amt = pair
        out[str(res)] = int(float(str(amt)))
    return out


def _infer_name_from_outputs(outputs: Dict[str, int], fallback: str) -> str:
    for r in outputs.keys():
        if not r.endswith("Waste"):
            return r
    return fallback


def load_transform_template_file(path: str | Path) -> TransformTemplate:
    path = Path(path)
    file_hint = path.name

    text = path.read_text(encoding="utf-8").strip()
    tokens = _tokenize(text)
    expr = _parse(tokens)

    if tokens:
        raise ValueError(f"{file_hint}: extra tokens after first expression")

    if not (isinstance(expr, list) and len(expr) >= 3 and expr[0] == "TRANSFORM"):
        raise ValueError(f"{file_hint}: expected (TRANSFORM ...), got: {expr!r}")

    inputs_node = next((n for n in expr if isinstance(n, list) and n and n[0] == "INPUTS"), None)
    outputs_node = next((n for n in expr if isinstance(n, list) and n and n[0] == "OUTPUTS"), None)

    if inputs_node is None or outputs_node is None:
        raise ValueError(f"{file_hint}: TRANSFORM missing INPUTS or OUTPUTS")

    inputs = _pairs_to_dict(inputs_node, "INPUTS", file_hint=file_hint)
    outputs = _pairs_to_dict(outputs_node, "OUTPUTS", file_hint=file_hint)

    name = path.stem[:1].upper() + path.stem[1:]
    return TransformTemplate(name=name, inputs=inputs, outputs=outputs)


def load_transform_templates_dir(dir_path: str | Path) -> Dict[str, TransformTemplate]:
    dir_path = Path(dir_path)
    templates: Dict[str, TransformTemplate] = {}

    for tmpl_file in sorted(dir_path.glob("*.tmpl")):
        tmpl = load_transform_template_file(tmpl_file)
        if tmpl.name in templates:
            raise ValueError(
                f"Duplicate transform template name {tmpl.name!r}: "
                f"{tmpl_file.name} conflicts with another .tmpl"
            )
        templates[tmpl.name] = tmpl

    if not templates:
        raise ValueError(f"No .tmpl files found in {dir_path}")

    return templates