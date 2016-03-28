# app-descriptor.sh add
# app-descriptor.sh update
exec 2> /dev/null

if [ "$1" == "-h"  ]; then
	echo "Usage: `basename $0` [add, update]"
	exit 0
fi

icegridadmin --Ice.Config=gridlocator.cfg -u ice -p xxx -e "application $1 app.xml"

echo "application -> $1"
echo "restarting servers ..."
servers=$(icegridadmin --Ice.Config=gridlocator.cfg -u grid -p xxx -e 'server list' | grep Worker)
for i in $servers; do
	icegridadmin --Ice.Config=gridlocator.cfg -u grid -p xxx -e "server stop $i"
	icegridadmin --Ice.Config=gridlocator.cfg -u grid -p xxx -e "server start $i"
done

