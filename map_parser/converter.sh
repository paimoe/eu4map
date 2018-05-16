#!/bin/bash

# copy in provinces.bmp to this folder
# ./converter.sh provinces.bmp output.svg

input=$1
output=$2
histogram="$2.tmp.histo"
tmpsvg="$2.tmp.svg"
tmpmask="$2.tmp.ppm"

if [ ! -f "$input" ]; then
  echo "File not found in this directory"
  exit
fi

convert $input  -format %c -depth 8 histogram:info:"$histogram"
sed -i '$d'  "$histogram"
sort -n -k1,1 -r -o  "$histogram" "$histogram"
echo "<?xml version='1.0' standalone='no'?>" > "$output" ;
echo "<svg version='1.0' xmlns='http://www.w3.org/2000/svg'><g>" >> "$output" ;

totalhisto=$(wc -l < "$histogram")

i=1;
 while IFS= read -r line; do
  color="${line:27:6}";
  echo "processing color $color $i/$totalhisto"
  i=$(($i+1))
  convert "$input" \
  -transparent "#$color" \
  -alpha extract \
  "$tmpmask" 
  # potrace -s input -o output -t <min num pixels to render> --flat <because its all the one colour anyway, means no manual editing>
  # -M margin size
  potrace -s "$tmpmask" -o  "$tmpsvg" -t 5 --flat -M 0
  sed -ni '/transform/,/g>/p' "$tmpsvg"  
  sed -i "s/#000000/#$color/" "$tmpsvg" 
  cat "$tmpsvg" >> "$output" 
done < "$histogram"
echo "</g></svg>" >> "$output"

rm "$histogram"
rm "$tmpsvg"
rm "$tmpmask"