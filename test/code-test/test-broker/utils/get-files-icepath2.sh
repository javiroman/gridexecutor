# Notas
# 1. creamos el directorio DISTRIB nombre application. Debe tener permisos 
# de lectura para others, para que el icepatch2server pueda leer su contenido.
# 2. Ejecutamos "icepatch2cal ." en dicho directorio.
# 3. Reiniciamos el icepatch2server
# 4. Obtenemos con el icepatch2client el contenido donde queramos

DIR=files-tmp
PORT=10002

mkdir $DIR
icepatch2client -t --IcePatch2Client.Proxy="HelloGridApplication.IcePatch2/server:default -h sgt2-master -p $PORT" $DIR
