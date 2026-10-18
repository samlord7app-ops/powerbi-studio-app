# 📊 Power BI Studio App — 雲端與本機雙棲智慧儀表板自動生成系統

🌐 **線上隨時隨地使用 (GitHub Pages 免安裝網頁版 APP)**：  
👉 **[https://samlord7app-ops.github.io/powerbi-studio-app/](https://samlord7app-ops.github.io/powerbi-studio-app/)**

---

## ✨ 系統特色

1. **🔒 100% 醫療與企業資安保障（純瀏覽器端運算）**
   * 線上網頁版採用 `SheetJS` 在您的瀏覽器本機記憶體內直接解析 Excel (`.xlsx` / `.xls` / `.csv`)，**資料絕不外傳至任何外部伺服器**。
2. **🧠 智慧資料品質診斷與異常過濾**
   * 自動將民國 7 碼日期（如 `1150701`）與西元日期統一標準化為 `YYYY-MM-DD`。
   * 自動偵測異常稀疏月份（例如佔比 `<2%` 的跨期殘留資料），提供一鍵勾選排除。
   * 內建醫院門診科別代碼 (`OPDSECTION`)、重複用藥原因備註品質 (`RXUSEMEMO`) 與中西藥交互作用 (`DDI`) 智慧分類字典。
3. **💬 自然語言指令 ＋ 🎛️ 視覺化多階層下鑽設定器**
   * 可直接打字輸入分析需求（例如：*「排除6月資料，門診科別重複用藥排行下鑽到開立理由，交互作用下鑽到藥品品項」*）。
   * 支援 **第 1 層 ➔ 第 2 層 ➔ 第 3 層 ➔ 第 4 層點擊向下鑽研 (Drill-Down)**。
   * 趨勢圖強制綁定日期維度並依 **日期遞增排序 (Chronological Ascending)**。
4. **🎨 4 款專業豐富配色主題**
   * `Executive Colorful 專業多彩風`、`Medical Teal & Coral 醫療品質風`、`Modern Sapphire 現代商務藍`、`Warm Sunset 暖陽活力風`。
5. **📦 多格式一鍵匯出**
   * **雲端網頁版**：一鍵下載「獨立互動式網頁儀表板 (`.html`)」與「Power BI 完整清理後 CSV 資料與配色主題包 (`.zip`)」。
   * **本機完整版**：雙擊 `啟動_PowerBI_自動生成APP.bat` 即可直接呼叫本機 `Microsoft.PowerBI.Packaging.dll` 封裝跨電腦相容之 `v1.28` `.pbit` 與 `.pbix` 原生檔案！

---

## 🚀 使用方式

### 方式 A：隨時隨地開啟線上版 (免安裝)
直接點擊上方 **GitHub Pages 網址**，將任何 Excel 檔案拖曳進網頁即可立即產生互動式下鑽儀表板！

### 方式 B：下載至電腦執行本機完整版 (支援直接產出 `.pbit` / `.pbix`)
```powershell
git clone https://github.com/samlord7app-ops/powerbi-studio-app.git
cd powerbi-studio-app
.\啟動_PowerBI_自動生成APP.bat
```
