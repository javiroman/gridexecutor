# Para que la distribucion de componentes de la aplicacion en los nodos
# del cluster tenga efecto, hay que parar el servidor icepatch2server e
# invocar la ejecucion de un patch a la applicacion.
# Una vez hecho esto, el repositorio distrib mantenido por el servidor
# icepatch2server es distribuido entre los nodos.

# 1. Paramos el servidor icepatch2server
icegridadmin --Ice.Config=gridlocator.cfg -u grid -p xxx -e 'server stop GridExecutorApp.IcePatch2'
# 2. Decimos al registry que queremos parchear la aplicacion con nuevos componetes.
icegridadmin --Ice.Config=gridlocator.cfg -u grid -p xxx -e 'application patch -f GridExecutorApp'
