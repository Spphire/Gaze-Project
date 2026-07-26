from __future__ import annotations

import argparse
import json
import xml.etree.ElementTree as ET
import zipfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
DEFAULT_DOCX = ROOT / "output" / "doc" / "Gaze-WAM_发明专利技术交底书_代码对齐版.docx"
DEFAULT_DRAWIO = ROOT / "output" / "patent_figures" / "gaze_wam_patent_figures.drawio"

WORD_NS = "http://schemas.openxmlformats.org/wordprocessingml/2006/main"
MATH_NS = "http://schemas.openxmlformats.org/officeDocument/2006/math"
REL_NS = "http://schemas.openxmlformats.org/package/2006/relationships"
NS = {"w": WORD_NS, "m": MATH_NS, "pr": REL_NS}


def validate_docx(path: Path) -> tuple[dict[str, object], list[str]]:
    errors: list[str] = []
    with zipfile.ZipFile(path) as archive:
        names = set(archive.namelist())
        document = ET.fromstring(archive.read("word/document.xml"))
        relationships = ET.fromstring(archive.read("word/_rels/document.xml.rels"))

    equations = document.findall(".//m:oMath", NS)
    nary_sums = document.findall(".//m:nary", NS)
    hidden_superscripts = 0
    for nary in nary_sums:
        sup_hide = nary.find("m:naryPr/m:supHide", NS)
        if sup_hide is not None and sup_hide.get(f"{{{MATH_NS}}}val", "1") in {"1", "true", "on"}:
            hidden_superscripts += 1

    external_hyperlinks = [
        rel
        for rel in relationships.findall(f"{{{REL_NS}}}Relationship")
        if rel.get("Type", "").endswith("/hyperlink") and rel.get("TargetMode") == "External"
    ]
    drawings = document.findall(".//w:drawing", NS)
    media = sorted(name for name in names if name.startswith("word/media/") and not name.endswith("/"))

    expected = {
        "editable_omml_equations": 15,
        "nary_sums": 6,
        "nary_sums_with_hidden_superscript": 6,
        "external_hyperlinks": 19,
        "embedded_drawings": 4,
        "embedded_media": 4,
    }
    actual = {
        "editable_omml_equations": len(equations),
        "nary_sums": len(nary_sums),
        "nary_sums_with_hidden_superscript": hidden_superscripts,
        "external_hyperlinks": len(external_hyperlinks),
        "embedded_drawings": len(drawings),
        "embedded_media": len(media),
    }
    for key, expected_value in expected.items():
        if actual[key] != expected_value:
            errors.append(f"DOCX {key}: expected {expected_value}, got {actual[key]}")

    return {"path": str(path), **actual, "media": media}, errors


def validate_drawio(path: Path) -> tuple[dict[str, object], list[str]]:
    errors: list[str] = []
    mxfile = ET.parse(path).getroot()
    diagrams = mxfile.findall("diagram")
    if mxfile.get("compressed") != "false":
        errors.append("Draw.io source must remain uncompressed and directly editable")
    if len(diagrams) != 4:
        errors.append(f"Draw.io pages: expected 4, got {len(diagrams)}")

    page_stats: list[dict[str, object]] = []
    for diagram in diagrams:
        graph_root = diagram.find("mxGraphModel/root")
        if graph_root is None:
            errors.append(f"Draw.io page {diagram.get('name')!r} has no mxGraphModel/root")
            continue

        cells = graph_root.findall("mxCell")
        ids = [cell.get("id") for cell in cells]
        valid_ids = {cell_id for cell_id in ids if cell_id is not None}
        duplicate_ids = sorted({cell_id for cell_id in valid_ids if ids.count(cell_id) > 1})
        vertices = [cell for cell in cells if cell.get("vertex") == "1"]
        edges = [cell for cell in cells if cell.get("edge") == "1"]
        broken_edges: list[str] = []
        missing_geometry: list[str] = []
        for edge in edges:
            edge_id = edge.get("id", "<unnamed>")
            source = edge.get("source")
            target = edge.get("target")
            if source not in valid_ids or target not in valid_ids:
                broken_edges.append(edge_id)
            geometry = edge.find("mxGeometry")
            if geometry is None or geometry.get("relative") != "1":
                missing_geometry.append(edge_id)

        if duplicate_ids:
            errors.append(f"Draw.io page {diagram.get('name')!r} duplicate IDs: {duplicate_ids}")
        if broken_edges:
            errors.append(f"Draw.io page {diagram.get('name')!r} broken edges: {broken_edges}")
        if missing_geometry:
            errors.append(f"Draw.io page {diagram.get('name')!r} invalid edge geometry: {missing_geometry}")

        page_stats.append(
            {
                "name": diagram.get("name"),
                "cells": len(cells),
                "vertices": len(vertices),
                "edges": len(edges),
            }
        )

    return {"path": str(path), "pages": page_stats}, errors


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate the generated Gaze-WAM patent artifacts.")
    parser.add_argument("--docx", type=Path, default=DEFAULT_DOCX)
    parser.add_argument("--drawio", type=Path, default=DEFAULT_DRAWIO)
    args = parser.parse_args()

    errors: list[str] = []
    docx_report, docx_errors = validate_docx(args.docx)
    drawio_report, drawio_errors = validate_drawio(args.drawio)
    errors.extend(docx_errors)
    errors.extend(drawio_errors)

    report = {
        "ok": not errors,
        "docx": docx_report,
        "drawio": drawio_report,
        "errors": errors,
    }
    print(json.dumps(report, ensure_ascii=False, indent=2))
    return 0 if not errors else 1


if __name__ == "__main__":
    raise SystemExit(main())
