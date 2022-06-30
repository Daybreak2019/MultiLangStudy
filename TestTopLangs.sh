
TopNumAry=(50 40 30 20 10)
for top_num in ${TopNumAry[@]}
do
	echo
	echo "#########################################################"
	echo "#"
	echo "#   try top $top_num languages ......  "
	echo "#"
	echo "#########################################################"
	echo
	
	python collect.py -t -f Data/OriginData/Repository_List.csv
	mv Repository_List Data/OriginData/
	
	python collect.py -l $top_num -s repostats
	cp Data/StatData/LangCombo_Stats.csv Data/StatData/LangCombo_Stats-$top_num.csv
	python collect.py -s asso
done


