import os
import sys
from time import sleep
import datetime

results = os.popen("find ~/.thunderbird -name msgFilterRules.dat").readlines()
# popen 是分叉一個子執行緒出去執行所給的命令. 所以下面主程序稍暫停等這個執行緒執行完畢傳回結果. 
sleep(1)
# print(results)
home = os.getenv("HOME")
cwd = os.getcwd()
if(cwd != home): os.chdir(home) #把現行工作路徑切到 home.

results = [ele.strip('\n') for ele in results]
# results = results[:]
for ele in results:
    print(ele)

src_path = [ ele.strip("\n")[ele.find(".thunderbird"):] for ele in results]

print(src_path)
#找家目錄底下有沒有 backup_thunderbird_rules資料夾.沒有就建一個!

if not os.path.exists(home+"/"+"backup_thunderbird_rules"):
    os.system("mkdir {}/backup_thunderbird_rules".format(home))

#按照來源路徑結構 cp到目的資料夾備份:
for target_file in src_path:
    os.system("cp -u --parents '{}' '{}'".format(target_file, home+"/"+"backup_thunderbird_rules"))

#取得時間命名打包的檔名.
backup_filename = "backup_thunderbird_rule-"+str(datetime.datetime.now()).replace(":","-").replace(" ","_").replace(".","-") + ".tar.gz"

#檢查目的地目錄 .thunderbird是否存在.
if os.path.exists(home+"/"+"backup_thunderbird_rules"+"/"+".thunderbird"):
    print(home+"/"+"backup_thunderbird_rules"+"/.thunderbird", " exists")
    
    #切到 備份目錄下.
    os.chdir(home+"/"+"backup_thunderbird_rules")
    #打包 .thunderbird成壓縮檔 backup_filename
    os.system("tar -zcavf {} {}".format(backup_filename ,".thunderbird"))
    print("已備份為 ", backup_filename)

else:
    print(home+"/"+"backup_thunderbird_rules"+"/.thunderbird", "not exist!")
    backup_filename=""