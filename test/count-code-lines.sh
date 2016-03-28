sum=0
for i in $(find . -maxdepth 2 -name "*.py"); do 
	x=$(cat $i | sed '/^$/d'| grep -v \# | wc -l)
	let sum+=$x
done
echo $sum

for i in $(find . -maxdepth 2 -name "*.py"); do 
	cat $i | sed '/^$/d' | grep -v \#
done | wc -l
