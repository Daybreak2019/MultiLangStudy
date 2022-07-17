
Years=(2010 2011 2012 2013 2014 2015 2016 2017 2018 2019)
for year in ${Years[@]}
do
	python collect.py -t -f Data/OriginData$year/Repository_List.csv
	mv Repository_List Data/OriginData$year/
	python collect.py -l 20 -y $year -s repostats
	python collect.py -y $year -s clone

done

