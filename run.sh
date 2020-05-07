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
	mv $CONVERT temp/$NAME.flac
	# Split into small chunks
	sox -V3 temp/$NAME.flac temp/${NAME}_part_.flac \
	silence -l  1 0.3 0.3%   1 0.3 0.3% trim 0 30 : newfile : restart
	cd speech_to_translated_text
	FILENAMES=$(ls ../temp/*part* | tr '\n' ',')
	./index.js $FILENAMES $SAMPLERATE $INPUT_LANGUAGE $OUTPUT_LANGUAGE
	mv translation.json ../translation.json
	cd ..
	rm temp/$NAME*.flac
else
	echo "Invalid file input given"
fi
