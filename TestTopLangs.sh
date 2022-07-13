
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
	
	python collect.py -s asso
	python collect.py -s assoml
	
	cd Data
	tar -zcvf LV-1-StatData-$top_num.tar.gz StatData
	cd -
	
	python collect.py -s asso -a
	python collect.py -s assoml -a
	
	cd Data
	tar -zcvf LV-2-StatData-$top_num.tar.gz StatData
	cd -
done


