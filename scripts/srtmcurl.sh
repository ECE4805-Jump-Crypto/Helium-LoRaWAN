#!/bin/bash

SUB_PATH=dem3
UNZIP_DIR=srtm3

if [[ $1 != "-p"  ]]; then
	echo "Usage: ./scripts/srtmcurl.sh -p <DATA PRECISION> [Region 1] [Region 2] ..."
	exit 1
elif [[ $2 -eq 1 ]]; then
	echo "Using 1-Arc Second Data"
	SUB_PATH="dem1"
	UNZIP_DIR="srtm1"
elif [[ $2 -eq 3  ]]; then
	echo "Using 3-Arc Second Data"
else
	echo "Arc-Second precision must be either 1 or 3"
	exit 1
fi

shift
shift

while [[ $# -gt 0 ]]; do
	curl -o $1.zip http://viewfinderpanoramas.org/$SUB_PATH/$1.zip
	unzip -j $1.zip -d ./rf_data/$UNZIP_DIR/
	cd ./rf_data/$UNZIP_DIR/
	for f in *.hgt; do
		srtm2sdf $f
	done
	rm *.hgt
	cd ../..
	rm $1.zip
	shift
done

exit 0
