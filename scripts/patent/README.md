# Gaze-WAM Patent Artifacts

The scripts in this directory reproduce and validate the code-aligned Chinese
patent disclosure and its editable Draw.io figures.

## Build

Run from the repository root:

```powershell
python scripts/patent/build_patent_figures.py
python scripts/patent/build_patent_disclosure.py
python scripts/patent/validate_patent_artifacts.py
```

Generated deliverables:

- `output/doc/Gaze-WAM_发明专利技术交底书_代码对齐版.docx`
- `output/patent_figures/gaze_wam_patent_figures.drawio`
- `output/patent_figures/figure_01_overall_training.png`
- `output/patent_figures/figure_02_sample_routing.png`
- `output/patent_figures/figure_03_dual_stream_cache.png`
- `output/patent_figures/figure_04_train_inference.png`

The DOCX equations are native editable Word OMML objects. The validator checks
the OMML equation count, summation formatting, external hyperlinks, embedded
figures, and Draw.io graph integrity.
