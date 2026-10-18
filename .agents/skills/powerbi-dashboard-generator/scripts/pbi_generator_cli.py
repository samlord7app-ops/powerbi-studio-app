#!/usr/bin/env python3
# /// script
# requires-python = ">=3.10"
# dependencies = [
#     "pandas",
#     "openpyxl",
# ]
# ///
"""
Power BI Dashboard Generator CLI (`pbi_generator_cli.py`)
Provides subcommands:
  - inspect     : Inspect an Excel/CSV file, detect columns, date ranges, and sparse month anomalies.
  - clean       : Clean dataset, filter excluded months, and export UTF-8-BOM CSV star-schema tables.
  - build       : Generate Power BI (.pbit) and interactive HTML (.html) dashboards from natural language or JSON config.
  - repack-pbix : Convert a saved .pbix file into a universal v1.28 cross-PC compatible .pbix with embedded DataModel.
  - serve-app   : Launch the standalone visual Power BI Studio Web App.
"""

import os
import sys
import time
import json
import argparse

# Locate core engine in c:\馨\Power BI\PowerBI_Studio_App
DEFAULT_APP_DIR = r"c:\馨\Power BI\PowerBI_Studio_App"
if os.path.exists(DEFAULT_APP_DIR) and DEFAULT_APP_DIR not in sys.path:
    sys.path.insert(0, DEFAULT_APP_DIR)
else:
    rel_app_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "..", "..", "PowerBI_Studio_App"))
    if os.path.exists(rel_app_dir) and rel_app_dir not in sys.path:
        sys.path.insert(0, rel_app_dir)

import pbi_engine


class RateLimitError(Exception):
    """Raised when an external service returns HTTP 429 rate limit exceeded."""
    pass


class MonotonicRateLimiter:
    """Cross-call monotonic rate limiter (1 request/sec default per skill guidelines)."""
    def __init__(self, calls_per_second: float = 1.0):
        self.min_interval = 1.0 / max(calls_per_second, 0.01)
        self._last_call = 0.0

    def wait(self):
        now = time.monotonic()
        elapsed = now - self._last_call
        if elapsed < self.min_interval:
            time.sleep(self.min_interval - elapsed)
        self._last_call = time.monotonic()


def write_json_output(data: dict, output_path: str):
    out_abs = os.path.abspath(output_path)
    os.makedirs(os.path.dirname(out_abs), exist_ok=True)
    with open(out_abs, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    print(f"Success! Data written to: {out_abs}")


def cmd_inspect(args):
    info = pbi_engine.inspect_dataset(args.input, limit=args.limit)
    write_json_output(info, args.output)


def cmd_clean(args):
    info = pbi_engine.inspect_dataset(args.input, limit=args.limit)
    cfg = info["recommended_config"]
    if args.exclude_months:
        cfg["exclude_months"] = [m.strip() for m in args.exclude_months.split(",") if m.strip()]
    res = pbi_engine.build_dashboard_bundle(args.input, cfg, args.out_dir, limit_top_n=args.limit)
    write_json_output(res, args.output)


def cmd_build(args):
    info = pbi_engine.inspect_dataset(args.input, limit=args.limit)
    if args.config and os.path.exists(args.config):
        with open(args.config, "r", encoding="utf-8") as f:
            cfg = json.load(f)
    else:
        cfg = pbi_engine.parse_natural_language_request(args.prompt or "", info)

    if args.theme:
        cfg["theme"] = args.theme
    if args.exclude_months is not None:
        cfg["exclude_months"] = [m.strip() for m in args.exclude_months.split(",") if m.strip()]

    out_dir = args.out_dir or os.path.join(os.path.dirname(os.path.abspath(args.input)), "Generated_Dashboards", pbi_engine.sanitize_table_name(os.path.splitext(os.path.basename(args.input))[0]))
    res = pbi_engine.build_dashboard_bundle(args.input, cfg, out_dir, limit_top_n=args.limit)
    write_json_output(res, args.output)


def cmd_repack_pbix(args):
    res = pbi_engine.repack_pbix_cross_pc(args.input_pbix, args.layout_json, args.output_pbix)
    write_json_output(res, args.output)


def cmd_serve_app(args):
    app_script = os.path.join(DEFAULT_APP_DIR, "app_server.py")
    write_json_output({
        "status": "starting",
        "url": f"http://127.0.0.1:{args.port}",
        "app_script": app_script
    }, args.output)
    import app_server
    app_server.run_server(port=args.port, open_browser=not args.no_browser)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="pbi_generator_cli",
        description="Universal Excel/CSV to Power BI (.pbit/.pbix) and Interactive HTML Dashboard Generator CLI"
    )
    sub = parser.add_subparsers(dest="command", required=True)

    # 1. inspect
    p_insp = sub.add_parser("inspect", help="Inspect Excel/CSV structure, date anomalies, and recommended config")
    p_insp.add_argument("--input", required=True, help="Path to input .xlsx, .xls, or .csv file")
    p_insp.add_argument("--limit", type=int, required=True, help="Max preview rows per sheet (explicitly required)")
    p_insp.add_argument("--output", required=True, help="Output JSON file path")
    p_insp.set_defaults(func=cmd_inspect)

    # 2. clean
    p_clean = sub.add_parser("clean", help="Clean dataset, remove anomalous months, and export Star Schema CSVs")
    p_clean.add_argument("--input", required=True, help="Path to input .xlsx, .xls, or .csv file")
    p_clean.add_argument("--exclude-months", default="", help="Comma-separated YYYY-MM months to exclude (e.g. 2026-06)")
    p_clean.add_argument("--out-dir", required=True, help="Target directory for cleaned CSVs and bundle")
    p_clean.add_argument("--limit", type=int, required=True, help="Top N items limit for aggregations")
    p_clean.add_argument("--output", required=True, help="Output manifest JSON file path")
    p_clean.set_defaults(func=cmd_clean)

    # 3. build
    p_build = sub.add_parser("build", help="Build Power BI (.pbit) and interactive HTML (.html) dashboards")
    p_build.add_argument("--input", required=True, help="Path to input .xlsx, .xls, or .csv file")
    p_build.add_argument("--prompt", default="", help="Natural language requirement description")
    p_build.add_argument("--config", default="", help="Optional path to custom dashboard config JSON")
    p_build.add_argument("--theme", default="", choices=["", "executive_colorful", "medical_teal", "modern_sapphire", "warm_sunset"], help="Color palette theme")
    p_build.add_argument("--exclude-months", default=None, help="Comma-separated YYYY-MM months to exclude")
    p_build.add_argument("--out-dir", default="", help="Output directory for generated .pbit, .html, and CSVs")
    p_build.add_argument("--limit", type=int, required=True, help="Max items per drill-down level (explicitly required)")
    p_build.add_argument("--output", required=True, help="Output result JSON file path")
    p_build.set_defaults(func=cmd_build)

    # 4. repack-pbix
    p_repack = sub.add_parser("repack-pbix", help="Repackage a saved .pbix into a cross-PC compatible v1.28 .pbix")
    p_repack.add_argument("--input-pbix", required=True, help="Path to source .pbix file saved by Power BI Desktop")
    p_repack.add_argument("--layout-json", required=True, help="Path to Report/Layout JSON file")
    p_repack.add_argument("--output-pbix", required=True, help="Target path for universal cross-PC .pbix")
    p_repack.add_argument("--output", required=True, help="Output status JSON file path")
    p_repack.set_defaults(func=cmd_repack_pbix)

    # 5. serve-app
    p_serve = sub.add_parser("serve-app", help="Start the visual Power BI Studio Web App")
    p_serve.add_argument("--port", type=int, default=8765, help="Local port (default: 8765)")
    p_serve.add_argument("--no-browser", action="store_true", help="Do not open browser automatically")
    p_serve.add_argument("--output", required=True, help="Output status JSON file path")
    p_serve.set_defaults(func=cmd_serve_app)

    return parser


def main():
    parser = build_parser()
    args = parser.parse_args()
    try:
        args.func(args)
    except Exception as exc:
        sys.stderr.write(f"ERROR: {exc}\n")
        sys.exit(1)


if __name__ == "__main__":
    main()
