---
name: powerbi-dashboard-generator
description: >-
  End-to-end Excel/CSV to Power BI (.pbit/.pbix) and interactive HTML Executive
  Dashboard generator. Use when the user provides any Excel (.xlsx/.xls) or CSV
  dataset and wants to build a colorful, professional Power BI dashboard with
  automatic data cleaning, ROC/ISO date normalization, anomaly period detection,
  chronological trend sorting, multi-level drill-down hierarchies, cross-PC
  v1.28 PBIX packaging, or wants to launch the visual Power BI Studio App.
---

# Power BI Dashboard Generator (`powerbi-dashboard-generator`)

## Overview

Transforms any Excel (`.xlsx`, `.xls`) or `.csv` dataset into both a **native Power BI Desktop dashboard (`.pbit` / cross-PC compatible `.pbix`)** and a **standalone interactive HTML Executive Dashboard (`.html`)**.

Key capabilities built into this skill:
1. **Smart Data Inspection & Anomaly Detection**: Automatically parses all worksheets, normalizes ROC 7-digit dates (e.g., `1150701` $\rightarrow$ `2026-07-01`) and standard dates, builds a continuous `Dim_Date` table, and detects sparse/anomalous months (`<2%` of total records) so they can be reported and excluded.
2. **Chronological Trend Sorting**: Binds all daily/monthly trend visuals to `Dim_Date[Date]` or `Dim_Date[YearMonth]` with explicit `OrderBy` ascending (`Direction: 1`).
3. **Multi-Level Drill-Down Hierarchies (`向下鑽研`)**: Configures multi-level `Category` projections (`Level 1 -> Level 2 -> Level 3`) in Power BI visuals and interactive click-to-drill-down trees in the HTML dashboard.
4. **Universal Cross-PC Packaging (`v1.28`)**: Packages `.pbit` and `.pbix` files using `Microsoft.PowerBI.Packaging.dll` with `Version: 1.28` and standard `Report/Layout` metadata so files open on any computer without PBIR preview errors.
5. **Standalone Visual Studio App**: Includes a browser-based GUI (`c:\馨\Power BI\啟動_PowerBI_自動生成APP.bat`) with drag-and-drop Excel upload, natural language prompt input, and visual chart/drill-down selectors.

## Dependencies

- **`uv`**: Required for executing the CLI script reliably via `uv run`.
- **`generative_ui`**: Referenced for executive dashboard card hierarchy, color palettes, and interactive visual layout standards.

## Quick Start

### 1. Inspect an Excel file for sheets, columns, and anomalous months
```powershell
uv run "c:\馨\Power BI\.agents\skills\powerbi-dashboard-generator\scripts\pbi_generator_cli.py" inspect --input "c:\path\to\data.xlsx" --limit 15 --output "inspect_result.json"
```

### 2. Build Power BI (`.pbit`), Interactive Web (`.html`), and Cleaned CSVs from Natural Language
```powershell
uv run "c:\馨\Power BI\.agents\skills\powerbi-dashboard-generator\scripts\pbi_generator_cli.py" build --input "c:\path\to\data.xlsx" --prompt "排除6月資料，門診科別重複用藥排行下鑽到開立理由，交互作用與跨院DDI下鑽到藥品品項" --theme executive_colorful --limit 25 --output "build_result.json"
```

### 3. Convert a Saved `.pbix` into a Cross-PC Compatible `.pbix`
```powershell
uv run "c:\馨\Power BI\.agents\skills\powerbi-dashboard-generator\scripts\pbi_generator_cli.py" repack-pbix --input-pbix "c:\path\to\saved.pbix" --layout-json "c:\path\to\Layout.json" --output-pbix "c:\path\to\saved_跨電腦相容版.pbix" --output "repack_result.json"
```

## Utility Scripts (CLI Subcommands)

All subcommands write structured JSON results to `--output` and require explicit `--limit` where applicable:

- **`inspect`**:
  - Arguments: `--input <path>` `--limit <int>` `--output <json_path>`
  - Inspects worksheets, column types (`date`, `category`, `numeric`, `text`), monthly record counts, sparse month anomalies, and generates a recommended dashboard blueprint.
- **`clean`**:
  - Arguments: `--input <path>` `--exclude-months <YYYY-MM,...>` `--out-dir <dir>` `--limit <int>` `--output <json_path>`
  - Normalizes dates, filters out excluded months, creates `Dim_Date.csv`, and exports UTF-8 with BOM CSV tables.
- **`build`**:
  - Arguments: `--input <path>` `--prompt <text>` `[--config <json>]` `[--theme <theme_name>]` `[--exclude-months <YYYY-MM,...>]` `[--out-dir <dir>]` `--limit <int>` `--output <json_path>`
  - Generates the `.pbit` file, interactive `.html` dashboard, and cleaned CSV folder.
- **`repack-pbix`**:
  - Arguments: `--input-pbix <path>` `--layout-json <path>` `--output-pbix <path>` `--output <json_path>`
  - Extracts the compiled VertiPaq `DataModel` stream from a saved `.pbix` and repackages it with universal `v1.28 Report/Layout` metadata.
- **`serve-app`**:
  - Arguments: `[--port 8765]` `[--no-browser]` `--output <json_path>`
  - Starts the visual `Power BI Studio App` local web interface.

## Rate Limiting

All core data processing and `.NET` Power BI packaging operations run locally with zero external API calls. For future external data connectors, `pbi_generator_cli.py` includes `MonotonicRateLimiter` using `time.monotonic()` defaulting to `1.0` request per second.

## Common Mistakes

1. **Saving `.pbix` with PBIR Preview Format (`v1.32 Report/definition`)**:
   - If a `.pbix` is saved while PBIR preview is active, other computers without the preview flag enabled will fail to open it. Always run `repack-pbix` to produce a universal `v1.28` `.pbix` with embedded `DataModel`.
2. **Sorting Trend Charts by Count Instead of Date**:
   - Power BI defaults to sorting visuals descending by measure value (`Direction: 2`). Always bind trend visuals to `Dim_Date[Date]` with `Direction: 1` (ascending).
3. **Leaving Sparse Error Months Unfiltered**:
   - Always run `inspect` first and check `anomalies` for months with `<2%` of total records (such as stray out-of-period entries) and confirm with the user or pass `--exclude-months`.
