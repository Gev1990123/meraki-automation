import pytest
import tempfile
import os
from unittest.mock import patch
from meraki_utils.helpers import convert_mbps_to_kbps, determine_object_type, contains_letters, extract_group_ids, write_csv, append_csv, load_csv, get_user_selection

def test_convert_mbps_to_kbps():
    assert convert_mbps_to_kbps(1) == 1000
    assert convert_mbps_to_kbps(0.5) == 500
    assert convert_mbps_to_kbps(0) == 0

def test_determine_object_type():
    assert determine_object_type("192.168.1.0/24") == "cidr"
    assert determine_object_type("google.com") == "fqdn"
    assert determine_object_type("::1/64") == "cidr"

def test_contains_letters():
    assert contains_letters("192.168.1.1") == "cidr"
    assert contains_letters("examples.com") == "fqdn"
    assert contains_letters("test123") == "fqdn"

def test_extract_group_ids():
    assert extract_group_ids("GRP(123)") == ["123"]
    assert extract_group_ids("GRP(123),GRP(456)") == ["123", "456"]
    assert extract_group_ids("NoGroupHere") == []
    assert extract_group_ids("") == []

@pytest.fixture
def temp_csv_file():
    with tempfile.NamedTemporaryFile(delete=False, suffix=".csv") as tmp:
        yield tmp.name
    os.remove(tmp.name)


def test_write_and_load_csv(temp_csv_file):
    data = [{'name': 'DeviceA', 'value': '100'}]
    fieldnames = ['name', 'value']

    success, msg = write_csv(temp_csv_file, data, fieldnames)
    assert success is True
    assert "Successfully" in msg

    loaded_data = load_csv(temp_csv_file, fieldnames)
    assert loaded_data == data


def test_append_csv(temp_csv_file):
    initial_data = [{'name': 'A', 'value': '1'}]
    more_data = [{'name': 'B', 'value': '2'}]
    fieldnames = ['name', 'value']

    write_csv(temp_csv_file, initial_data, fieldnames)
    append_csv(temp_csv_file, more_data, fieldnames)

    combined = load_csv(temp_csv_file, fieldnames)
    assert combined == initial_data + more_data


# --- User Input Test with Mock ---

def test_get_user_selection_valid():
    items = [{'name': 'Option1'}, {'name': 'Option2'}]
    with patch('builtins.input', return_value='2'):
        selected = get_user_selection(items)
        assert selected == items[1]

def test_get_user_selection_invalid():
    items = [{'name': 'One'}, {'name': 'Two'}]
    with patch('builtins.input', return_value='99'):
        result = get_user_selection(items)
        assert result is None

