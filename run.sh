#!/bin/bash

OUT_AUDIO=out_audio.flac
FILE=$1
# First detect samplerate with ffmpeg -i FILENAME
SAMPLERATE=$2
INPUT_LANGUAGE=$3
OUTPUT_LANGUAGE=$4
mkdir temp
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
	if ./index.js $FILENAMES $SAMPLERATE $INPUT_LANGUAGE $OUTPUT_LANGUAGE; then
		mv translation.json ../translation.json
		# If above translation is successful then run text to speech translation
		cd ../
		cd text_to_speech
		if ./demo_cli.py ../temp/$NAME.flac ../translation.json; then
			cd ../sow_speech
			if ./combine_speech.py ../translation.json ../output $OUT_AUDIO; then
				mv $OUT_AUDIO ../
				if ffmpeg -i ../$FILE -i ../$OUT_AUDIO -c:v copy -map 0:v:0 -map 1:a:0 ../new_${NAME}.mp4; then
					rm ../output/*
					echo "created new video new_${NAME}.mp4"
				fi
			fi
		fi
		cd ..
		rm temp/$NAME*.flac
		if test -f "$OUT_AUDIO"; then
			rm $OUT_AUDIO
		fi
	fi
else
	echo "Invalid file input given"
fi
rm -rf temp
