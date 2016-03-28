# Muestra informacion de debug
A=$(curl --fail --silent --show-error \
	--header "Accept: application/json" \
	--request GET \
	http://sgt2-master:8888/debug)

echo "Main queue size: $A"



