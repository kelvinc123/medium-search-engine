import os
import pandas as pd
from bs4 import BeautifulSoup
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from nltk.tokenize import sent_tokenize
from nltk.stem import WordNetLemmatizer
import string


class DataLoader(object):
    """Abstract Data Loader Class"""

    def __init__(self):
        self.lemmatizer = WordNetLemmatizer()
        self.stop_words = set(stopwords.words('english'))
        self.punctuations = set(string.punctuation)
        self.punctuations.add("’")
        self.punctuations.add("“")
        self.punctuations.add("—")
        self.punctuations.add("·")
        self.punctuations.add("”")
        self.punctuations.add("…")
        self.text_data = None
        self.html_idx = None
        self.json = None
        self.df = None

    def load_csv(self, file_path):
        self.df = pd.read_csv(file_path)
        self.df = self.df.drop(["image"], axis=1).fillna("-")
        self.df["reading_time"] = pd.to_numeric(self.df["reading_time"])
        self.df["responses"] = pd.to_numeric(self.df["responses"], errors="coerce").fillna(-1)
        self.df["claps"] = pd.to_numeric(self.df["claps"])
        self.df["clap_prop"] = self.df["claps"] / self.df["claps"].sum()

    def load_data(self, file_path, auto_parse=False):
        pass
        # raise Exception("Not implemented yet")

    def parse_data(self):
        pass
        # raise Exception("Not implemented yet")

    def _parse_node(self, node):
        """Method to parse soup node to python dictionary"""

        ldict = {"doc": {}}

        def recurse(node, parents_str):
            """Recursive method to parse data until leaf nodes"""
            exec_str = f'doc["' + '"]["'.join(parents_str.split(' ')) + '"] = '
            if not node.findChildren(recursive=False):
                exec_str += '"'
                exec_str += node.text.strip().replace("\n", "\\n")
                exec_str += '"'
                exec(exec_str, globals(), ldict)
                return
            else:
                exec_str += "{}"
                exec(exec_str, globals(), ldict)
                for childNode in node.findChildren(recursive=False):
                    new_parents_str = parents_str + f" {childNode.name}"
                    recurse(childNode, new_parents_str)

        recurse(node, node.name)
        doc = ldict["doc"]
        return doc

    def get_json(self):
        """Method to get the list of dictionary of the data"""
        return self.json


class HTMLDataLoader(DataLoader):

    """Class for parsing AP Dataset"""

    def __init__(self):
        super().__init__()

    def load_data(self, file_path, auto_parse=False):
        """Method to load data from a given path"""
        with open(file_path, "r") as f:
            raw_data = " ".join(f.read().encode('ascii', errors='ignore').decode().replace(
                "Kelvin Christian", "").strip().split())

        self.json = None
        self.text_data = BeautifulSoup(raw_data, "html.parser")
        self.html_idx = int(os.path.basename(file_path).split(".")[0])
        if auto_parse:
            self.parse_data()

    def parse_data(self):
        """Method to parse the html structured data to dictionary"""
        text = " ".join(
            [node.text.strip() for node in self.text_data.findChildren(["p", "h1", "h2", "h3", "h4"])
                if not node.text.strip() == ""
            ]
        )
        # Clean text
        lemmatized_token = [self.lemmatizer.lemmatize(w) for w in word_tokenize(text)]
        filtered_token = [w for w in lemmatized_token if w.lower() not in self.stop_words]
        filtered_token = [w for w in filtered_token if w.lower() not in self.punctuations]
        clean_text = " ".join(filtered_token)

        # Full text
        sent_tokens = [s.strip().replace("  ", " ") for s in sent_tokenize(text)]
        full_text = " ".join(sent_tokens)

        self.json = self.df[self.df["id"] == self.html_idx].iloc[0].to_dict()
        self.json["text"] = clean_text
        self.json["full_text"] = full_text
