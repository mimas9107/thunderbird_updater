---
name:             "CHANGELOG.md"
description:      "版本變更日誌"
created_date:     "2026/05/12"
modified_date:    "2026/05/13"
project_version:  "1.2.0"
document_version: "1.2.0"
agent_sign:       ['human/justin', 'gemini cli/2.0.0']
---

# Changelog

All notable changes to this project will be documented in this file.

## [1.2.0] - 2026-05-13

### Added
- Download cache 機制：同版本不再重複下載
- `--cache-dir` 參數：自訂 cache 目錄（預設 `./download_cache/`）
- `--no-cache` 參數：強制重新下載
- `verify_cache_integrity()` - 雙重驗證（HEAD 比大小 + tar 解壓測試）
- 自動刪除不完整下載（大小不符的 cache）

### Changed
- 下載目錄從 current folder 改為 `./download_cache/`

## [1.1.0] - 2026-05-13

### Added
- 使用 Mozilla FTP 目錄結構取得版本資訊，不依賴 HTML 爬蟲
- `check_for_update()` - 檢查是否有新版本
- `download()` - 使用 requests 下載（去除 wget 依賴）
- `install()` - 解壓並安裝 Thunderbird
- 支援 release / esr 通道選擇
- `/tmp` 目錄安裝不需 sudo

### Changed
- 重構為模組化架構：check, download, install 各自獨立函式
- main() 簡化為命令列介面
- 改善錯誤處理與使用者體驗
- 修正版本解析邏輯以支援 149+ 版本

### Security
- 移除 `os.system()` 直接執行命令，改用 `subprocess`
- 移除 `input()` 直接拼接命令，防止 Injection

## [1.0.0] - 2026-05-12

### Added
- 初始版本
- `update_thunderbird.py` - 從官方網站取得更新
- `backup_thunderbird_rule.py` - 備份郵件篩選器規則