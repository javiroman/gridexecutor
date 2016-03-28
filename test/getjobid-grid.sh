jobid=$1
A=$(curl --fail --silent --show-error \
	--header "Accept: application/json" \
	--request GET \
	http://sgt2-master:8888/status?jobid=$1)

echo $A




