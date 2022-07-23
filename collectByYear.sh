
startYear=$1
Years=(2010 2011 2012 2013 2014 2015 2016 2017 2018 2019)
for year in ${Years[@]}
do
	if [ $year -lt $startYear ]; then
		continue
	fi
	python collect.py -y $year -s collect
done
