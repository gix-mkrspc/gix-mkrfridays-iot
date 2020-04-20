source ./esphome/bin/activate
# start server on default port
esphome config/ dashboard &
sleep 5
# open web dashboard to default port
open http://localhost:6052