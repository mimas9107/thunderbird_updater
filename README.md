# update_thunderbird2
1. 2025/05月以後 官網已無法使用 requests+bs4方式爬取下載網址。
2. 改以官方儲存庫下載對應版本網址： https://download-origin.cdn.mozilla.net/pub/thunderbird/releases/

# thunderbird_updater
1. 使用官方 thunderbird for x86_64 linux version
2. 自動比對本機的 thunderbird版本 ( mine is /opt/thunderbird ), 若比線上的舊, 就自動下載並更新.
3. 主要程式為 update_thunderbird.py

# backup_thunderbird_rule
1. 備份本機端所有郵件篩選器規則檔, 並壓縮.
2. 備份路徑為 $HOME/back_thunderbird_rules/
3. 主要程式為 backup_thunderbird_rule.py  喵喵喵
