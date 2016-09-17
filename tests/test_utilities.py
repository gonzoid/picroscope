import pytest
import utilities

@pytest.fixture()
def sample_text():
    return {'hello_lilol': 'HELLO LILOL'}

def test_text_formatting(sample_text):
    for raw, expected in sample_text.items():
        formatted = utilities.format_text(raw)
        assert( formatted == expected )
