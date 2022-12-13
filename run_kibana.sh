PROJECT_NETWORK='elastic-network'
CONTAINER='kibana'
IMAGE='docker.elastic.co/kibana/kibana:8.5.0'

# clean up existing resources, if any
echo "----------Cleaning up existing resources----------"
docker container stop $CONTAINER 2> /dev/null && docker container rm     $CONTAINER 2> /dev/null

# only clean up
if [ "$1" == "cleanup-only" ]
  then
exit
fi

# run kibana image
echo "----------Running server app----------"
docker run \
--name $CONTAINER \
--net $PROJECT_NETWORK \
-p 5601:5601 \
$IMAGE 
