import json
import sys
from pandas import read_csv
sys.path.append("../pubtator")

from pathlib import Path

from pubtator3_api import (parse_cite_response, send_publication_query,
                           send_search_query, get_biocjson_annotations,
                           convert_to_pubtator, batch_publication_query)

TESTDATA_DIR = Path(__file__).parent / "test_data"


def test_send_search_query_search():
    query = "N-dimethylnitrosamine and Metformin"
    res = send_search_query(query, type="search")

    expected = 130 
    if res.status_code == 200:
        total_articles = res.json()["count"]
    else:
        total_articles = None

    assert total_articles >= expected


def test_parse_cite_response():
    filepath = TESTDATA_DIR / "cite_tsv.tsv"
    expected = ["38229736", "38173127", "38132876"]
    with open(filepath) as f:
        pmid_list = parse_cite_response(f.read())
    
    assert pmid_list == expected


def test_send_search_query_cite():
    query = "N-dimethylnitrosamine and Metformin"
    res = send_search_query(query, type="cite")
    expected = 130 
    if res.status_code == 200:
        total_articles = len(parse_cite_response(res.text))
    else:
        total_articles = None

    assert total_articles >= expected


def test_parse_biocjson_response():
    filepath = TESTDATA_DIR / "pubtator3.37026113.json"
    with open(filepath) as f:
        file = json.load(f)
    
    expected_len = 33
    annotation_list = get_biocjson_annotations(file, retain_ori_text=False)

    assert len(annotation_list) == expected_len


def test_full_text():
    pmid = "37026113"
    res = send_publication_query(pmid, type="pmids", format="biocjson", full_text=True)

    expected_len = 389
    if res.status_code == 200:
        annotation_list = get_biocjson_annotations(res.json(), retain_ori_text=False)
    else:
        annotation_list = []

    assert len(annotation_list) == expected_len


def test_biocjson_pubtator_equal():
    pubtator_path = TESTDATA_DIR / "pubtator3.37026113.pubtator"
    biocjson_path = TESTDATA_DIR / "pubtator3.37026113.json"
    
    with open(pubtator_path) as pubtator, open(biocjson_path) as cjson:
        pubtator = pubtator.read()
        cjson = convert_to_pubtator(json.load(cjson), retain_ori_text=True, role_type="identifier")
        assert cjson == pubtator


def test_batch_standardized_annotations():
    test_filepath = TESTDATA_DIR / "pubtator3.37026113_standardized.pubtator"
    output = batch_publication_query(["37026113"], type="pmids", full_text=False, standardized=True)
    result = convert_to_pubtator(output[0], retain_ori_text=False, role_type="name")

    with open(test_filepath) as f:
        assert result == f.read()