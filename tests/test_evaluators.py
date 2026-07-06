from langsmith.schemas import Example, Run

from app.core.evaluation.evaluators import _extract_query, _extract_response, _parse_score


def test_extract_query_from_nested_dataset_shape():
    inputs = {
        "query": {
            "query": "Is there API access for custom integrations?",
            "context": {},
        }
    }
    assert _extract_query(inputs) == "Is there API access for custom integrations?"


def test_extract_response_from_run_outputs():
    outputs = {
        "response": "# API Access for Custom Integrations\nYes, CrowdStrike Falcon provides API access.",
        "confidence": 0.8,
    }
    assert "API Access" in _extract_response(outputs)


def test_extract_response_from_nested_output():
    outputs = {
        "output": {
            "response": "Quarantined files can be reviewed in Falcon.",
        }
    }
    assert _extract_response(outputs) == "Quarantined files can be reviewed in Falcon."


def test_parse_score():
    assert _parse_score("Score: 5 - Excellent response") == 5
    assert _parse_score("This is poor and misses the point") == 2
