#!/bin/bash
total_token=13
min_workers=3
n_python_pid=$(ps aux |grep python |grep runner.py |wc |awk '{print $1}')
total_csvs=$(ls ./results/*.csv|wc|awk '{print $1}')
echo "=====We have generated $total_csvs repos====="
if [ $n_python_pid  -lt $min_workers ]
    then
        echo "=====Only $n_python_pid processes running, will start run_jobs.sh====="
        sudo pkill python
        # sleep 400
        for a in $(seq 0 1 $total_token)
            do
            command="python runner.py $a"
            # ($command &)
            # echo $command
            python runner.py $a  &
            sleep 1
         done
    else
        echo "=====Still have $n_python_pid proecesses running, we're good====="

fi