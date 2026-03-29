from unittest.mock import patch, MagicMock

import pandas as pd
import pytest

from backend.data.coingecko import fetch


class TestCoinGeckoFetch:
    @patch("backend.data.coingecko.requests.get")
    def test_missing_prices_key(self, mock_get):
        mock_response = MagicMock()
        mock_response.json.return_value = {"error": "rate limited"}
        mock_response.raise_for_status = MagicMock()
        mock_get.return_value = mock_response

        with pytest.raises(ValueError, match="missing required fields"):
            fetch("bitcoin", "2024-01-01", "2024-01-31")

    @patch("backend.data.coingecko.requests.get")
    def test_empty_prices(self, mock_get):
        mock_response = MagicMock()
        mock_response.json.return_value = {"prices": [], "total_volumes": []}
        mock_response.raise_for_status = MagicMock()
        mock_get.return_value = mock_response

        result = fetch("bitcoin", "2024-01-01", "2024-01-31")
        assert isinstance(result, pd.DataFrame)
        assert result.empty

    @patch("backend.data.coingecko.requests.get")
    def test_valid_response(self, mock_get):
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "prices": [[1704067200000, 42000.0], [1704153600000, 42500.0]],
            "total_volumes": [[1704067200000, 1e9], [1704153600000, 1.1e9]],
        }
        mock_response.raise_for_status = MagicMock()
        mock_get.return_value = mock_response

        result = fetch("bitcoin", "2024-01-01", "2024-01-02")
        assert len(result) == 2
        assert list(result.columns) == ["date", "open", "high", "low", "close", "volume"]

    @patch("backend.data.coingecko.requests.get")
    def test_non_dict_response(self, mock_get):
        mock_response = MagicMock()
        mock_response.json.return_value = "Rate limit exceeded"
        mock_response.raise_for_status = MagicMock()
        mock_get.return_value = mock_response

        with pytest.raises(ValueError, match="unexpected format"):
            fetch("bitcoin", "2024-01-01", "2024-01-31")

    @patch("backend.data.coingecko.requests.get")
    def test_timeout_parameter_passed(self, mock_get):
        mock_response = MagicMock()
        mock_response.json.return_value = {"prices": [], "total_volumes": []}
        mock_response.raise_for_status = MagicMock()
        mock_get.return_value = mock_response

        fetch("bitcoin", "2024-01-01", "2024-01-31")
        _, kwargs = mock_get.call_args
        assert "timeout" in kwargs
        assert kwargs["timeout"] == 30
