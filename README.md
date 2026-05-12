---
name:             "README.md"
description:      "Thunderbird Updater 專案說明文件"
created_date:     "2026/05/12"
modified_date:    "2026/05/13"
project_version:  "1.2.0"
document_version: "1.2.0"
agent_sign:       ['human/justin']
---

# thunderbird_updater
1. 使用官方 thunderbird for x86_64 linux version
2. 自動比對本機的 thunderbird版本 ( mine is /opt/thunderbird ), 若比線上的舊, 就自動下載並更新.
3. 主要程式為 update_thunderbird.py
4. 下載 cache 機制：同版本不再重複下載

## 功能

- 從 Mozilla FTP 取得最新版本資訊
- 檢查本機版本是否需要更新
- Download cache：已下載的檔案會儲存於 `./download_cache/`，同版本不再重複下載
- 完整性驗證：下載前 HEAD 比對大小 + 解壓測試

## 使用方式

```bash
# 檢查更新
python3 update_thunderbird.py

# 強制更新到指定路徑
python3 update_thunderbird.py --force --install-path /tmp/test_tb

# 只下載不安裝
python3 update_thunderbird.py --download-only

# 指定 cache 目錄
python3 update_thunderbird.py --cache-dir /path/to/cache

# 強制重新下載（不使用 cache）
python3 update_thunderbird.py --no-cache

# 指定通道 (release / esr)
python3 update_thunderbird.py --channel esr
```

## 參數

| 參數 | 說明 | 預設值 |
|------|------|--------|
| `--install-path` | 安裝路徑 | `/opt/thunderbird` |
| `--channel` | 更新通道 (release/esr) | `release` |
| `--cache-dir` | Cache 目錄 | `./download_cache/` |
| `--no-cache` | 強制重新下載 | false |
| `--download-only` | 只下載不安裝 | false |
| `--force` | 強制更新（不檢查版本） | false |

# backup_thunderbird_rule
1. 備份本機端所有郵件篩選器規則檔, 並壓縮.
2. 備份路徑為 $HOME/back_thunderbird_rules/
3. 主要程式為 backup_thunderbird_rule.py
