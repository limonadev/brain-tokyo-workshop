timestamp=$( date +%s )
results="results_${timestamp}"


for i in {1..2}
do
    mkdir -p $results/$i
    python wann_train.py -p p/laptop_swing.json -n 15
    cp -r log/ $results/$i/log
    cp results.txt $results/$i
done

cp p/default_wan.json $results
cp p/laptop_swing.json $results