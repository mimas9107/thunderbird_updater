# thunderbird_updater
1. 使用官方 thunderbird for x86_64 linux version
2. 自動比對本機的 thunderbird版本 ( mine is /opt/thunderbird ), 若比線上的舊, 就自動下載並更新.
3. 主要程式為 update_thunderbird.py

# backup_thunderbird_rule
1. 備份本機端所有郵件篩選器規則檔, 並壓縮.
2. 備份路徑為 $HOME/back_thunderbird_rules/
3. 主要程式為 backup_thunderbird_rule.py
