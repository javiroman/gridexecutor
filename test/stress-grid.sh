# http://alvinalexander.com/web/using-curl-scripts-to-test-restful-web-services

exec 2> log
set -xv

ITER=$1
results=()

echo "sending $ITER jobs in async mode"
for i in $(seq $ITER); do
	# Ejecuta una tarea asincrona
	A=$(curl --fail --silent --show-error \
	--header "Accept: application/json" \
	--request POST \
	http://sgt2-master:8888/apagar \
		-d ip=192.168.122.203 -d ip=192.168.122.166 -d ip=192.168.122.133)

	results+=($A)
done

check_status() {
	curl --fail --silent --show-error \
		--header "Accept: application/json" \
		--request GET \
		http://sgt2-master:8888/status?jobid=$1
}

# echo "${results[@]}"

echo "Waiting for results ..."
while [ ${#results[*]} -gt 0 ]; do
	for i in ${!results[*]}; do
		ret=$(check_status ${results[$i]})
		if [ "$ret" == "running" ]; then
			continue
		else
			echo
			echo "Results for jobid: ${results[$i]}"
			echo
			unset results[$i]
			echo $ret | sh JSON.sh -b
		fi
	done
done
echo

