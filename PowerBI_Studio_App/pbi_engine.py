import os
import re
import csv
import json
import shutil
import subprocess
from datetime import datetime, timedelta
import pandas as pd

# ==============================================================================
# Color Palettes (4 Professional Executive BI Themes)
# ==============================================================================
THEMES = {
    "executive_colorful": {
        "name": "Executive Colorful 專業多彩風",
        "banner_bg": "#0F172A",
        "banner_sub": "#93C5FD",
        "canvas_bg": "#E2E8F0",
        "data_colors": [
            "#2563EB", "#0D9488", "#7C3AED", "#EA580C", "#E11D48",
            "#0284C7", "#D97706", "#4F46E5", "#059669", "#DB2777"
        ],
        "kpi_styles": [
            {"title_bg": "#1E40AF", "callout": "#1D4ED8", "card_bg": "#EFF6FF", "border": "#93C5FD"},
            {"title_bg": "#0D9488", "callout": "#0F766E", "card_bg": "#F0FDFA", "border": "#5EEAD4"},
            {"title_bg": "#D97706", "callout": "#B45309", "card_bg": "#FFFBEB", "border": "#FCD34D"},
            {"title_bg": "#E11D48", "callout": "#BE123C", "card_bg": "#FFF1F2", "border": "#FDA4AF"}
        ],
        "chart_headers": ["#1E3A8A", "#065F46", "#9F1239", "#4C1D95", "#B45309", "#0F766E"]
    },
    "medical_teal": {
        "name": "Medical Teal & Coral 醫療品質風",
        "banner_bg": "#134E4A",
        "banner_sub": "#5EEAD4",
        "canvas_bg": "#F0FDFA",
        "data_colors": [
            "#0D9488", "#0284C7", "#E11D48", "#D97706", "#4F46E5",
            "#059669", "#7C3AED", "#EA580C", "#2563EB", "#0891B2"
        ],
        "kpi_styles": [
            {"title_bg": "#0F766E", "callout": "#115E59", "card_bg": "#F0FDFA", "border": "#5EEAD4"},
            {"title_bg": "#0369A1", "callout": "#075985", "card_bg": "#F0F9FF", "border": "#7DD3FC"},
            {"title_bg": "#B45309", "callout": "#92400E", "card_bg": "#FFFBEB", "border": "#FCD34D"},
            {"title_bg": "#BE123C", "callout": "#9F1239", "card_bg": "#FFF1F2", "border": "#FDA4AF"}
        ],
        "chart_headers": ["#0F766E", "#0369A1", "#BE123C", "#1E40AF", "#B45309", "#4338CA"]
    },
    "modern_sapphire": {
        "name": "Modern Sapphire 現代商務藍",
        "banner_bg": "#1E3A8A",
        "banner_sub": "#BFDBFE",
        "canvas_bg": "#EFF6FF",
        "data_colors": [
            "#1D4ED8", "#3B82F6", "#6366F1", "#0EA5E9", "#8B5CF6",
            "#14B8A6", "#F59E0B", "#EC4899", "#10B981", "#64748B"
        ],
        "kpi_styles": [
            {"title_bg": "#1E3A8A", "callout": "#1D4ED8", "card_bg": "#EFF6FF", "border": "#93C5FD"},
            {"title_bg": "#3730A3", "callout": "#4338CA", "card_bg": "#EEF2FF", "border": "#A5B4FC"},
            {"title_bg": "#0369A1", "callout": "#0284C7", "card_bg": "#F0F9FF", "border": "#7DD3FC"},
            {"title_bg": "#0F766E", "callout": "#0D9488", "card_bg": "#F0FDFA", "border": "#5EEAD4"}
        ],
        "chart_headers": ["#1E3A8A", "#3730A3", "#0369A1", "#0F766E", "#4C1D95", "#1E40AF"]
    },
    "warm_sunset": {
        "name": "Warm Sunset 暖陽活力風",
        "banner_bg": "#7C2D12",
        "banner_sub": "#FDBA74",
        "canvas_bg": "#FFF7ED",
        "data_colors": [
            "#EA580C", "#E11D48", "#D97706", "#7C3AED", "#0D9488",
            "#2563EB", "#DB2777", "#65A30D", "#0284C7", "#4F46E5"
        ],
        "kpi_styles": [
            {"title_bg": "#C2410C", "callout": "#9A3412", "card_bg": "#FFF7ED", "border": "#FDBA74"},
            {"title_bg": "#BE123C", "callout": "#9F1239", "card_bg": "#FFF1F2", "border": "#FDA4AF"},
            {"title_bg": "#B45309", "callout": "#92400E", "card_bg": "#FFFBEB", "border": "#FCD34D"},
            {"title_bg": "#6D28D9", "callout": "#5B21B6", "card_bg": "#F5F3FF", "border": "#C4B5FD"}
        ],
        "chart_headers": ["#C2410C", "#BE123C", "#B45309", "#6D28D9", "#0F766E", "#1E40AF"]
    }
}

# Built-in hospital section code dictionary (used automatically if OPDSECTION is present)
SECTION_MAP = {
    "01": "家醫科", "02": "內科", "03": "外科", "04": "兒科", "05": "婦產科",
    "06": "骨科", "07": "神經外科", "08": "泌尿科", "09": "耳鼻喉科", "10": "眼科",
    "11": "皮膚科", "12": "神經科", "13": "精神科", "14": "復健科", "15": "整形外科",
    "40": "牙科", "60": "中醫一般科", "85": "高齡醫學科",
    "CV": "心臟血管內科", "GI": "胃腸肝膽科", "chest": "胸腔內科", "CHEST": "胸腔內科",
    "NEPH": "腎臟內科", "META": "新陳代謝科", "ENDO": "內分泌新陳代謝科", "RHEU": "風濕免疫科",
    "INF": "感染科", "HEMA": "血液腫瘤科", "NEUR": "神經內科", "PSY": "身心醫學科",
    "FM": "家庭醫學科", "OPH": "眼科", "ENT": "耳鼻喉科", "DERM": "皮膚科",
    "URO": "泌尿科", "ORTH": "骨科", "NS": "神經外科", "GS": "一般外科",
    "CRS": "大腸直腸外科", "CVS": "心臟血管外科", "CS": "胸腔外科", "PS": "整形外科",
    "PED": "小兒科", "OBGYN": "婦產科", "REH": "復健科", "TCM": "中醫科"
}


def sanitize_table_name(name: str) -> str:
    clean = re.sub(r'[^\w\u4e00-\u9fff]+', '_', str(name).strip()).strip('_')
    return clean or "Table_1"


def parse_any_date(val) -> str:
    """Normalizes ROC 7-digit (1150701), 8-digit (20260701), slash/dash dates, or datetime to YYYY-MM-DD."""
    if pd.isna(val):
        return ""
    if isinstance(val, (datetime, pd.Timestamp)):
        return val.strftime("%Y-%m-%d")
    s = str(val).strip()
    if not s or s.lower() in ("nan", "none", "null", "nat"):
        return ""
    if s.endswith(".0"):
        s = s[:-2]
    digits = re.sub(r"\D", "", s)
    # 7-digit ROC date e.g. 1150701 -> 2026-07-01
    if len(digits) == 7 and digits.startswith(("10", "11", "12")):
        y = int(digits[:3]) + 1911
        m = int(digits[3:5])
        d = int(digits[5:7])
        try:
            return datetime(y, m, d).strftime("%Y-%m-%d")
        except ValueError:
            return ""
    # 6-digit ROC date e.g. 990701
    if len(digits) == 6 and int(digits[:2]) >= 70:
        y = int(digits[:2]) + 1911
        m = int(digits[2:4])
        d = int(digits[4:6])
        try:
            return datetime(y, m, d).strftime("%Y-%m-%d")
        except ValueError:
            return ""
    # 8-digit ISO date e.g. 20260701
    if len(digits) == 8 and digits.startswith(("19", "20")):
        y = int(digits[:4])
        m = int(digits[4:6])
        d = int(digits[6:8])
        try:
            return datetime(y, m, d).strftime("%Y-%m-%d")
        except ValueError:
            return ""
    # ROC with slashes e.g. 115/07/01 or 115-07-01
    m_roc = re.match(r"^(\d{2,3})[/\-.](\d{1,2})[/\-.](\d{1,2})", s)
    if m_roc and int(m_roc.group(1)) < 200:
        y = int(m_roc.group(1)) + 1911
        m = int(m_roc.group(2))
        d = int(m_roc.group(3))
        try:
            return datetime(y, m, d).strftime("%Y-%m-%d")
        except ValueError:
            return ""
    # Standard ISO/slash date
    try:
        dt = pd.to_datetime(s, errors="raise")
        if 1970 <= dt.year <= 2100:
            return dt.strftime("%Y-%m-%d")
    except Exception:
        pass
    return ""


def _col_letters_to_idx(letters: str) -> int:
    idx = 0
    for ch in letters:
        idx = idx * 26 + (ord(ch.upper()) - ord('A') + 1)
    return idx - 1


def _read_xlsx_via_stdlib(xlsx_path: str) -> dict:
    """Reads all sheets from an .xlsx file using only Python stdlib (zipfile + xml.etree.ElementTree)."""
    import zipfile
    import xml.etree.ElementTree as ET

    ns = {"main": "http://schemas.openxmlformats.org/spreadsheetml/2006/main"}
    sheets = {}
    with zipfile.ZipFile(xlsx_path, "r") as z:
        shared_strings = []
        if "xl/sharedStrings.xml" in z.namelist():
            ss_xml = ET.fromstring(z.read("xl/sharedStrings.xml"))
            for si in ss_xml.findall("{http://schemas.openxmlformats.org/spreadsheetml/2006/main}si"):
                t_els = si.findall(".//{http://schemas.openxmlformats.org/spreadsheetml/2006/main}t")
                shared_strings.append("".join(t.text or "" for t in t_els))

        # Parse sheet names from workbook.xml
        wb_xml = ET.fromstring(z.read("xl/workbook.xml"))
        sheet_Defs = []
        for idx, sh in enumerate(wb_xml.findall(".//{http://schemas.openxmlformats.org/spreadsheetml/2006/main}sheet"), start=1):
            sname = sh.attrib.get("name", f"Sheet{idx}")
            sheet_Defs.append((idx, sname))

        for idx, sname in sheet_Defs:
            xml_path = f"xl/worksheets/sheet{idx}.xml"
            if xml_path not in z.namelist():
                continue
            sheet_xml = ET.fromstring(z.read(xml_path))
            raw_rows = []
            max_col = 0
            for row_el in sheet_xml.findall(".//{http://schemas.openxmlformats.org/spreadsheetml/2006/main}row"):
                row_dict = {}
                for c in row_el.findall("{http://schemas.openxmlformats.org/spreadsheetml/2006/main}c"):
                    ref = c.attrib.get("r", "")
                    col_letters = "".join(filter(str.isalpha, ref))
                    col_idx = _col_letters_to_idx(col_letters) if col_letters else len(row_dict)
                    if col_idx + 1 > max_col:
                        max_col = col_idx + 1
                    t = c.attrib.get("t", "")
                    v_el = c.find("{http://schemas.openxmlformats.org/spreadsheetml/2006/main}v")
                    is_el = c.find("{http://schemas.openxmlformats.org/spreadsheetml/2006/main}is")
                    val = ""
                    if t == "s" and v_el is not None and v_el.text is not None:
                        val = shared_strings[int(v_el.text)]
                    elif t == "inlineStr" and is_el is not None:
                        t_els = is_el.findall(".//{http://schemas.openxmlformats.org/spreadsheetml/2006/main}t")
                        val = "".join(te.text or "" for te in t_els)
                    elif v_el is not None and v_el.text is not None:
                        val = v_el.text
                    row_dict[col_idx] = val
                if row_dict:
                    raw_rows.append(row_dict)

            if len(raw_rows) >= 2 and max_col > 0:
                headers = [str(raw_rows[0].get(i, f"Col_{i+1}")).strip() or f"Col_{i+1}" for i in range(max_col)]
                data_rows = []
                for r in raw_rows[1:]:
                    data_rows.append([r.get(i, "") for i in range(max_col)])
                df = pd.DataFrame(data_rows, columns=headers)
                if len(df) > 0:
                    sheets[sname] = df
    return sheets


def load_raw_sheets(file_path: str) -> dict:
    """Loads all sheets from an Excel (.xlsx/.xls) or CSV file safely (even if locked by Excel or missing openpyxl)."""
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"找不到輸入檔案: {file_path}")
    ext = os.path.splitext(file_path)[1].lower()
    temp_copy = None
    target_path = file_path
    try:
        with open(file_path, "rb"):
            pass
    except PermissionError:
        temp_copy = os.path.join(os.environ.get("TEMP", "."), f"temp_read_{os.getpid()}{ext}")
        shutil.copy2(file_path, temp_copy)
        target_path = temp_copy

    try:
        if ext in (".csv", ".txt", ".tsv"):
            sep = "\t" if ext == ".tsv" else ","
            try:
                df = pd.read_csv(target_path, sep=sep, encoding="utf-8-sig")
            except UnicodeDecodeError:
                df = pd.read_csv(target_path, sep=sep, encoding="cp950", errors="replace")
            base_name = sanitize_table_name(os.path.splitext(os.path.basename(file_path))[0])
            return {base_name: df}
        else:
            try:
                xl = pd.ExcelFile(target_path)
                sheets = {}
                for sname in xl.sheet_names:
                    df = xl.parse(sname)
                    if len(df.columns) > 0 and len(df) > 0:
                        sheets[sname] = df
                return sheets
            except Exception:
                return _read_xlsx_via_stdlib(target_path)
    finally:
        if temp_copy and os.path.exists(temp_copy):
            try:
                os.remove(temp_copy)
            except OSError:
                pass


def enrich_dataframe(df: pd.DataFrame, sheet_name: str) -> pd.DataFrame:
    """Applies automatic smart enrichment (date normalization, section names, drug pairs, memo quality)."""
    df = df.copy()
    # Drop completely empty Unnamed columns
    drop_cols = [c for c in df.columns if str(c).startswith("Unnamed:") and df[c].isna().all()]
    if drop_cols:
        df.drop(columns=drop_cols, inplace=True)

    # 1. Detect and normalize date column
    date_col_candidates = [
        c for c in df.columns
        if any(k in str(c).upper() for k in ("DATE", "日期", "年月", "時間", "DAY", "DT"))
    ]
    chosen_date_col = None
    for c in date_col_candidates:
        sample = df[c].dropna().head(30)
        if len(sample) > 0:
            parsed = [parse_any_date(v) for v in sample]
            if sum(1 for x in parsed if x) >= len(sample) * 0.6:
                chosen_date_col = c
                break
    if not chosen_date_col:
        for c in df.columns:
            sample = df[c].dropna().head(30)
            if len(sample) > 0:
                parsed = [parse_any_date(v) for v in sample]
                if sum(1 for x in parsed if x) >= len(sample) * 0.7:
                    chosen_date_col = c
                    break

    if chosen_date_col:
        df["Date"] = df[chosen_date_col].apply(parse_any_date)
        df["YearMonth"] = df["Date"].apply(lambda x: x[:7] if len(x) >= 7 else "Unknown")

    # 2. If OPDSECTION exists, enrich Section_Name
    for sec_col in ("OPDSECTION", "科別代碼", "部門代碼", "SECTION"):
        if sec_col in df.columns and "Section_Name" not in df.columns:
            df["Section_Name"] = df[sec_col].astype(str).str.strip().map(
                lambda x: f"{SECTION_MAP.get(x, x)} ({x})" if x in SECTION_MAP else x
            )
            break

    # 3. If hospital duplicate med memo column exists (RXUSEMEMO), enrich Memo_Quality & Clinical_Reason_Subcategory
    if "RXUSEMEMO" in df.columns:
        def classify_memo(val):
            s = str(val).strip() if pd.notna(val) else ""
            if not s or s.lower() in ("nan", "none") or re.match(r"^[\.\,\-\_0-9a-zA-Z]{1,2}$", s):
                return "無效/空白備註 (., 0, N, f 等)"
            return "具體臨床備註"

        def subcat_memo(row):
            memo = str(row.get("RXUSEMEMO", "")).strip() if pd.notna(row.get("RXUSEMEMO")) else ""
            code_nm = str(row.get("HISSYSCODENM", "")).strip() if pd.notna(row.get("HISSYSCODENM")) else ""
            if not memo or memo.lower() in ("nan", "none") or re.match(r"^[\.\,\-\_0-9a-zA-Z]{1,2}$", memo):
                return f"未填具體原因 ({code_nm[:8]})" if code_nm else "未填具體原因"
            if any(k in memo for k in ("出國", "遠行", "出海", "旅遊")):
                return "出國或遠行備藥"
            if any(k in memo for k in ("遺失", "弄丟", "破損", "打破")):
                return "藥品遺失或毀損"
            if any(k in memo for k in ("調整", "改藥", "加藥", "換藥", "劑量", "血壓", "血糖", "痛", "不適", "惡化", "發作", "住院", "急診")):
                return "病情變化/劑量調整"
            if any(k in memo for k in ("提前", "提早", "連假", "颱風", "回診", "順便", "合併", "同日")):
                return "配合回診/連假提前領藥"
            return "其他具體臨床說明"

        df["Memo_Quality"] = df["RXUSEMEMO"].apply(classify_memo)
        df["Is_Meaningless_Memo"] = df["Memo_Quality"].apply(lambda x: 1 if "無效" in x else 0)
        df["Clinical_Reason_Subcategory"] = df.apply(subcat_memo, axis=1)

    # 4. If hospital in-hospital DDI columns exist (UDDMDPNAME & UDDMDPNAME2)
    if "UDDMDPNAME" in df.columns and "UDDMDPNAME2" in df.columns:
        df["Drug_Pair_Display"] = (
            df["UDDMDPNAME"].fillna("Unknown").astype(str).str.strip().str[:22]
            + " + "
            + df["UDDMDPNAME2"].fillna("Unknown").astype(str).str.strip().str[:22]
        )

    # 5. If Cloud DDI COMMENTS column exists
    if "COMMENTS" in df.columns and "Severity_Level" not in df.columns:
        def parse_cloud_comment(val):
            s = str(val).strip() if pd.notna(val) else ""
            sev = "3_需密切監測 (Monitor Closely)"
            if any(k in s.lower() for k in ("contraindicated", "絕對禁忌", "禁止併用", "不可併用")):
                sev = "1_絕對禁忌 (Contraindicated)"
            elif any(k in s.lower() for k in ("avoid", "避免併用", "不建議併用", "嚴重")):
                sev = "2_建議避免併用 (Avoid Combination)"
            parts = re.split(r"[;；\n]", s)
            pair = parts[0][:45].strip() if parts else "未知藥物組合"
            drugs = re.split(r"\s+and\s+|\s*\+\s*|\s*與\s*", pair, maxsplit=1)
            d_a = drugs[0].strip()[:28] if len(drugs) > 0 else pair[:28]
            d_b = drugs[1].strip()[:28] if len(drugs) > 1 else "併用藥品"
            return pd.Series([sev, pair, d_a, d_b])

        parsed_cols = df["COMMENTS"].apply(parse_cloud_comment)
        parsed_cols.columns = ["Severity_Level", "Normalized_Drug_Pair", "Drug_A", "Drug_B"]
        for c in parsed_cols.columns:
            df[c] = parsed_cols[c]

    return df


def inspect_dataset(file_path: str, limit: int = 20) -> dict:
    """Inspects an Excel/CSV file, classifies columns, detects anomalies, and builds a recommended config."""
    raw_sheets = load_raw_sheets(file_path)
    sheets_info = {}
    overall_months = {}
    total_rows_all_sheets = 0

    for sname, raw_df in raw_sheets.items():
        df = enrich_dataframe(raw_df, sname)
        table_id = sanitize_table_name(sname)
        row_count = len(df)
        total_rows_all_sheets += row_count

        if "YearMonth" in df.columns:
            ym_counts = df["YearMonth"].value_counts().to_dict()
            for ym, cnt in ym_counts.items():
                if ym and ym != "Unknown":
                    overall_months[ym] = overall_months.get(ym, 0) + int(cnt)

        cols_meta = []
        date_cols = []
        cat_cols = []
        num_cols = []
        text_cols = []

        for col in df.columns:
            col_str = str(col)
            non_null = df[col].dropna()
            nunique = int(non_null.nunique())
            null_count = int(df[col].isna().sum())
            sample_vals = [str(v)[:50] for v in non_null.head(5).tolist()]

            if col_str in ("Date", "YearMonth") or any(k in col_str.upper() for k in ("DATE", "日期")):
                ctype = "date"
                date_cols.append(col_str)
            elif pd.api.types.is_numeric_dtype(df[col]) and not any(k in col_str.upper() for k in ("ID", "NO", "CODE", "代碼", "單號", "案號")):
                ctype = "numeric"
                num_cols.append(col_str)
            elif nunique <= max(120, int(row_count * 0.4)):
                ctype = "category"
                cat_cols.append(col_str)
            else:
                ctype = "text"
                text_cols.append(col_str)

            cols_meta.append({
                "name": col_str,
                "type": ctype,
                "distinct_count": nunique,
                "null_count": null_count,
                "samples": sample_vals
            })

        sheets_info[table_id] = {
            "original_sheet_name": sname,
            "table_name": table_id,
            "row_count": row_count,
            "columns": cols_meta,
            "date_columns": date_cols,
            "category_columns": cat_cols,
            "numeric_columns": num_cols,
            "text_columns": text_cols,
            "preview_rows": df.head(min(limit, 10)).fillna("").astype(str).to_dict(orient="records")
        }

    # Detect anomalous sparse months (< 2% of total records)
    anomalies = []
    sorted_months = sorted(overall_months.keys())
    total_dated_rows = sum(overall_months.values())
    recommended_exclude_months = []
    if total_dated_rows > 0 and len(sorted_months) > 1:
        for ym in sorted_months:
            cnt = overall_months[ym]
            ratio = cnt / total_dated_rows
            if ratio < 0.02 or (cnt < 20 and total_dated_rows > 500):
                anomalies.append({
                    "type": "sparse_month",
                    "month": ym,
                    "count": cnt,
                    "ratio_pct": round(ratio * 100, 2),
                    "message": f"偵測到【{ym}】僅有 {cnt} 筆資料（佔全體 {ratio*100:.2f}%），疑似跨期殘留或異常登錄資料，建議排除。"
                })
                recommended_exclude_months.append(ym)

    default_config = generate_recommended_config(file_path, sheets_info, recommended_exclude_months)

    return {
        "file_path": os.path.abspath(file_path),
        "file_name": os.path.basename(file_path),
        "total_sheets": len(sheets_info),
        "total_rows": total_rows_all_sheets,
        "monthly_distribution": {k: overall_months[k] for k in sorted_months},
        "anomalies": anomalies,
        "recommended_exclude_months": recommended_exclude_months,
        "sheets": sheets_info,
        "recommended_config": default_config
    }


def pick_best_drill_columns(sheet_meta: dict, preferred_keywords: list = None) -> list:
    """Picks 2 to 3 hierarchical columns for drill-down from a sheet."""
    cats = sheet_meta["category_columns"] + sheet_meta["text_columns"]
    exclude = {"Date", "YearMonth", "ID", "CASE_NO", "OPDCASENO", "OPDDATE"}
    candidates = [c for c in cats if c not in exclude]

    picked = []
    if preferred_keywords:
        for kw in preferred_keywords:
            for c in candidates:
                if kw.lower() in c.lower() and c not in picked:
                    picked.append(c)
                    break
    for c in candidates:
        if c not in picked and len(picked) < 3:
            picked.append(c)
    if not picked and cats:
        picked = cats[:2]
    return picked[:3]


def generate_recommended_config(file_path: str, sheets_info: dict, exclude_months: list) -> dict:
    """Automatically creates a complete KPI + Trend + Drill-down configuration for any Excel dataset."""
    table_names = list(sheets_info.keys())
    primary_table = table_names[0]
    base_title = os.path.splitext(os.path.basename(file_path))[0]

    # Check if this is the Hospital Medication Quality dataset or similar multi-sheet clinical dataset
    kpis = []
    trends = []
    charts = []
    slicers = []

    has_date = any("Date" in s["date_columns"] for s in sheets_info.values())
    if has_date:
        slicers.append({"table": "Dim_Date", "column": "YearMonth", "title": "📅 月份區間篩選"})

    # Find common category slicer (e.g. Section_Name or first medium-cardinality category)
    first_meta = sheets_info[primary_table]
    if "Section_Name" in first_meta["category_columns"]:
        slicers.append({"table": primary_table, "column": "Section_Name", "title": "🏥 部門/科別篩選"})
    elif first_meta["category_columns"]:
        c0 = [c for c in first_meta["category_columns"] if c not in ("Date", "YearMonth")]
        if c0:
            slicers.append({"table": primary_table, "column": c0[0], "title": f"🔍 {c0[0]} 篩選"})

    # Generate 4 KPIs across available sheets
    for idx, tname in enumerate(table_names[:4]):
        smeta = sheets_info[tname]
        orig_label = smeta["original_sheet_name"]
        kpis.append({
            "id": f"kpi_{idx+1}",
            "title": f"📊 {orig_label} 總筆數",
            "table": tname,
            "agg": "COUNTROWS",
            "column": smeta["columns"][0]["name"]
        })
        if "Is_Meaningless_Memo" in smeta["numeric_columns"] and len(kpis) < 4:
            kpis.append({
                "id": f"kpi_memo_{idx}",
                "title": f"✍️ {orig_label} 無效備註率",
                "table": tname,
                "agg": "MEANINGLESS_RATE",
                "column": "Is_Meaningless_Memo"
            })
        elif smeta["numeric_columns"] and len(kpis) < 4:
            ncol = smeta["numeric_columns"][0]
            kpis.append({
                "id": f"kpi_sum_{idx}",
                "title": f"📈 { ncol } 總計",
                "table": tname,
                "agg": "SUM",
                "column": ncol
            })

    while len(kpis) < 4:
        smeta = sheets_info[primary_table]
        cat_col = smeta["category_columns"][min(len(kpis) - 1, len(smeta["category_columns"]) - 1)] if smeta["category_columns"] else smeta["columns"][0]["name"]
        kpis.append({
            "id": f"kpi_extra_{len(kpis)+1}",
            "title": f"🎯 不重複 {cat_col} 數",
            "table": primary_table,
            "agg": "DISTINCTCOUNT",
            "column": cat_col
        })
    kpis = kpis[:4]

    # Generate 2 Chronological Daily/Monthly Trend Charts (Sorted Ascending by Date)
    trend_tables = [t for t in table_names if "Date" in sheets_info[t]["date_columns"]]
    if not trend_tables:
        trend_tables = [primary_table]
    for idx, tname in enumerate(trend_tables[:2]):
        orig_label = sheets_info[tname]["original_sheet_name"]
        trends.append({
            "id": f"trend_{idx+1}",
            "title": f"📈 每日{orig_label}趨勢 (依日期遞增排序)",
            "chart_type": "areaChart",
            "table": tname,
            "date_column": "Date" if "Date" in sheets_info[tname]["date_columns"] else sheets_info[tname]["columns"][0]["name"],
            "agg": "COUNTROWS",
            "value_column": sheets_info[tname]["columns"][0]["name"]
        })
    if len(trends) == 1:
        tname = trend_tables[0]
        orig_label = sheets_info[tname]["original_sheet_name"]
        trends.append({
            "id": "trend_2",
            "title": f"📊 各月份{orig_label}統計趨勢 (依月份遞增排序)",
            "chart_type": "clusteredColumnChart",
            "table": tname,
            "date_column": "YearMonth" if "YearMonth" in sheets_info[tname]["date_columns"] else sheets_info[tname]["columns"][0]["name"],
            "agg": "COUNTROWS",
            "value_column": sheets_info[tname]["columns"][0]["name"]
        })

    # Generate 3 Multi-Level Drill-Down Charts
    for idx in range(3):
        tname = table_names[idx % len(table_names)]
        smeta = sheets_info[tname]
        orig_label = smeta["original_sheet_name"]

        # Smart defaults if clinical columns exist
        if "RXUSEMEMO" in [c["name"] for c in smeta["columns"]]:
            levels = [c for c in ("Section_Name", "HISSYSCODENM", "Clinical_Reason_Subcategory", "RXUSEMEMO") if any(x["name"] == c for x in smeta["columns"])]
            chart_title = f"🏥 {orig_label} 科別排行 (點擊↓下鑽至開立理由)"
            vtype = "clusteredBarChart"
        elif "Drug_Pair_Display" in [c["name"] for c in smeta["columns"]]:
            levels = [c for c in ("Section_Name", "Drug_Pair_Display", "UDDMDPNAME", "UDDMDPNAME2") if any(x["name"] == c for x in smeta["columns"])]
            chart_title = f"💊 {orig_label} 科別排行 (點擊↓下鑽至藥品品項)"
            vtype = "clusteredBarChart"
        elif "Severity_Level" in [c["name"] for c in smeta["columns"]]:
            levels = [c for c in ("Severity_Level", "Normalized_Drug_Pair", "Drug_A", "Drug_B") if any(x["name"] == c for x in smeta["columns"])]
            chart_title = f"⚠️ {orig_label} 嚴重度分佈 (點擊↓下鑽至藥品品項)"
            vtype = "donutChart"
        else:
            levels = pick_best_drill_columns(smeta)
            if idx == 2 and len(levels) >= 1:
                # Shift levels on 3rd chart if single sheet so all 3 charts show distinct dimensions
                levels = levels[1:] + levels[:1]
                vtype = "donutChart"
                chart_title = f"🎯 {orig_label} - {levels[0]} 佔比分佈 (點擊↓下鑽明細)"
            else:
                if idx == 1 and len(levels) >= 2 and len(table_names) == 1:
                    levels = [levels[1], levels[0]] + levels[2:]
                vtype = "clusteredBarChart"
                chart_title = f"🏆 {orig_label} - {levels[0] if levels else '項目'} 排行 (點擊↓下鑽)"

        charts.append({
            "id": f"chart_drill_{idx+1}",
            "title": chart_title,
            "chart_type": vtype,
            "table": tname,
            "drill_columns": levels if levels else [smeta["columns"][0]["name"]],
            "agg": "COUNTROWS",
            "value_column": smeta["numeric_columns"][0] if smeta["numeric_columns"] else smeta["columns"][0]["name"]
        })

    return {
        "dashboard_title": f"{base_title} - 專業數據分析儀表板",
        "dashboard_subtitle": "支援多階層向下鑽研 (Drill-Down) ｜ 趨勢依日期遞增排序 ｜ 跨電腦相容 Power BI 報表",
        "theme": "executive_colorful",
        "exclude_months": exclude_months,
        "slicers": slicers,
        "kpis": kpis,
        "trends": trends,
        "charts": charts
    }


def parse_natural_language_request(prompt: str, inspection: dict) -> dict:
    """Translates a user's natural language prompt into a customized dashboard configuration."""
    import copy
    config = copy.deepcopy(inspection["recommended_config"])
    if not prompt or not prompt.strip():
        return config

    p = prompt.strip()
    p_lower = p.lower()

    # 1. Theme selection via natural language
    if any(k in p_lower for k in ("醫療", "綠", "teal", "清新")):
        config["theme"] = "medical_teal"
    elif any(k in p_lower for k in ("商務藍", "深藍", "sapphire", "科技")):
        config["theme"] = "modern_sapphire"
    elif any(k in p_lower for k in ("暖", "橘", "紅", "活力", "sunset")):
        config["theme"] = "warm_sunset"
    elif any(k in p_lower for k in ("多彩", "豐富", "漂亮", "colorful")):
        config["theme"] = "executive_colorful"

    # 2. Month exclusion via natural language (e.g. "去除6月", "排除 2026-06")
    for m_match in re.finditer(r"(?:排除|去除|不要|過濾|刪掉)\s*(?:(\d{4})[-/年])?(\d{1,2})月?", p):
        yr = m_match.group(1)
        mn = int(m_match.group(2))
        for ym in inspection.get("monthly_distribution", {}).keys():
            if ym.endswith(f"-{mn:02d}") and (not yr or ym.startswith(yr)):
                if ym not in config["exclude_months"]:
                    config["exclude_months"].append(ym)

    # 3. Custom title if specified
    t_match = re.search(r"標題(?:改為|設為|是)[:：\s]*([^\n，,。]+)", p)
    if t_match:
        config["dashboard_title"] = t_match.group(1).strip()

    # 4. Match column names mentioned in prompt for drill-down customization
    # Pattern like: "A下鑽到B" or "A鑽研至B"
    all_sheets = inspection["sheets"]
    for chart in config["charts"]:
        tname = chart["table"]
        smeta = all_sheets.get(tname, {})
        col_names = [c["name"] for c in smeta.get("columns", [])]

        # Specific clinical shortcut rules if mentioned
        if "重複用藥" in chart["title"] and any(k in p for k in ("理由", "原因", "備註")):
            reason_Hierarchy = [c for c in ("Section_Name", "HISSYSCODENM", "Clinical_Reason_Subcategory", "RXUSEMEMO") if c in col_names]
            if reason_Hierarchy:
                chart["drill_columns"] = reason_Hierarchy
                chart["title"] = "🏥 門診科別重複用藥排行 (點擊↓下鑽至開立理由)"
        if ("交互作用" in chart["title"] or "DDI" in chart["title"]) and any(k in p for k in ("藥品", "品項", "藥物")):
            if "Drug_Pair_Display" in col_names:
                chart["drill_columns"] = [c for c in ("Section_Name", "Drug_Pair_Display", "UDDMDPNAME", "UDDMDPNAME2") if c in col_names]
            elif "Normalized_Drug_Pair" in col_names:
                chart["drill_columns"] = [c for c in ("Severity_Level", "Normalized_Drug_Pair", "Drug_A", "Drug_B") if c in col_names]

        # Generic column matching if user says "依[欄位A]下鑽到[欄位B]"
        for c1 in col_names:
            for c2 in col_names:
                if c1 != c2 and c1 in p and c2 in p:
                    idx1 = p.find(c1)
                    idx2 = p.find(c2)
                    if 0 <= idx1 < idx2 and any(k in p[idx1:idx2+len(c2)+6] for k in ("下鑽", "鑽研", "細分", "再到", "->")):
                        new_levels = [c1, c2]
                        for c3 in col_names:
                            if c3 not in new_levels and c3 in p[idx2:]:
                                new_levels.append(c3)
                        chart["drill_columns"] = new_levels[:4]
                        chart["title"] = f"📊 {c1} 排行分析 (點擊↓下鑽至 {' ➔ '.join(new_levels[1:])})"

    return config


def build_dashboard_bundle(file_path: str, config: dict, output_dir: str, limit_top_n: int = 25) -> dict:
    """
    Executes the full pipeline:
    1. Cleans sheets, filters excluded months, creates Dim_Date.csv & cleaned UTF-8-BOM CSVs.
    2. Generates Power BI DataModelSchema + Report/Layout JSON and packages a universal v1.28 .pbit file.
    3. Generates a standalone interactive HTML Executive Dashboard (.html) with click-to-drill-down.
    """
    os.makedirs(output_dir, exist_ok=True)
    csv_dir = os.path.join(output_dir, "PowerBI_Data")
    os.makedirs(csv_dir, exist_ok=True)

    raw_sheets = load_raw_sheets(file_path)
    exclude_months = set(config.get("exclude_months", []))
    theme_key = config.get("theme", "executive_colorful")
    theme = THEMES.get(theme_key, THEMES["executive_colorful"])

    cleaned_tables = {}
    all_dates = set()

    for sname, raw_df in raw_sheets.items():
        tname = sanitize_table_name(sname)
        df = enrich_dataframe(raw_df, sname)
        if "YearMonth" in df.columns and exclude_months:
            df = df[~df["YearMonth"].isin(exclude_months)].copy()
        if "Date" in df.columns:
            valid_dates = [d for d in df["Date"].dropna().unique() if len(str(d)) == 10]
            all_dates.update(valid_dates)

        # Clean newlines in string cells so CSV imports into Power BI cleanly with QuoteStyle.Csv
        for col in df.columns:
            if df[col].dtype == object:
                df[col] = df[col].fillna("").astype(str).str.replace(r"[\r\n]+", " ", regex=True).str.strip()

        csv_path = os.path.join(csv_dir, f"{tname}.csv")
        df.to_csv(csv_path, index=False, encoding="utf-8-sig", quoting=csv.QUOTE_MINIMAL)
        cleaned_tables[tname] = {
            "df": df,
            "csv_path": csv_path,
            "original_name": sname
        }

    # Build continuous Dim_Date table sorted ascending
    if all_dates:
        min_dt = datetime.strptime(min(all_dates), "%Y-%m-%d")
        max_dt = datetime.strptime(max(all_dates), "%Y-%m-%d")
    else:
        min_dt = datetime(2026, 7, 1)
        max_dt = datetime(2026, 9, 30)

    date_rows = []
    cur = min_dt
    weekday_names = ["週一", "週二", "週三", "週四", "週五", "週六", "週日"]
    while cur <= max_dt:
        d_str = cur.strftime("%Y-%m-%d")
        roc_yr = cur.year - 1911
        date_rows.append({
            "Date": d_str,
            "ROC_Date": f"{roc_yr}{cur.strftime('%m%d')}",
            "YearMonth": cur.strftime("%Y-%m"),
            "MonthName": f"{cur.year}年{cur.month:02d}月",
            "DayOfWeek": cur.isoweekday(),
            "DayOfWeekName": weekday_names[cur.weekday()]
        })
        cur += timedelta(days=1)

    dim_date_df = pd.DataFrame(date_rows)
    dim_date_csv = os.path.join(csv_dir, "Dim_Date.csv")
    dim_date_df.to_csv(dim_date_csv, index=False, encoding="utf-8-sig")

    # Build Power BI DataModelSchema & Report Layout
    base_name = sanitize_table_name(os.path.splitext(os.path.basename(file_path))[0])
    schema_dict, measure_lookup = build_pbi_schema(cleaned_tables, dim_date_csv, config)
    layout_dict = build_pbi_layout(cleaned_tables, config, theme, measure_lookup)

    temp_build_dir = os.path.join(output_dir, "_pbi_build_temp")
    os.makedirs(temp_build_dir, exist_ok=True)
    schema_path = os.path.join(temp_build_dir, "DataModelSchema.json")
    layout_path = os.path.join(temp_build_dir, "Layout.json")

    with open(schema_path, "w", encoding="utf-8") as f:
        json.dump(schema_dict, f, ensure_ascii=False, indent=2)
    with open(layout_path, "w", encoding="utf-8") as f:
        json.dump(layout_dict, f, ensure_ascii=False, indent=2)

    pbit_path = os.path.join(output_dir, f"{base_name}_PowerBI儀表板.pbit")
    _invoke_packager_bridge({
        "Mode": "pbit",
        "SchemaPath": os.path.abspath(schema_path),
        "LayoutPath": os.path.abspath(layout_path),
        "SourcePbixPath": "",
        "OutputPath": os.path.abspath(pbit_path)
    })

    # Build Interactive HTML Dashboard
    html_path = os.path.join(output_dir, f"{base_name}_互動式網頁儀表板.html")
    html_content = build_interactive_html(cleaned_tables, dim_date_df, config, theme, limit_top_n)
    with open(html_path, "w", encoding="utf-8") as f:
        f.write(html_content)

    return {
        "status": "success",
        "pbit_path": os.path.abspath(pbit_path),
        "html_path": os.path.abspath(html_path),
        "csv_dir": os.path.abspath(csv_dir),
        "layout_json_path": os.path.abspath(layout_path),
        "tables_exported": {k: len(v["df"]) for k, v in cleaned_tables.items()},
        "date_range": f"{min_dt.strftime('%Y-%m-%d')} ~ {max_dt.strftime('%Y-%m-%d')}",
        "excluded_months": list(exclude_months)
    }


def make_m_partition(table_name: str, csv_path: str, num_cols: int) -> dict:
    escaped_path = csv_path.replace("\\", "\\\\")
    return {
        "name": table_name,
        "mode": "import",
        "source": {
            "type": "m",
            "expression": [
                "let",
                f"    Source = Csv.Document(File.Contents(\"{escaped_path}\"),[Delimiter=\",\", Columns={num_cols}, Encoding=65001, QuoteStyle=QuoteStyle.Csv]),",
                "    PromotedHeaders = Table.PromoteHeaders(Source, [PromoteAllScalars=true])",
                "in",
                "    PromotedHeaders"
            ]
        }
    }


def build_pbi_schema(cleaned_tables: dict, dim_date_csv: str, config: dict):
    """Constructs the Tabular Model DataModelSchema JSON and registers DAX measures."""
    tables_bim = [
        {
            "name": "Dim_Date",
            "columns": [
                {"name": "Date", "dataType": "string", "sourceColumn": "Date"},
                {"name": "ROC_Date", "dataType": "string", "sourceColumn": "ROC_Date"},
                {"name": "YearMonth", "dataType": "string", "sourceColumn": "YearMonth"},
                {"name": "MonthName", "dataType": "string", "sourceColumn": "MonthName"},
                {"name": "DayOfWeek", "dataType": "int64", "sourceColumn": "DayOfWeek"},
                {"name": "DayOfWeekName", "dataType": "string", "sourceColumn": "DayOfWeekName"}
            ],
            "partitions": [make_m_partition("Dim_Date", dim_date_csv, 6)]
        }
    ]

    relationships = []
    measure_lookup = {}

    for tname, tinfo in cleaned_tables.items():
        df = tinfo["df"]
        cols_bim = []
        for col in df.columns:
            col_str = str(col)
            dtype = "int64" if pd.api.types.is_integer_dtype(df[col]) else ("double" if pd.api.types.is_float_dtype(df[col]) else "string")
            cols_bim.append({"name": col_str, "dataType": dtype, "sourceColumn": col_str})

        # Create default & configured DAX measures on this table
        measures_bim = []
        default_m_name = f"{tname}_總筆數"
        measures_bim.append({
            "name": default_m_name,
            "expression": f"COUNTROWS('{tname}')",
            "formatString": "#,0"
        })
        measure_lookup[(tname, "COUNTROWS", "")] = default_m_name

        if "Is_Meaningless_Memo" in df.columns:
            m_rate = f"{tname}_無效備註率"
            measures_bim.append({
                "name": m_rate,
                "expression": f"DIVIDE(SUM('{tname}'[Is_Meaningless_Memo]), COUNTROWS('{tname}'), 0)",
                "formatString": "0.0%"
            })
            measure_lookup[(tname, "MEANINGLESS_RATE", "Is_Meaningless_Memo")] = m_rate

        # Register any KPI / chart specific measures
        for item in config.get("kpis", []) + config.get("trends", []) + config.get("charts", []):
            if item.get("table") != tname:
                continue
            agg = item.get("agg", "COUNTROWS")
            col = item.get("column") or item.get("value_column") or ""
            key = (tname, agg, col)
            if key in measure_lookup:
                continue
            if agg == "COUNTROWS":
                measure_lookup[key] = default_m_name
            elif agg == "DISTINCTCOUNT" and col in df.columns:
                m_name = f"{tname}_{col}_不重複數"
                measures_bim.append({
                    "name": m_name,
                    "expression": f"DISTINCTCOUNT('{tname}'[{col}])",
                    "formatString": "#,0"
                })
                measure_lookup[key] = m_name
            elif agg == "SUM" and col in df.columns:
                m_name = f"{tname}_{col}_加總"
                measures_bim.append({
                    "name": m_name,
                    "expression": f"SUM('{tname}'[{col}])",
                    "formatString": "#,0.##"
                })
                measure_lookup[key] = m_name
            elif agg == "AVERAGE" and col in df.columns:
                m_name = f"{tname}_{col}_平均"
                measures_bim.append({
                    "name": m_name,
                    "expression": f"AVERAGE('{tname}'[{col}])",
                    "formatString": "#,0.00"
                })
                measure_lookup[key] = m_name
            else:
                measure_lookup[key] = default_m_name

        tables_bim.append({
            "name": tname,
            "columns": cols_bim,
            "partitions": [make_m_partition(tname, tinfo["csv_path"], len(cols_bim))],
            "measures": measures_bim
        })

        if "Date" in df.columns:
            relationships.append({
                "name": f"Rel_{tname}_Dim_Date",
                "fromTable": tname,
                "fromColumn": "Date",
                "toTable": "Dim_Date",
                "toColumn": "Date",
                "crossFilteringBehavior": "oneDirection"
            })

    schema = {
        "name": "SemanticModel",
        "compatibilityLevel": 1567,
        "model": {
            "culture": "zh-TW",
            "dataAccessOptions": {"legacyRedirects": True, "returnErrorValuesAsNull": True},
            "defaultPowerBIDataSourceVersion": "powerBI_V3",
            "tables": tables_bim,
            "relationships": relationships
        }
    }
    return schema, measure_lookup


def build_pbi_layout(cleaned_tables: dict, config: dict, theme: dict, measure_lookup: dict) -> dict:
    """Builds the standard v1.28 Report/Layout JSON with banner, slicers, KPIs, trends, and drill-down visuals."""
    visuals = []

    # 1. Top Banner
    banner_cfg = {
        "name": "banner_top",
        "layouts": [{"id": 0, "position": {"x": 0, "y": 0, "z": 0, "width": 1280, "height": 54, "tabOrder": 0}}],
        "singleVisual": {
            "visualType": "textbox",
            "objects": {
                "general": [{
                    "properties": {
                        "paragraphs": [{
                            "textRuns": [
                                {
                                    "value": f"📊 {config.get('dashboard_title', '專業數據分析儀表板')}   ",
                                    "textStyle": {"fontWeight": "bold", "fontFamily": "Segoe UI", "fontSize": "16pt", "color": "#FFFFFF"}
                                },
                                {
                                    "value": f"｜  {config.get('dashboard_subtitle', '')}",
                                    "textStyle": {"fontWeight": "normal", "fontFamily": "Segoe UI", "fontSize": "10.5pt", "color": theme["banner_sub"]}
                                }
                            ]
                        }]
                    }
                }]
            },
            "vcObjects": {
                "background": [{"properties": {
                    "show": {"expr": {"Literal": {"Value": "true"}}},
                    "color": {"solid": {"color": {"expr": {"Literal": {"Value": f"'{theme['banner_bg']}'"}}}}}
                }}],
                "border": [{"properties": {"show": {"expr": {"Literal": {"Value": "false"}}}}}
            ]}
        }
    }
    visuals.append({"x": 0, "y": 0, "z": 0, "width": 1280, "height": 54, "config": json.dumps(banner_cfg, ensure_ascii=False), "filters": "[]"})

    # 2. Slicers (top-left)
    slicers = config.get("slicers", [])[:2]
    sx = 16
    for idx, sl in enumerate(slicers):
        sw = 215 if len(slicers) > 1 else 440
        sl_table = sl["table"]
        sl_col = sl["column"]
        sl_title = sl["title"]
        sl_cfg = {
            "name": f"slicer_{idx+1}",
            "layouts": [{"id": 0, "position": {"x": sx, "y": 60, "z": idx + 1, "width": sw, "height": 88, "tabOrder": idx + 1}}],
            "singleVisual": {
                "visualType": "slicer",
                "projections": {"Values": [{"queryRef": f"{sl_table}.{sl_col}", "active": True}]},
                "prototypeQuery": {
                    "Version": 2,
                    "From": [{"Name": "t", "Entity": sl_table, "Type": 0}],
                    "Select": [{"Column": {"Expression": {"SourceRef": {"Source": "t"}}, "Property": sl_col}, "Name": f"{sl_table}.{sl_col}"}]
                },
                "objects": {
                    "data": [{"properties": {"mode": {"expr": {"Literal": {"Value": "'Dropdown'"}}}}}],
                    "header": [{"properties": {
                        "show": {"expr": {"Literal": {"Value": "true"}}},
                        "text": {"expr": {"Literal": {"Value": f"'{sl_title}'"}}},
                        "fontColor": {"solid": {"color": {"expr": {"Literal": {"Value": f"'{theme['chart_headers'][idx % len(theme['chart_headers'])]}'"}}}}},
                        "fontSize": {"expr": {"Literal": {"Value": "10D"}}}
                    }}]
                },
                "vcObjects": {
                    "background": [{"properties": {"show": {"expr": {"Literal": {"Value": "true"}}}, "color": {"solid": {"color": {"expr": {"Literal": {"Value": "'#FFFFFF'"}}}}}}}],
                    "border": [{"properties": {"show": {"expr": {"Literal": {"Value": "true"}}}, "color": {"solid": {"color": {"expr": {"Literal": {"Value": "'#94A3B8'"}}}}}, "radius": {"expr": {"Literal": {"Value": "8D"}}}}}]
                }
            }
        }
        visuals.append({"x": sx, "y": 60, "z": idx + 1, "width": sw, "height": 88, "config": json.dumps(sl_cfg, ensure_ascii=False), "filters": "[]"})
        sx += sw + 12

    # 3. 4 Colorful KPI Cards (top-right)
    kpis = config.get("kpis", [])[:4]
    kx_start = 475 if slicers else 16
    total_kw = 1264 - kx_start
    kw = int((total_kw - (len(kpis) - 1) * 10) / max(len(kpis), 1))
    for idx, kpi in enumerate(kpis):
        kx = kx_start + idx * (kw + 10)
        ktable = kpi["table"]
        kagg = kpi.get("agg", "COUNTROWS")
        kcol = kpi.get("column", "")
        m_name = measure_lookup.get((ktable, kagg, kcol)) or measure_lookup.get((ktable, "COUNTROWS", ""))
        kstyle = theme["kpi_styles"][idx % len(theme["kpi_styles"])]
        card_cfg = {
            "name": f"kpi_card_{idx+1}",
            "layouts": [{"id": 0, "position": {"x": kx, "y": 60, "z": 5 + idx, "width": kw, "height": 88, "tabOrder": 5 + idx}}],
            "singleVisual": {
                "visualType": "card",
                "projections": {"Values": [{"queryRef": f"{ktable}.{m_name}"}]},
                "prototypeQuery": {
                    "Version": 2,
                    "From": [{"Name": "t", "Entity": ktable, "Type": 0}],
                    "Select": [{"Measure": {"Expression": {"SourceRef": {"Source": "t"}}, "Property": m_name}, "Name": f"{ktable}.{m_name}"}]
                },
                "objects": {
                    "labels": [{"properties": {
                        "color": {"solid": {"color": {"expr": {"Literal": {"Value": f"'{kstyle['callout']}'"}}}}},
                        "fontSize": {"expr": {"Literal": {"Value": "23D"}}},
                        "fontFamily": {"expr": {"Literal": {"Value": "'Segoe UI Semibold'"}}}
                    }}],
                    "categoryLabels": [{"properties": {"show": {"expr": {"Literal": {"Value": "false"}}}}}]
                },
                "vcObjects": {
                    "title": [{"properties": {
                        "show": {"expr": {"Literal": {"Value": "true"}}},
                        "text": {"expr": {"Literal": {"Value": f"'{kpi['title']}'"}}},
                        "fontSize": {"expr": {"Literal": {"Value": "11D"}}},
                        "fontColor": {"solid": {"color": {"expr": {"Literal": {"Value": "'#FFFFFF'"}}}}},
                        "background": {"solid": {"color": {"expr": {"Literal": {"Value": f"'{kstyle['title_bg']}'"}}}}},
                        "alignment": {"expr": {"Literal": {"Value": "'center'"}}}
                    }}],
                    "background": [{"properties": {"show": {"expr": {"Literal": {"Value": "true"}}}, "color": {"solid": {"color": {"expr": {"Literal": {"Value": f"'{kstyle['card_bg']}'"}}}}}}}],
                    "border": [{"properties": {"show": {"expr": {"Literal": {"Value": "true"}}}, "color": {"solid": {"color": {"expr": {"Literal": {"Value": f"'{kstyle['border']}'"}}}}}, "radius": {"expr": {"Literal": {"Value": "10D"}}}, "width": {"expr": {"Literal": {"Value": "2D"}}}}}],
                    "dropShadow": [{"properties": {"show": {"expr": {"Literal": {"Value": "true"}}}, "color": {"solid": {"color": {"expr": {"Literal": {"Value": "'#CBD5E1'"}}}}}, "position": {"expr": {"Literal": {"Value": "'Outer'"}}}}}]
                }
            }
        }
        visuals.append({"x": kx, "y": 60, "z": 5 + idx, "width": kw, "height": 88, "config": json.dumps(card_cfg, ensure_ascii=False), "filters": "[]"})

    # 4. Middle Row: Chronological Trend Visuals (Direction: 1 = Ascending by Date)
    trends = config.get("trends", [])[:2]
    tw = int((1248 - (len(trends) - 1) * 12) / max(len(trends), 1))
    for idx, tr in enumerate(trends):
        tx = 16 + idx * (tw + 12)
        ttable = tr["table"]
        tcol = tr.get("date_column", "Date")
        date_entity = "Dim_Date" if tcol in ("Date", "YearMonth") else ttable
        m_name = measure_lookup.get((ttable, tr.get("agg", "COUNTROWS"), tr.get("value_column", ""))) or measure_lookup.get((ttable, "COUNTROWS", ""))
        hdr_bg = theme["chart_headers"][(idx + 1) % len(theme["chart_headers"])]
        line_col = theme["data_colors"][idx % len(theme["data_colors"])]
        vtype = tr.get("chart_type", "areaChart")

        tr_cfg = {
            "name": f"trend_visual_{idx+1}",
            "layouts": [{"id": 0, "position": {"x": tx, "y": 158, "z": 10 + idx, "width": tw, "height": 252, "tabOrder": 10 + idx}}],
            "singleVisual": {
                "visualType": vtype,
                "projections": {
                    "Category": [{"queryRef": f"{date_entity}.{tcol}", "active": True}],
                    "Y": [{"queryRef": f"{ttable}.{m_name}"}]
                },
                "prototypeQuery": {
                    "Version": 2,
                    "From": [{"Name": "c", "Entity": date_entity, "Type": 0}, {"Name": "v", "Entity": ttable, "Type": 0}] if date_entity != ttable else [{"Name": "c", "Entity": ttable, "Type": 0}],
                    "Select": [
                        {"Column": {"Expression": {"SourceRef": {"Source": "c"}}, "Property": tcol}, "Name": f"{date_entity}.{tcol}"},
                        {"Measure": {"Expression": {"SourceRef": {"Source": "v" if date_entity != ttable else "c"}}, "Property": m_name}, "Name": f"{ttable}.{m_name}"}
                    ],
                    "OrderBy": [{"Direction": 1, "Expression": {"Column": {"Expression": {"SourceRef": {"Source": "c"}}, "Property": tcol}}}]
                },
                "objects": {
                    "dataPoint": [{"properties": {"fill": {"solid": {"color": {"expr": {"Literal": {"Value": f"'{line_col}'"}}}}}}}],
                    "labels": [{"properties": {"show": {"expr": {"Literal": {"Value": "true"}}}, "color": {"solid": {"color": {"expr": {"Literal": {"Value": "'#334155'"}}}}}}}]
                },
                "vcObjects": {
                    "title": [{"properties": {
                        "show": {"expr": {"Literal": {"Value": "true"}}},
                        "text": {"expr": {"Literal": {"Value": f"'{tr['title']}'"}}},
                        "fontSize": {"expr": {"Literal": {"Value": "11.5D"}}},
                        "fontColor": {"solid": {"color": {"expr": {"Literal": {"Value": "'#FFFFFF'"}}}}},
                        "background": {"solid": {"color": {"expr": {"Literal": {"Value": f"'{hdr_bg}'"}}}}}
                    }}],
                    "background": [{"properties": {"show": {"expr": {"Literal": {"Value": "true"}}}, "color": {"solid": {"color": {"expr": {"Literal": {"Value": "'#FFFFFF'"}}}}}}}],
                    "border": [{"properties": {"show": {"expr": {"Literal": {"Value": "true"}}}, "color": {"solid": {"color": {"expr": {"Literal": {"Value": "'#CBD5E1'"}}}}}, "radius": {"expr": {"Literal": {"Value": "10D"}}}}}],
                    "dropShadow": [{"properties": {"show": {"expr": {"Literal": {"Value": "true"}}}, "color": {"solid": {"color": {"expr": {"Literal": {"Value": "'#CBD5E1'"}}}}}, "position": {"expr": {"Literal": {"Value": "'Outer'"}}}}}]
                }
            }
        }
        visuals.append({"x": tx, "y": 158, "z": 10 + idx, "width": tw, "height": 252, "config": json.dumps(tr_cfg, ensure_ascii=False), "filters": "[]"})

    # 5. Bottom Row: 3 Multi-Level Drill-Down Visuals
    charts = config.get("charts", [])[:3]
    cw = int((1248 - (len(charts) - 1) * 12) / max(len(charts), 1))
    for idx, ch in enumerate(charts):
        cx = 16 + idx * (cw + 12)
        ctable = ch["table"]
        drill_cols = ch.get("drill_columns", [])
        if not drill_cols:
            drill_cols = [list(cleaned_tables[ctable]["df"].columns)[0]]
        m_name = measure_lookup.get((ctable, ch.get("agg", "COUNTROWS"), ch.get("value_column", ""))) or measure_lookup.get((ctable, "COUNTROWS", ""))
        vtype = ch.get("chart_type", "clusteredBarChart")
        hdr_bg = theme["chart_headers"][idx % len(theme["chart_headers"])]
        bar_col = theme["data_colors"][idx % len(theme["data_colors"])]

        cat_proj = []
        select_clauses = []
        for l_idx, dcol in enumerate(drill_cols):
            qref = f"{ctable}.{dcol}"
            cat_proj.append({"queryRef": qref, "active": True if l_idx == 0 else False})
            select_clauses.append({"Column": {"Expression": {"SourceRef": {"Source": "t"}}, "Property": dcol}, "Name": qref})
        select_clauses.append({"Measure": {"Expression": {"SourceRef": {"Source": "t"}}, "Property": m_name}, "Name": f"{ctable}.{m_name}"})

        vis_objs = {
            "labels": [{"properties": {"show": {"expr": {"Literal": {"Value": "true"}}}, "color": {"solid": {"color": {"expr": {"Literal": {"Value": "'#1E293B'"}}}}}}}]
        }
        if vtype not in ("donutChart", "pieChart"):
            vis_objs["dataPoint"] = [{"properties": {"fill": {"solid": {"color": {"expr": {"Literal": {"Value": f"'{bar_col}'"}}}}}}}]

        ch_cfg = {
            "name": f"drill_visual_{idx+1}",
            "layouts": [{"id": 0, "position": {"x": cx, "y": 420, "z": 15 + idx, "width": cw, "height": 286, "tabOrder": 15 + idx}}],
            "singleVisual": {
                "visualType": vtype,
                "projections": {
                    "Category": cat_proj,
                    "Y": [{"queryRef": f"{ctable}.{m_name}"}]
                },
                "prototypeQuery": {
                    "Version": 2,
                    "From": [{"Name": "t", "Entity": ctable, "Type": 0}],
                    "Select": select_clauses,
                    "OrderBy": [{"Direction": 2, "Expression": {"Measure": {"Expression": {"SourceRef": {"Source": "t"}}, "Property": m_name}}}]
                },
                "objects": vis_objs,
                "vcObjects": {
                    "title": [{"properties": {
                        "show": {"expr": {"Literal": {"Value": "true"}}},
                        "text": {"expr": {"Literal": {"Value": f"'{ch['title']}'"}}},
                        "fontSize": {"expr": {"Literal": {"Value": "11.5D"}}},
                        "fontColor": {"solid": {"color": {"expr": {"Literal": {"Value": "'#FFFFFF'"}}}}},
                        "background": {"solid": {"color": {"expr": {"Literal": {"Value": f"'{hdr_bg}'"}}}}}
                    }}],
                    "background": [{"properties": {"show": {"expr": {"Literal": {"Value": "true"}}}, "color": {"solid": {"color": {"expr": {"Literal": {"Value": "'#FFFFFF'"}}}}}}}],
                    "border": [{"properties": {"show": {"expr": {"Literal": {"Value": "true"}}}, "color": {"solid": {"color": {"expr": {"Literal": {"Value": "'#CBD5E1'"}}}}}, "radius": {"expr": {"Literal": {"Value": "10D"}}}}}],
                    "dropShadow": [{"properties": {"show": {"expr": {"Literal": {"Value": "true"}}}, "color": {"solid": {"color": {"expr": {"Literal": {"Value": "'#CBD5E1'"}}}}}, "position": {"expr": {"Literal": {"Value": "'Outer'"}}}}}]
                }
            }
        }
        visuals.append({"x": cx, "y": 420, "z": 15 + idx, "width": cw, "height": 286, "config": json.dumps(ch_cfg, ensure_ascii=False), "filters": "[]"})

    return {
        "config": json.dumps({
            "version": "5.53",
            "themeCollection": {"baseTheme": {"name": "CY24SU06", "version": "5.53", "type": 2}},
            "activeSectionIndex": 0,
            "defaultDrillFilterOtherVisuals": True
        }, ensure_ascii=False),
        "layoutOptimization": 0,
        "resourcePackages": [],
        "sections": [
            {
                "name": "ReportSection1",
                "displayName": "數據品質與下鑽分析總覽",
                "filters": "[]",
                "ordinal": 0,
                "visualContainers": visuals,
                "config": json.dumps({
                    "objects": {
                        "background": [{"properties": {
                            "color": {"solid": {"color": {"expr": {"Literal": {"Value": f"'{theme['canvas_bg']}'"}}}}},
                            "transparency": {"expr": {"Literal": {"Value": "15D"}}}
                        }}]
                    }
                }),
                "displayOption": 1,
                "width": 1280,
                "height": 720
            }
        ]
    }


def compute_agg(df: pd.DataFrame, agg: str, col: str):
    if len(df) == 0:
        return 0
    if agg == "COUNTROWS":
        return int(len(df))
    if agg == "DISTINCTCOUNT" and col in df.columns:
        return int(df[col].nunique())
    if agg == "SUM" and col in df.columns:
        return float(pd.to_numeric(df[col], errors="coerce").fillna(0).sum())
    if agg == "AVERAGE" and col in df.columns:
        return round(float(pd.to_numeric(df[col], errors="coerce").fillna(0).mean()), 2)
    if agg == "MEANINGLESS_RATE" and "Is_Meaningless_Memo" in df.columns:
        return round(float(df["Is_Meaningless_Memo"].sum()) / len(df) * 100, 1)
    return int(len(df))


def build_nested_drill_tree(df: pd.DataFrame, drill_cols: list, agg: str, val_col: str, top_n: int = 20, depth: int = 0) -> list:
    if not drill_cols or depth >= len(drill_cols) or len(df) == 0:
        return []
    col = drill_cols[depth]
    if col not in df.columns:
        return []
    grouped = []
    for k, grp in df.groupby(col, dropna=False):
        label = str(k).strip() if pd.notna(k) and str(k).strip() else "(未填/空白)"
        val = compute_agg(grp, agg, val_col)
        node = {"label": label[:45], "value": val}
        if depth + 1 < len(drill_cols):
            node["children"] = build_nested_drill_tree(grp, drill_cols, agg, val_col, top_n, depth + 1)
        grouped.append(node)
    grouped.sort(key=lambda x: x["value"], reverse=True)
    return grouped[:top_n]


def build_interactive_html(cleaned_tables: dict, dim_date_df: pd.DataFrame, config: dict, theme: dict, top_n: int = 20) -> str:
    """Generates a standalone, offline-ready HTML Executive Dashboard with click-to-drill-down."""
    kpi_results = []
    for idx, kpi in enumerate(config.get("kpis", [])[:4]):
        df = cleaned_tables[kpi["table"]]["df"]
        agg = kpi.get("agg", "COUNTROWS")
        val = compute_agg(df, agg, kpi.get("column", ""))
        val_str = f"{val}%" if agg == "MEANINGLESS_RATE" else f"{val:,}"
        kstyle = theme["kpi_styles"][idx % len(theme["kpi_styles"])]
        kpi_results.append({
            "title": kpi["title"],
            "value": val_str,
            "style": kstyle
        })

    trend_results = []
    for idx, tr in enumerate(config.get("trends", [])[:2]):
        df = cleaned_tables[tr["table"]]["df"]
        dcol = tr.get("date_column", "Date")
        if dcol not in df.columns and "Date" in df.columns:
            dcol = "Date"
        if dcol in df.columns:
            grp = df[df[dcol] != ""].groupby(dcol)
            pts = sorted([(str(k), compute_agg(g, tr.get("agg", "COUNTROWS"), tr.get("value_column", ""))) for k, g in grp], key=lambda x: x[0])
        else:
            pts = []
        trend_results.append({
            "id": f"trend_canvas_{idx}",
            "title": tr["title"],
            "chart_type": "bar" if "Column" in tr.get("chart_type", "") else "line",
            "labels": [p[0] for p in pts],
            "values": [p[1] for p in pts],
            "header_bg": theme["chart_headers"][(idx + 1) % len(theme["chart_headers"])],
            "color": theme["data_colors"][idx % len(theme["data_colors"])]
        })

    drill_results = []
    for idx, ch in enumerate(config.get("charts", [])[:3]):
        df = cleaned_tables[ch["table"]]["df"]
        dcols = [c for c in ch.get("drill_columns", []) if c in df.columns]
        if not dcols and len(df.columns) > 0:
            dcols = [str(df.columns[0])]
        tree = build_nested_drill_tree(df, dcols, ch.get("agg", "COUNTROWS"), ch.get("value_column", ""), top_n)
        drill_results.append({
            "id": f"drill_canvas_{idx}",
            "title": ch["title"],
            "chart_type": "doughnut" if "donut" in ch.get("chart_type", "").lower() else "bar",
            "drill_columns": dcols,
            "tree": tree,
            "header_bg": theme["chart_headers"][idx % len(theme["chart_headers"])],
            "color": theme["data_colors"][idx % len(theme["data_colors"])]
        })

    payload_json = json.dumps({
        "title": config.get("dashboard_title", "專業數據分析儀表板"),
        "subtitle": config.get("dashboard_subtitle", ""),
        "theme": theme,
        "kpis": kpi_results,
        "trends": trend_results,
        "drills": drill_results
    }, ensure_ascii=False)

    return f"""<!DOCTYPE html>
<html lang="zh-TW">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{config.get('dashboard_title', 'Power BI 互動式儀表板')}</title>
<script src="https://cdn.jsdelivr.net/npm/chart.js@4.4.1/dist/chart.umd.min.js"></script>
<style>
  * {{ box-sizing: border-box; margin: 0; padding: 0; font-family: 'Segoe UI', 'Microsoft JhengHei', sans-serif; }}
  body {{ background: {theme['canvas_bg']}; color: #0F172A; padding-bottom: 32px; }}
  .banner {{ background: {theme['banner_bg']}; color: #fff; padding: 16px 28px; display: flex; align-items: center; justify-content: space-between; box-shadow: 0 4px 12px rgba(0,0,0,0.15); }}
  .banner h1 {{ font-size: 21px; font-weight: 700; letter-spacing: 0.5px; }}
  .banner .sub {{ color: {theme['banner_sub']}; font-size: 13px; margin-top: 4px; }}
  .container {{ max-width: 1440px; margin: 18px auto; padding: 0 20px; display: flex; flex-direction: column; gap: 18px; }}
  .kpi-grid {{ display: grid; grid-template-columns: repeat(4, 1fr); gap: 14px; }}
  .kpi-card {{ border-radius: 12px; overflow: hidden; box-shadow: 0 4px 10px rgba(15,23,42,0.08); border: 2px solid #cbd5e1; text-align: center; }}
  .kpi-hdr {{ color: #fff; font-size: 13px; font-weight: 600; padding: 8px 12px; }}
  .kpi-val {{ font-size: 30px; font-weight: 800; padding: 16px 12px; }}
  .trend-grid {{ display: grid; grid-template-columns: repeat(2, 1fr); gap: 16px; }}
  .drill-grid {{ display: grid; grid-template-columns: repeat(3, 1fr); gap: 16px; }}
  .card {{ background: #fff; border-radius: 12px; overflow: hidden; border: 1px solid #cbd5e1; box-shadow: 0 4px 12px rgba(15,23,42,0.07); display: flex; flex-direction: column; }}
  .card-hdr {{ color: #fff; padding: 10px 14px; font-size: 14px; font-weight: 700; display: flex; justify-content: space-between; align-items: center; gap: 8px; }}
  .drill-bar {{ background: #F8FAFC; border-bottom: 1px solid #E2E8F0; padding: 6px 14px; font-size: 12px; color: #475569; display: flex; justify-content: space-between; align-items: center; }}
  .btn-up {{ background: #1E40AF; color: #fff; border: none; border-radius: 6px; padding: 3px 10px; font-size: 11.5px; cursor: pointer; font-weight: 600; display: none; }}
  .btn-up:hover {{ opacity: 0.9; }}
  .canvas-wrap {{ padding: 12px; height: 290px; position: relative; }}
  @media (max-width: 1024px) {{ .kpi-grid, .trend-grid, .drill-grid {{ grid-template-columns: 1fr; }} }}
</style>
</head>
<body>
  <div class="banner">
    <div>
      <h1 id="main-title"></h1>
      <div class="sub" id="main-sub"></div>
    </div>
    <div style="font-size:12px;background:rgba(255,255,255,0.15);padding:6px 12px;border-radius:99px;">
      💡 點擊下方排行榜或環圈圖任一項目，即可自動向下鑽研 (Drill-Down)
    </div>
  </div>
  <div class="container">
    <div class="kpi-grid" id="kpi-container"></div>
    <div class="trend-grid" id="trend-container"></div>
    <div class="drill-grid" id="drill-container"></div>
  </div>
<script>
const DATA = {payload_json};
document.getElementById('main-title').textContent = '📊 ' + DATA.title;
document.getElementById('main-sub').textContent = DATA.subtitle;

const kpiBox = document.getElementById('kpi-container');
DATA.kpis.forEach(k => {{
  const el = document.createElement('div');
  el.className = 'kpi-card';
  el.style.background = k.style.card_bg;
  el.style.borderColor = k.style.border;
  el.innerHTML = `<div class="kpi-hdr" style="background:${{k.style.title_bg}}">${{k.title}}</div>
                  <div class="kpi-val" style="color:${{k.style.callout}}">${{k.value}}</div>`;
  kpiBox.appendChild(el);
}});

const trendBox = document.getElementById('trend-container');
DATA.trends.forEach(t => {{
  const el = document.createElement('div');
  el.className = 'card';
  el.innerHTML = `<div class="card-hdr" style="background:${{t.header_bg}}"><span>${{t.title}}</span></div>
                  <div class="canvas-wrap"><canvas id="${{t.id}}"></canvas></div>`;
  trendBox.appendChild(el);
  new Chart(document.getElementById(t.id), {{
    type: t.chart_type,
    data: {{
      labels: t.labels,
      datasets: [{{
        label: '數量',
        data: t.values,
        borderColor: t.color,
        backgroundColor: t.chart_type === 'line' ? t.color + '28' : t.color,
        fill: t.chart_type === 'line',
        tension: 0.25,
        pointRadius: 3
      }}]
    }},
    options: {{
      responsive: true,
      maintainAspectRatio: false,
      plugins: {{ legend: {{ display: false }} }},
      scales: {{ x: {{ ticks: {{ maxRotation: 45, font: {{ size: 11 }} }} }} }}
    }}
  }});
}});

const drillBox = document.getElementById('drill-container');
DATA.drills.forEach((d, idx) => {{
  const el = document.createElement('div');
  el.className = 'card';
  el.innerHTML = `
    <div class="card-hdr" style="background:${{d.header_bg}}">
      <span>${{d.title}}</span>
    </div>
    <div class="drill-bar">
      <span id="crumb_${{idx}}">階層 1：${{d.drill_columns[0] || ''}}</span>
      <button class="btn-up" id="btn_up_${{idx}}">⬆ 返回上一層</button>
    </div>
    <div class="canvas-wrap"><canvas id="${{d.id}}"></canvas></div>`;
  drillBox.appendChild(el);

  let stack = [{{ nodes: d.tree, levelName: d.drill_columns[0] || '項目', path: [] }}];
  const ctx = document.getElementById(d.id);
  let chartInst = null;

  function renderLevel() {{
    const cur = stack[stack.length - 1];
    const crumbEl = document.getElementById('crumb_' + idx);
    const btnUp = document.getElementById('btn_up_' + idx);
    const colLabel = d.drill_columns[stack.length - 1] || '';
    crumbEl.textContent = stack.length === 1
      ? `目前階層：${{colLabel}} (共 ${{ d.drill_columns.join(' ➔ ') }})`
      : `路徑：${{cur.path.join(' ➔ ')}} (${{colLabel}})`;
    btnUp.style.display = stack.length > 1 ? 'inline-block' : 'none';

    const labels = cur.nodes.map(n => n.label);
    const vals = cur.nodes.map(n => n.value);
    const palette = DATA.theme.data_colors;

    if (chartInst) chartInst.destroy();
    chartInst = new Chart(ctx, {{
      type: d.chart_type,
      data: {{
        labels: labels,
        datasets: [{{
          data: vals,
          backgroundColor: d.chart_type === 'doughnut'
            ? labels.map((_, i) => palette[i % palette.length])
            : palette[(idx + stack.length - 1) % palette.length],
          borderRadius: d.chart_type === 'bar' ? 5 : 0
        }}]
      }},
      options: {{
        indexAxis: d.chart_type === 'bar' ? 'y' : 'x',
        responsive: true,
        maintainAspectRatio: false,
        onClick: (evt, elements) => {{
          if (!elements || !elements.length) return;
          const clickedNode = cur.nodes[elements[0].index];
          if (clickedNode && clickedNode.children && clickedNode.children.length > 0) {{
            stack.push({{
              nodes: clickedNode.children,
              path: [...cur.path, clickedNode.label]
            }});
            renderLevel();
          }}
        }},
        plugins: {{
          legend: {{ display: d.chart_type === 'doughnut', position: 'right', labels: {{ boxWidth: 11, font: {{ size: 11 }} }} }},
          tooltip: {{
            callbacks: {{
              afterLabel: (context) => {{
                const node = cur.nodes[context.dataIndex];
                return (node && node.children && node.children.length) ? '👉 點擊向下鑽研下一層' : '（已達最底層明細）';
              }}
            }}
          }}
        }}
      }}
    }});
  }}

  document.getElementById('btn_up_' + idx).addEventListener('click', () => {{
    if (stack.length > 1) {{
      stack.pop();
      renderLevel();
    }}
  }});

  renderLevel();
}});
</script>
</body>
</html>"""


def _invoke_packager_bridge(job_dict: dict):
    temp_dir = os.environ.get("TEMP", ".")
    src_bridge = os.path.join(os.path.dirname(os.path.abspath(__file__)), "packager_bridge.ps1")
    temp_bridge = os.path.join(temp_dir, f"pbi_packager_bridge_{os.getpid()}.ps1")
    temp_job = os.path.join(temp_dir, f"pbi_pack_job_{os.getpid()}.json")
    shutil.copy2(src_bridge, temp_bridge)
    with open(temp_job, "w", encoding="utf-8") as f:
        json.dump(job_dict, f, ensure_ascii=False, indent=2)
    try:
        proc = subprocess.run([
            "powershell.exe", "-NoProfile", "-ExecutionPolicy", "Bypass",
            "-File", temp_bridge,
            "-JobJsonPath", temp_job
        ], capture_output=True, text=True)
        if proc.returncode != 0:
            raise RuntimeError(f"Power BI 封裝器執行失敗: {proc.stderr or proc.stdout}")
    finally:
        for p in (temp_bridge, temp_job):
            if os.path.exists(p):
                try:
                    os.remove(p)
                except OSError:
                    pass


def repack_pbix_cross_pc(source_pbix: str, layout_json_path: str, output_pbix: str) -> dict:
    """Repackages a saved .pbix into a universal v1.28 cross-PC compatible .pbix with embedded DataModel."""
    if not os.path.exists(source_pbix):
        raise FileNotFoundError(f"找不到來源 PBIX 檔案: {source_pbix}")
    _invoke_packager_bridge({
        "Mode": "repack_pbix",
        "SchemaPath": "",
        "LayoutPath": os.path.abspath(layout_json_path),
        "SourcePbixPath": os.path.abspath(source_pbix),
        "OutputPath": os.path.abspath(output_pbix)
    })
    return {
        "status": "success",
        "source_pbix": os.path.abspath(source_pbix),
        "compatible_pbix": os.path.abspath(output_pbix),
        "size_bytes": os.path.getsize(output_pbix)
    }
