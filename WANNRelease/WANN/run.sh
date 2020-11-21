timestamp=$( date +%s )
results="/data/avillena/ademir/results_${timestamp}"

mkdir -p log
rm -r log
mkdir -p log

for i in $(seq 1 25)
do
    mkdir -p log
    rm -r log
    mkdir -p log
    mkdir -p $results/$i
    python wann_train.py -p p/laptop_swing.json -n 10
    cp -r log/ $results/$i/log
    cp results.txt $results/$i
done

cp p/default_wan.json $results
cp p/laptop_swing.json $results
