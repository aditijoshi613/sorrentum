# ---
# jupyter:
#   jupytext:
#     text_representation:
#       extension: .py
#       format_name: percent
#       format_version: '1.3'
#       jupytext_version: 1.14.1
#   kernelspec:
#     display_name: Python 3 (ipykernel)
#     language: python
#     name: python3
# ---

# %% [markdown]
# # Description

# %% [markdown]
# The notebook demonstrates how open-source solvers solves the DaoCross problem.

# %% [markdown]
# # Imports

# %%
# %load_ext autoreload
# %autoreload 2
# %matplotlib inline

# %%
import logging
from typing import Tuple

import helpers.hdbg as hdbg
import helpers.henv as henv
import helpers.hprint as hprint

# %%
try:
    import pulp
except ImportError:
    # !sudo /bin/bash -c "(source /venv/bin/activate; pip install pulp)"
    import pulp

# %%
hdbg.init_logger(verbosity=logging.INFO)

_LOG = logging.getLogger(__name__)

_LOG.info("%s", henv.get_system_signature()[0])

hprint.config_notebook()


# %% [markdown]
# # Order class

# %%
class Order:

    # TODO(Grisha): add type hints, add assertions.
    def __init__(self, action, quantity, base_token, limit_price, quote_token):
        self.action = action
        self.quantity = quantity
        self.base_token = base_token
        self.limit_price = limit_price
        self.quote_token = quote_token

    def __repr__(self):
        return str(self)

    def __str__(self):
        ret = "action=%s, quantity=%s, base_token=%s, limit_price=%s, quote_token=%s" % (self.action, self.quantity, self.base_token, self.limit_price, self.quote_token)
        return ret


# %% [markdown]
# # Functions

# %%
# TODO(Grisha): consider extending for n orders.
def optimize_for_volume(order_1: Order, order_2: Order, exchange_rate: float) -> None:
    """
    Find the maximum transacted volume given the orders and the constraints.

    :param order_1: input buy order
    :param order_2: input sell order
    :param exchange_rate: price of base token / price of quote token
    :return: solver output in a human readable format
    """
    # Assume the fixed directions.
    hdbg.dassert_eq(order_1.action, "buy")
    hdbg.dassert_eq(order_2.action, "sell")
    #
    hdbg.dassert_lt(0, exchange_rate)
    # Initialize the model.
    prob = pulp.LpProblem("The DaoCross problem", pulp.LpMaximize)
    # Specify the vars. By setting the lower bound to zero it is safe
    # to omit the >= 0 constraint on the executed quantity.
    q_base_asterisk_1 = pulp.LpVariable("q_base_asterisk_1", lowBound=0)
    q_base_asterisk_2 = pulp.LpVariable("q_base_asterisk_2", lowBound=0)
    # Objective function.
    # TODO(Grisha): since the base token is the same, i.e. BTC it's
    # ok to use quantity, however the objective function should be
    # modified to account for different base tokens.
    prob += q_base_asterisk_1 + q_base_asterisk_2
    # Constraints.
    # Random number that is big enough to use the
    # "Big M" method.
    M = 1e6
    # TODO(Grisha): this should be a function of action.
    limit_price_cond_1 = int(exchange_rate <= order_1.limit_price)
    _LOG.info("limit_price_cond_1 is %s", limit_price_cond_1)
    limit_price_cond_2 = int(exchange_rate >= order_2.limit_price)
    _LOG.info("limit_price_cond_2 is %s", limit_price_cond_2)
    # Executed quantity is not greater than the requested quantity
    # given that the limit price condition is satisfied.
    prob += q_base_asterisk_1 <= order_1.quantity + M*(1-limit_price_cond_1)
    prob += q_base_asterisk_2 <= order_2.quantity + M*(1-limit_price_cond_2)
    # Executed quantity is zero if the limit price condition is not met.
    prob += q_base_asterisk_1 <= M*limit_price_cond_1
    prob += q_base_asterisk_1 >= -M*limit_price_cond_1
    #
    prob += q_base_asterisk_2 <= M*limit_price_cond_2
    prob += q_base_asterisk_2 >= -M*limit_price_cond_2
    # The number of sold tokens must match the number of bought tokens.
    prob += q_base_asterisk_1 == q_base_asterisk_2
    #
    prob.solve()
    # Display the results.
    _LOG.info(
        "The status is: %s"
        "\nThe total volume (in BTC) exchanged is: %s"
        "\nThe value of exchanged base token from order 1: %s"
        "\nThe value of exchanged base token from order 2: %s"
        "\nThe solution time (in seconds) is: %s",
        pulp.LpStatus[prob.status],
        pulp.value(prob.objective),
        q_base_asterisk_1.varValue,
        q_base_asterisk_2.varValue,
        round(prob.solutionTime, 2)
    )


def get_test_orders(limit_price_1: float, limit_price_2: float) -> Tuple[Order, Order]:
    # Genereate buy order.
    action = "buy"
    quantity = 5
    base_token = "BTC"
    quote_token = "ETH"
    order_1 = Order(action, quantity, base_token, limit_price_1, quote_token)
    _LOG.info("Buy order: %s", str(order_1))
    # Generate sell order.
    action = "sell"
    quantity = 5
    base_token = "BTC"
    quote_token = "ETH"
    order_2 = Order(action, quantity, base_token, limit_price_2, quote_token)
    _LOG.info("Sell order: %s", str(order_2))
    return order_1, order_2


# %% [markdown]
# # Solve the optimization problem

# %%
exchange_rate = 4
_LOG.info("Exchange rate=%s", exchange_rate)

# %% [markdown]
# ## Limit price condition is met for both orders

# %%
limit_price_1 = 5
limit_price_2 = 3
test_orders_1 = get_test_orders(limit_price_1, limit_price_2)
optimize_for_volume(test_orders_1[0], test_orders_1[1], exchange_rate)

# %% [markdown]
# ## Limit price condition is met only for 1 order

# %%
limit_price_1 = 5
limit_price_2 = 5
test_orders_1 = get_test_orders(limit_price_1, limit_price_2)
optimize_for_volume(test_orders_1[0], test_orders_1[1], exchange_rate)

# %%
limit_price_1 = 3
limit_price_2 = 3
test_orders_1 = get_test_orders(limit_price_1, limit_price_2)
optimize_for_volume(test_orders_1[0], test_orders_1[1], exchange_rate)

# %% [markdown]
# ## Limit price condition is not met for both orders

# %%
limit_price_1 = 3
limit_price_2 = 5
test_orders_1 = get_test_orders(limit_price_1, limit_price_2)
optimize_for_volume(test_orders_1[0], test_orders_1[1], exchange_rate)
