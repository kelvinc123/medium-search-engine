
## Requirements

The dataset will not be submitted to maintain the size of the files.

The elastic search docker version is used because the non-docker version gives an error. Download Docker Desktop at: https://www.docker.com/products/docker-desktop/

After downloading docker, run `./pull_images.sh` to pull the **elasticsearch** image from dockerhub.


## Instruction

#### Install required packages
* Create python environment using `python -m venv venv`

* Activate virtual environment: `source venv/bin/activate`

* Install packages `pip install -r requirements.txt`

#### Run elastic
* Run docker desktop or docker engine.
* Run `./run_elastic.sh` to run the elastic search on docker. Wait until the password is given, copy that password.
* Run `./first_setup.sh` to download **http_ca.crt** from docker that will be used as certificate. Use the password from previous step to get the file

#### Run Flask
To populate the data before running the flask app, run `python app.py <password> --populate`. The argument `password` is required which can be found on the elastic terminal. The `--populate` argument gives instruction to store the AP data to the elasticsearch. It can be omitted if the data is already there.


## Additional Comments
If the bash file doesn't work, run `chmod 755 <filename>.sh` before runnning the **.sh** file.

The query method can be found inside `resources/search_engine.py`. The result document must match the query. The correct order of the query is optional, but will be given a higher score if the document contains the exact same order as the query.

## Additional Resources
https://www.elastic.co/guide/en/elasticsearch/reference/current/docker.html
