# US Treasury daily yield curve data fetcher.
# Pulls daily yield curve rates (2Y, 10Y, and full curve)
# from the US Treasury website XML feed.

import requests
import pandas as pd
from xml.etree import ElementTree


TREASURY_URL = "https://data.treasury.gov/feed.svc/DailyTreasuryYieldCurveRateData"


def fetch(start_date, end_date):
    """
    Args:
        start_date (str or datetime.date): start of date range
        end_date (str or datetime.date): end of date range

    Process:
        Calls the US Treasury XML feed for daily yield curve rates.
        Filters results to the requested date range.
        Parses the XML response to extract date, 2Y yield, and 10Y yield.
        Each yield is returned as a separate row with an indicator name
        so it can be stored in the macro_data table via store.write_macro_data().

    Returns:
        pd.DataFrame: columns — date, indicator, value
            indicator is one of: "YIELD_2Y", "YIELD_10Y"
    """
    response = requests.get(
        TREASURY_URL,
        params={
            "$filter": f"NEW_DATE ge datetime'{start_date}T00:00:00' and NEW_DATE le datetime'{end_date}T00:00:00'",
        },
    )
    response.raise_for_status()

    ns = {
        "atom": "http://www.w3.org/2005/Atom",
        "m": "http://schemas.microsoft.com/ado/2007/08/dataservices/metadata",
        "d": "http://schemas.microsoft.com/ado/2007/08/dataservices",
    }

    tree = ElementTree.fromstring(response.content)
    rows = []

    for entry in tree.findall("atom:entry", ns):
        content = entry.find("atom:content", ns)
        properties = content.find("m:properties", ns)

        date_str = properties.find("d:NEW_DATE", ns).text[:10]
        yield_2y = properties.find("d:BC_2YEAR", ns).text
        yield_10y = properties.find("d:BC_10YEAR", ns).text

        if yield_2y:
            rows.append({"date": date_str, "indicator": "YIELD_2Y", "value": float(yield_2y)})
        if yield_10y:
            rows.append({"date": date_str, "indicator": "YIELD_10Y", "value": float(yield_10y)})

    return pd.DataFrame(rows)
