from elasticsearch import Elasticsearch
import os
import sys


class ElasticConnect(object):

    def __init__(self, addr: str, ca_certs: str, username: str, password: str, data_loader):
        """
        data_loader: DataLoader Instance
        """
        self.address = addr
        self.ca_certs = ca_certs
        self.username = username
        self.password = password
        self.data_loader = data_loader
        self.connect()

    def connect(self):
        # Create Elasticsearch Instance with the provided credentials
        if self.ca_certs:
            self.client = Elasticsearch(
                self.address,
                ca_certs=self.ca_certs,
                basic_auth=(self.username, self.password)
            )
        else:
            self.client = Elasticsearch(
                self.address,
                basic_auth=(self.username, self.password)
            )
        try:
            self.client.info()
        except Exception as e:
            print(e)
            print("Elastic is not connected")
            print("Exit...")
            sys.exit(1)

    def populate_data_from_file(self, index: str, file_path: str):
        """Parse and Load data from file to elasticsearch"""
        if not os.path.isfile(file_path):
            return

        # Load the dataset
        try:
            print(f"Parsing data from {file_path}")
            self.data_loader.load_data(file_path=file_path, auto_parse=True)
        except Exception as e:
            print(e)
            print("Error in loading the data")
            with open("unreadable_file.txt", "a") as f:
                f.write(file_path)
            return

        # Get the data
        doc = self.data_loader.get_json()

        # Index document
        print(f"Storing data to elastic")
        self.client.index(index=index, document=doc)

        return

    def populate_data_from_dir(self, index: str, dir_path: str, force_new=False):
        """
        Parse and Load data from directory to elasticsearch

        if force_new argument is True, it deletes the index and creates a new one
        """
        if os.path.exists("unreadable_file.txt"):
            os.remove("unreadable_file.txt")

        # Delete index
        if force_new and self.client.indices.exists(index=index):
            self.client.indices.delete(index=index)

        # Create new index if it doesn't exists
        if not self.client.indices.exists(index=index):
            self.client.indices.create(index=index)

        file_paths = os.listdir(dir_path)
        i = 0
        for file_path in file_paths:
            i += 1
            print(f"Working on the {i}-th data")
            self.populate_data_from_file(
                index=index, file_path=os.path.join(dir_path, file_path))

        self.client.indices.refresh(index=index)
        return