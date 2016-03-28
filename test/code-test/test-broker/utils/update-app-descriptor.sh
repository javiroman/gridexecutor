DIR=../sync
#DIR=../async

cd $DIR
icegridadmin --Ice.Config=../client.cfg -u ice -p xxx -e 'application update app.xml'
