#!/bin/sh
if [ ! -r macbeth.txt ];then wget -O macbeth.txt http://www.gutenberg.org/dirs/etext98/2ws3410.txt
fi 
head -n -0 macbeth.txt | tr -d "\'" | tr -cs A-Za-z '\n' | sed "s/\s//g;s/\(.*\)/\L\1/" | sort | uniq -c | sort -rn | sed "s/[0-9]//g;s/\t//g;s/\s//g;" | head -n 10
