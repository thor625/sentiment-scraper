from src.app import score_sentiment, to_stooq_symbol

def test_score_sentiment_positive_vs_negative():
    pos = score_sentiment("This stock is amazing and I love it")
    neg = score_sentiment("This stock is terrible and I hate it")
    assert pos > neg
    assert pos > 0
    assert neg < 0

def test_to_stooq_symbol_adds_us_suffix():
    assert to_stooq_symbol("AAPL") == "AAPL.US"
    assert to_stooq_symbol("aapl") == "AAPL.US"
    assert to_stooq_symbol("AAPL.US") == "AAPL.US"
    assert to_stooq_symbol("") == ""