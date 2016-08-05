#!/bin/sh

export C_LOG_PATH=$KC_NWTTLS__CONTROLLER_LOG_PATH
export C_KOCHIEF_DIR_PATH=$KC_NWTTLS__KOCHIEF_DIR_PATH
export C_PYTHON_PATH=$KC_NWTTLS__PYTHON_PATH
export C_PARSER_PATH=$KC_NWTTLS__PARSER_PATH
export C_UPDATES_DIR_PATH=$KC_NWTTLS__UPDATES_DIR_PATH  # include trailing slash

echo " " >> $C_LOG_PATH
echo "-------" >> $C_LOG_PATH
echo "$(date +%Y-%d-%b_%H-%M-%S) - starting nightly script" >> $C_LOG_PATH
echo "$(date +%Y-%d-%b_%H-%M-%S) - about to call parser" >> $C_LOG_PATH

cd $C_KOCHIEF_DIR_PATH
echo "$(date +%Y-%d-%b_%H-%M-%S) - pwd, $(pwd)" >> $C_LOG_PATH

## parse files in updates dir & post to solr
$C_PYTHON_PATH $C_PARSER_PATH $C_UPDATES_DIR_PATH >> $C_LOG_PATH

echo "$(date +%Y-%d-%b_%H-%M-%S) - script done" >> $C_LOG_PATH
