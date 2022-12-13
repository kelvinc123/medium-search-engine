
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from nltk.stem import WordNetLemmatizer
import string
import numpy as np


class Preprocess(object):
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

    def clean_text(self, text):
        lemmatized_token = [self.lemmatizer.lemmatize(
            w) for w in word_tokenize(text)]
        filtered_token = [
            w for w in lemmatized_token if w.lower() not in self.stop_words]
        filtered_token = [
            w for w in filtered_token if w.lower() not in self.punctuations]
        clean_text = " ".join(filtered_token)
        return clean_text.lower()


class SearchEngine(object):

    def __init__(self, elastic_instance) -> None:
        self.elastic = elastic_instance
        self.preprocess = Preprocess()

    def search(self, query, index, top_10=True, score_prop=0.9):
        clean_query = self.preprocess.clean_text(query)
        results = self.elastic.client.search(
            index=index,
            query={
                "bool": {
                    "must": [
                        {
                            "match": {
                                "text": {"query": clean_query}
                            }
                        },
                        {
                            "match": {
                                "full_text": {"query": query.lower()}
                            }
                        }
                    ],
                    "should":
                    [
                        {
                            "multi_match": {
                                "query": query.lower(),
                                "fields": [
                                    "title^3",
                                    "full_text"
                                ],
                                "type": "phrase"
                            }
                        },
                        {
                            "match": {
                                "title": {"query": clean_query}
                            }
                        }
                    ]
                }
            }
        )
        claps = np.array([result["_source"]["claps"] for result in results["hits"]["hits"]])
        claps = claps / np.sum(claps)
        scores = np.array([result["_score"] for result in results["hits"]["hits"] ])
        scores = scores / np.sum(scores)
        new_score = (score_prop * scores) + ((1 - score_prop) * claps)
        for i in range(len(results["hits"]["hits"])):
            results["hits"]["hits"][i]["_source"]["score"] = new_score[i]

        results = [result["_source"] for result in results["hits"]["hits"]]
        results = sorted(results, key=lambda x: x["score"], reverse=True)
        if top_10:
            return results[:10]
        else:
            return results
