#!/bin/bash

SUB_PATH=dem1
UNZIP_DIR=srtm1
REGIONS=(M10 M11 M12 M13 M14 M15 M16 M17 M18 M19 M20 M21 M22 
         L10 L11 L12 L13 L14 L15 L16 L17 L18 L19 L20 L21 L22
         K10 K11 K12 K13 K14 K15 K16 K17 K18 K19 K20 K21
         J10 J11 J12 J13 J14 J15 J16 J17 J18
         I10 I11 I12 I13 I14 I15 I16 I17 I18
         H12 H13 H14 H15 H16 H17
         G14 G17)

EAST=(L15 L16 L17 L18 
         K15 K16 K17 K18
         J15 J16 J17 J18)

for region in ${REGIONS[@]}; do
	curl -o $region.zip http://viewfinderpanoramas.org/$SUB_PATH/$region.zip
    echo "processing region ${region}"
	unzip -j $region.zip -d ./rf_data/$UNZIP_DIR/
    rm $region.zip
	cd ./rf_data/$UNZIP_DIR/
	for f in *.hgt; do
		srtm2sdf-hd $f
        rm $f
	done
	cd ../..
    pwd
	
done

exit 0
