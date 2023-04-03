from elasticsearch import Elasticsearch
from backoff import backoff
from tests.functional.settings import config


@backoff
def es_connect():
    es_client = Elasticsearch(
        hosts=f"{config.elastic_schema}://{config.elastic_host}:{config.elastic_port}",
    )

    if not es_client.ping():
        raise Exception


if __name__ == '__main__':
    es_connect()

