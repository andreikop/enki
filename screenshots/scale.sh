for image in `ls *.png`; do
    convert $image -scale 50% preview/$image
done;
