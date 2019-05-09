traininput_dir="train_data"
testinput_dir="test_data"
output_dir="output"
pattern_file="pat/Tok321dis.pat"  ##pattern_file="pat/pattern2.txt"
training_options=' -a sgd-l1 -t 5 -i 10 '  ##training_options=' -a sgd-l1 -t 5 '
patname=$(basename $pattern_file .pat)
corpus_name=$(basename $traininput_dir)

echo "================ Training $corpus_name (this may take some time) ================" 1>&2
# training: create a MODEL based on PATTERNS and TRAINING-CORPUS
# wapiti train -p PATTERNS TRAINING-CORPUS MODEL
echo "wapiti train $training_options -p $pattern_file <(cat $1) $output_dir/$patname-train-$corpus_name-$3.mod" 1>&2

wapiti train $training_options -p $pattern_file <(cat $traininput_dir/*.tab) $output_dir/$patname-train-$corpus_name.mod
# wapiti train -a bcd -t 2 -i 5 -p t.pat train-bio.tab t-train-bio.mod
#
# Note: The default algorithm, l-bfgs, stops early and does not succeed in annotating any token (all O)
# sgd-l1 works; bcd works

wapiti dump $output_dir/$patname-train-$corpus_name.mod $output_dir/$patname-train-$corpus_name.txt

echo "================ Inference $corpus_name ================" 1>&2
# inference (labeling): apply the MODEL to label the TEST-CORPUS, put results in TEST-RESULTS
# wapiti label -m MODEL TEST-CORPUS TEST-RESULTS
# -c : check (= evaluate)
# <(COMMAND ARGUMENTS ...) : runs COMMAND on ARGUMENTS ... and provides the results as if in a file
echo "wapiti label -c -m $output_dir/$patname-train-$corpus_name-$3.mod <(cat $1) $output_dir/$patname-train-test-$corpus_name-$3.tab" 1>&2
wapiti label -c -m $output_dir/$patname-train-$corpus_name.mod <(cat $testinput_dir/*) $output_dir/$patname-train-test-$corpus_name.tab
# wapiti label -c -m t-train-bio.mod test-bio.tab t-train-test-bio.tab
#echo "================ Evaluation with conlleval.pl $corpus_name ================" 1>&2
echo "Finished!"
# evaluate the resulting entities
# $'\t' is a way to obtain a tabulation in bash
#echo "$BINDIR/conlleval.pl -d $'\t' < $output_dir/$patname-train-test-$corpus_name-$3.tab | tee $output_dir/$patname-train-test-$corpus_name-$3.eval" 1>&2
perl conlleval.pl -d $'\t' < $output_dir/$patname-train-test-$corpus_name.tab | tee -a $output_dir/$patname-train-test-$corpus_name.eval