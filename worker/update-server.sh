cp ../broker/contract.ice worker.py fabexecutor.py fabfile.py /opt/DISTRIB/GridExecutorApp/
cd /opt/DISTRIB/GridExecutorApp/
icepatch2calc .
cd -
sh _distrib-artifacts.sh 
