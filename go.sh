FILE="./tests/test$1.go"
rm ./src/parsetab.py ./src/parser.out
python3 src/parser.py $FILE
