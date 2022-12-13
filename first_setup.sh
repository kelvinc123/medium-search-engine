CONTAINER='elasticsearch'

# Generate http_ca
echo "----------Generate http_ca file----------"
docker cp $CONTAINER:/usr/share/elasticsearch/config/certs/http_ca.crt .

# Setup
echo ""
echo "----------First Setup----------"
echo "----------Password can be found in the running docker terminal----------"
curl --cacert http_ca.crt -u elastic https://localhost:9200
