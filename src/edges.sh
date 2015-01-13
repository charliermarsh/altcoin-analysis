mkdir ../edges
mkdir ../txin
mkdir ../txout
mkdir ../clusters
mkdir ../balances
for i in "ltc" "dgc" "ppc" "anc" "ftc" "nvc" "nmc" "gld" "mnc" "lky" "drk" "mec"
do
    psql -U postgres -d abe-$i -A -F ',' -f abe_schema_edges.sql > ../edges/edges-$i.csv
    psql -U postgres -d abe-$i -A -F ',' -f abe_schema_txin.sql > ../txin/txin-$i.csv
    psql -U postgres -d abe-$i -A -F ',' -f abe_schema_txout.sql > ../txout/txout-$i.csv
    python clustergen.py ../edges-$i.csv > ../clusters/clusters-$i.txt
    python balancegen.py ../edges-$i.csv ../txin/txin-$i.csv ../txout/txout-$i.csv ../balances/balances-$i.pickle
done
