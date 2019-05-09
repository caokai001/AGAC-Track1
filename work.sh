#!bin/bash
python kcao_modify_zq.py
mkdir -p ./test_data && cp ./AGAC_training/test.tab ./test_data
mkdir -p ./train_data && cp ./AGAC_training/train.tab ./train_data
mkdir -p ./output
##添加wapiti到环境变量
bash wapiti.sh
