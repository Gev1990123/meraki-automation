import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from unittest.mock import MagicMock
from meraki_utils.firewall import firewall_get_application_categories 

def test_firewall_get_application_categories_found():
    mock_dashboard = MagicMock()
    mock_dashboard.appliance.getNetworkApplianceFirewallL7FirewallRulesApplicationCategories.return_value = {
        'applicationCategories': [
            {'name': 'Social Media', 'id': '123'},
            {'name': 'Gaming', 'id': '456'}
        ]
    }

    result = firewall_get_application_categories(mock_dashboard, 'net123', 'Gaming')
    assert result['id'] == '456'

def test_firewall_get_application_categories_not_found():
    mock_dashboard = MagicMock()
    mock_dashboard.appliance.getNetworkApplianceFirewallL7FirewallRulesApplicationCategories.return_value = {
        'applicationCategories': [{'name': 'Productivity', 'id': '999'}]
    }

    result = firewall_get_application_categories(mock_dashboard, 'net123', 'Unknown')
    assert result is None

from meraki_utils.firewall import firewall_get_l3_rules

def test_firewall_get_l3_rules():
    mock_dashboard = MagicMock()
    mock_dashboard.appliance.getNetworkApplianceFirewallL3FirewallRules.return_value = [
        {'comment': 'Allow HTTP', 'policy': 'allow'}
    ]

    result = firewall_get_l3_rules(mock_dashboard, 'net123')
    assert isinstance(result, list)
    assert result[0]['comment'] == 'Allow HTTP'

from meraki_utils.firewall import firewall_l3_rule_exists

def test_firewall_l3_rule_exists_true():
    existing_rules = [
        {
            'comment': 'Allow SSH',
            'policy': 'allow',
            'protocol': 'tcp',
            'destPort': '22',
            'destCidr': '192.168.1.0/24',
            'srcPort': 'any',
            'srcCidr': 'any',
            'syslogEnabled': False
        }
    ]

    new_rule = existing_rules[0].copy()
    assert firewall_l3_rule_exists(new_rule, existing_rules) is True

def test_firewall_l3_rule_exists_false():
    existing_rules = []
    new_rule = {
        'comment': 'Block Telnet',
        'policy': 'deny',
        'protocol': 'tcp',
        'destPort': '23',
        'destCidr': '0.0.0.0/0',
        'srcPort': 'any',
        'srcCidr': 'any',
        'syslogEnabled': True
    }
    assert firewall_l3_rule_exists(new_rule, existing_rules) is False

