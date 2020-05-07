#!/bin/bash

FILE=$1
# First detect samplerate with ffmpeg -i FILENAME
SAMPLERATE=$2
INPUT_LANGUAGE=$3
OUTPUT_LANGUAGE=$4
if test -f "$FILE"; then
	FILENAME=$(basename -- "$FILE")
	EXTENSION="${filename##*.}"
	NAME="${FILENAME%.*}"
	CONVERT="${NAME}_converted.flac"
	ffmpeg -i $FILE -ac 1 $CONVERT
	mv $CONVERT audio/$NAME.flac
	# Split into small chunks
	sox -V3 audio/$NAME.flac audio/${NAME}_part_.flac \
	silence -l  1 0.3 0.3%   1 0.3 0.3% trim 0 30 : newfile : restart
	FILENAMES=$(ls audio/*part* | tr '\n' ',')
	./index.js $FILENAMES $SAMPLERATE $INPUT_LANGUAGE $OUTPUT_LANGUAGE
	rm audio/$NAME*.flac
else
	echo "Invalid file input given"
fi
