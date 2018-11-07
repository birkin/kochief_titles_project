#!/bin/sh

## called by a cron entry that cd's to the project-stuff directory; activates the virtual environment; then calls this script


export C_LOG_PATH=$KC_NWTTLS__CONTROLLER_LOG_PATH
export C_KOCHIEF_DIR_PATH=$KC_NWTTLS__KOCHIEF_DIR_PATH
export C_PYTHON_PATH=$KC_NWTTLS__PYTHON_PATH
echo "python path is... $C_PYTHON_PATH" >> $C_LOG_PATH
echo " " >> $C_LOG_PATH

export C_PARSER_PATH=$KC_NWTTLS__PARSER_PATH
echo "parser-path is... $C_PARSER_PATH" >> $C_LOG_PATH
echo " " >> $C_LOG_PATH

export C_UPDATES_DIR_PATH=$KC_NWTTLS__UPDATES_DIR_PATH  # include trailing slash
echo "updates dir path is... $C_UPDATES_DIR_PATH" >> $C_LOG_PATH
echo " " >> $C_LOG_PATH

export C_PROJECT_URL=$KC_NWTTLS__BASE_URL  # include trailing slash

echo " " >> $C_LOG_PATH
echo "-------" >> $C_LOG_PATH
echo "$(date +%Y-%d-%b_%H-%M-%S) - starting nightly script" >> $C_LOG_PATH
echo " " >> $C_LOG_PATH

echo "$(date +%Y-%d-%b_%H-%M-%S) - about to parse records and update solr" >> $C_LOG_PATH
cd $C_KOCHIEF_DIR_PATH
# echo "kochief dir path is... $C_KOCHIEF_DIR_PATH"
nice -19 $C_PYTHON_PATH $C_PARSER_PATH $C_UPDATES_DIR_PATH >> $C_LOG_PATH 2>&1
echo "$(date +%Y-%d-%b_%H-%M-%S) - parse and solr commit step completed" >> $C_LOG_PATH
echo " " >> $C_LOG_PATH

echo "$(date +%Y-%d-%b_%H-%M-%S) - about to remove 'expired' records from index" >> $C_LOG_PATH
# nice -19 $C_PYTHON_PATH manage.py index -expired >> $C_LOG_PATH 2>&1
echo "TODO: Redo expired-removal-code by calling script directly." >> $C_LOG_PATH
echo " " >> $C_LOG_PATH

echo "$(date +%Y-%d-%b_%H-%M-%S) - about to optimize the index" >> $C_LOG_PATH
# nice -19 python manage.py index --optimize all >> $C_LOG_PATH 2>&1
echo "TODO: Redo optimize-index-code by calling script directly." >> $C_LOG_PATH
echo " " >> $C_LOG_PATH

echo "$(date +%Y-%d-%b_%H-%M-%S) - about to warm caches by hitting $C_PROJECT_URL" >> $C_LOG_PATH
nice -19 curl -s $C_PROJECT_URL > /dev/null
echo " " >> $C_LOG_PATH

echo "$(date +%Y-%d-%b_%H-%M-%S) - script done" >> $C_LOG_PATH

## EOF
