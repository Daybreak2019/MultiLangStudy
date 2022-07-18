

Years=(2010 2011 2012 2013 2014 2015 2016 2017 2018 2019)
for year in ${Years[@]}
do
	python collect.py -y $year -s swc &
done
