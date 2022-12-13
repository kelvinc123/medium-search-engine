PROJECT_NETWORK='elastic-network'
CONTAINER='elasticsearch'
IMAGE='docker.elastic.co/elasticsearch/elasticsearch:8.5.0'

# clean up existing resources, if any
echo "----------Cleaning up existing resources----------"
docker container stop $CONTAINER 2> /dev/null && docker container rm     $CONTAINER 2> /dev/null
docker network rm $PROJECT_NETWORK 2> /dev/null

# only clean up
if [ "$1" == "cleanup-only" ]
then
  exit
fi

# create network
echo "----------creating a virtual network----------"
docker network create $PROJECT_NETWORK

# run elastic image 
echo "----------Running server app----------"
docker run \
--name $CONTAINER \
--network $PROJECT_NETWORK \
--publish "9200:9200" \
--publish "9300:9300" \
-it \
$IMAGE 

