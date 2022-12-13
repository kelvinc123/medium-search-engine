import os
import argparse
from flask import Flask, render_template, request
from models.elastic.ElasticConnect import ElasticConnect
from models.elastic.DataLoader import HTMLDataLoader
from models.Medium import Medium
from resources.search_engine import SearchEngine

# ---------------------------------------------------------------------------- #
#                                   Constants                                  #
# ---------------------------------------------------------------------------- #
# Path to directory of the dataset
DIR_HTML_PATH = os.path.join(os.path.join(".", "dataset"), "html")
CSV_PATH = os.path.join(os.path.join(".", "dataset"), "medium_data.csv")

ADDRESS = "https://localhost:9200"
CA_CERTS = "http_ca.crt"
USERNAME = "elastic"
INDEX = "medium_index"

# ---------------------------------------------------------------------------- #
#                              Command Line Parser                             #
# ---------------------------------------------------------------------------- #

# Parse commands
parser = argparse.ArgumentParser()
parser.add_argument(
    "password",
    type=str,
    help="A required string for elasticsearch password"
)
parser.add_argument(
    "--populate",
    action='store_true',
    help="A boolean arg to store AP data to elasticsearch"
)
args = parser.parse_args()
password = args.password
password = "d=AEspitO-_p+9dRwZeF"
populate = args.populate

# Instantiate Objects
loader = HTMLDataLoader()
loader.load_csv(CSV_PATH)
elastic = ElasticConnect(
    addr=ADDRESS,
    ca_certs=CA_CERTS,
    username=USERNAME,
    password=password,
    data_loader=loader
)
search_engine = SearchEngine(elastic_instance=elastic)

# ---------------------------------------------------------------------------- #
#                                     Flask                                    #
# ---------------------------------------------------------------------------- #
app = Flask(__name__)


@app.route("/")
def home():
    return render_template("home.html")


@app.route("/search_result/", methods=["POST"])
def search_result():
    global search_engine
    query = request.form.get("content")
    results = search_engine.search(query=query, index=INDEX, top_10=True, score_prop=0.98)
    results = [
        Medium(
            file_id = result.get("file_id", None),
            url = result.get("url", None),
            title = result.get("title", None),
            subtitle = result.get("subtitle", None),
            claps = result.get("claps", None),
            reponses = result.get("reponses", None),
            reading_time = result.get("reading_time", None),
            publication = result.get("publication", None),
            date = result.get("date", None),
            text = result.get("text", None),
            full_text = result.get("full_text", None),
            score = result.get("score", None)
        ) for result in results]

    return render_template("search_result.html", results=results)

# ---------------------------------------------------------------------------- #
#                                     Main                                     #
# ---------------------------------------------------------------------------- #
if __name__ == "__main__":

    if populate:
        elastic.populate_data_from_dir(
            index=INDEX, dir_path=DIR_HTML_PATH, force_new=True)
    else:
        app.run(port=5000)