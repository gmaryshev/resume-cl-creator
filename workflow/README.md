# Context bundler

`bundle_context.py` preserves the separate reference folders while assembling
one traceable context package for a generation run. The checked-in
[`source_registry.json`](./source_registry.json) is the approval list; adding a
file to a reference folder does not automatically make it generation input.

Run it from the repository root:

```bash
python3 workflow/bundle_context.py Job_descriptions/jobdesc
```

The normal workflow entry point is still `go wf.txt`. When that instruction is
used, run the command above first and use the printed bundle directory for the
rest of the run. Do not generate documents or tracking rows if bundling fails.

The command writes an ignored directory under `.workflow/bundles/` containing:

- `context.md`: compact source content and Copilot generation constraints.
- `manifest.json`: source groups, trust levels, SHA-256 hashes, character
  counts, and summarization requests.

The script does not call a cloud model. For sources above the configured
threshold, the bundle records a Copilot-agent summarization request with
provenance requirements. Use `--summary-threshold` to change that threshold
and `--run-name` to choose a stable run directory name. Existing bundle
directories are never overwritten.
