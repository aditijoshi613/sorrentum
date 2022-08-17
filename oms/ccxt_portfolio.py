"""
Import as:

import oms.ccxt_portfolio as occxport
"""

import logging
from typing import Any, List, Optional

import market_data as mdata
import oms.ccxt_broker as occxbrok
import oms.portfolio as omportfo

_LOG = logging.getLogger(__name__)


class CcxtPortfolio(omportfo.DataFramePortfolio):
    """
    A Portfolio that stores the information in a dataframe backed by
    CcxtBroker.
    """

    def __init__(
        self,
        *args: Any,
        **kwargs: Any,
    ):
        """
        Constructor.
        """
        super().__init__(
            *args,
            **kwargs,
        )


def get_CcxtPortfolio_prod_instance1(
    strategy_id: str,
    market_data: mdata.MarketData,
    asset_ids: Optional[List[int]],
    pricing_method: str,
) -> CcxtPortfolio:
    """
    Initialize the `CcxtPortfolio` with cash using `CcxtBroker`.
    """
    # Build CcxtBroker.
    broker = occxbrok.get_CcxtBroker_prod_instance1(
        market_data,
        strategy_id,
    )
    # Build CcxtPortfolio.
    mark_to_market_col = "close"
    initial_cash = 1e6
    portfolio = CcxtPortfolio.from_cash(
        broker,
        mark_to_market_col,
        pricing_method,
        initial_cash=initial_cash,
        asset_ids=asset_ids,
    )
    return portfolio