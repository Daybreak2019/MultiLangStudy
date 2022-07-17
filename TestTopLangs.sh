
TopNumAry=(20 0)
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
	tar -zcvf StatData-$top_num.tar.gz StatData
	cd -
	
	python collect.py -s asso -L level1
	python collect.py -s assoml -L level1	
	cd Data
	tar -zcvf LV-1-StatData-$top_num.tar.gz StatData
	cd -
	
	python collect.py -s asso -L level2
	python collect.py -s assoml -L level2	
	cd Data
	tar -zcvf LV-2-StatData-$top_num.tar.gz StatData
	cd -
	
	echo
	echo "#########################################################"
	echo "#"
	echo "#   try evolution analysis ......  "
	echo "#"
	echo "#########################################################"
	echo
	Years=(2010 2011 2012 2013 2014 2015 2016 2017 2018 2019)
	for year in ${Years[@]}
	do
		python collect.py -t -f Data/OriginData$year/Repository_List.csv
		mv Repository_List Data/OriginData$year/
		python collect.py -l $top_num -s repostats
		python collect.py -l $top_num -y $year -s repostats
	done
	
done


