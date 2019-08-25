#!/bin/bash
## gitlab slave node rsync script
# 可设置定时去同步，如每隔10分钟执行一次同步


HOST="10.100.240.204"
USERNAME="yemago"
PASSWORD_File="/etc/rsyncd/rsync.password"
RSYNC_COMMON_PARAMERS=" --port=873 -vzrtopgl --progress --delete --password-file=${PASSWORD_File}"
LOG_PATH="/var/log/gitlab_rsync.log"

## record the resync thread is processing or finish
# processing : resync working
# finish: synchronized work completion

RSYNC_STATUS_PATH="/var/log/gitlab_rsync_status"


function date_time_format() {
    ## return date time format
    
    echo `date +'%Y-%m-%d %H:%M:%S'`
}

function logger() {
    ## record log to file

    if [[ -n "$1" ]]; then
        echo `date_time_format` $1 >> ${LOG_PATH}
    fi
}

function process() {
    ## rsync process
    ## 
    
    rsync_is_processing
    echo "processing" > ${RSYNC_STATUS_PATH}    

    # .ssh
    logger ".ssh start to rsync"
    rsync ${RSYNC_COMMON_PARAMERS} ${USERNAME}@${HOST}::gitlab/.ssh /var/opt/gitlab/
    logger ".ssh rsync have finish"    

    # uploads
    logger "start to rsync uploads"
    rsync ${RSYNC_COMMON_PARAMERS} ${USERNAME}@${HOST}::gitlab/gitlab-rails/uploads /var/opt/gitlab/gitlab-rails/
    logger "uploads rsync have finish"    
 
    # shared
    logger "shared start to rsync"
    rsync ${RSYNC_COMMON_PARAMERS} ${USERNAME}@${HOST}::gitlab/gitlab-rails/shared /var/opt/gitlab/gitlab-rails/
    logger "shared rsync have finish"    
 
    # builds
    logger "builds start to rsync"
    rsync ${RSYNC_COMMON_PARAMERS} ${USERNAME}@${HOST}::gitlab/gitlab-ci/builds /var/opt/gitlab/gitlab-ci/
    logger "builds rsync have finish"    
 
    # git-data
    logger "git-data start to rsync"
    rsync ${RSYNC_COMMON_PARAMERS} ${USERNAME}@${HOST}::gitlab/git-data /var/opt/gitlab/
    logger "git-data rsync have finish"    

    echo "finish" > ${RSYNC_STATUS_PATH}    
}

function rsync_is_processing() {
    ## check the rsync process is processing, if not then exit this process

    grep "processing" ${RSYNC_STATUS_PATH} >> /dev/null
    if [[ $? == 0 ]]; then
        # 前面在执行的rsync进程还未结束,则本次先不同步
        # 当前一个rsync进程时，会用grep查找找到2个
        
        #echo `ps -ef |grep "bash /utils/scripts/gitlab_rsync.sh" |grep -v "grep" |wc -l`
        #echo `ps -ef |grep "bash /utils/scripts/gitlab_rsync.sh" |grep -v "grep"`
        if test `ps -ef |grep "bash /utils/scripts/gitlab_rsync.sh" |grep -v "grep" |wc -l` -gt 2; then
            logger "there are gitlab_rsync process on processing ..."
            exit 0
        fi

    fi
}

function main() {
    ## the program enter
    
    process
}

main

