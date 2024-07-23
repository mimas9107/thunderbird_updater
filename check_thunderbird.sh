#!/usr/bin/bash
## 
current_ver=`/usr/bin/thunderbird --version|awk -F ' ' '{print $2}'`
update_ver=`curl https://www.thunderbird.net/zh-TW/download/ |grep -A 5 os_linux64 |grep -B 3 download-esr | grep href |awk -F '-' '{print $2}'`

echo "current version: $current_ver"
echo "update version: $update_ver"
if [ $current_ver == $update_ver ]; then
	echo "thunderbird ver. is newest"
else
	if [ -f update_thunderbird.py ]; then
#		./update_thunderbird.py
	else
		echo "Please download the newest ver. on the website manually."
	fi
	
fi

