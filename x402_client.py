"""x402-enabled HTTP client for making payments to payment-gated APIs.

Wraps a standard requests session with automatic x402 (HTTP 402 Payment
Required) handling so research agents can access paid APIs and data sources
without manual payment steps.

Usage:
    from wallet import AgenticWallet
    from x402_client import X402Client

    wallet = AgenticWallet.load()
    client = X402Client(wallet)

    # Requests to x402-protected endpoints are paid automatically
    response = client.get("https://api.example.com/paid-endpoint")
    print(response.json())

    # POST is also supported
    response = client.post("https://api.example.com/submit", json={"key": "value"})
"""

from typing import Any

import requests

from wallet import AgenticWallet
from x402 import x402ClientSync
from x402.http.clients import x402_requests
from x402.mechanisms.evm.exact.register import register_exact_evm_client


class X402Client:
    """HTTP client with automatic x402 payment handling.

    Wraps a requests session and transparently negotiates x402 payments
    using the provided agentic wallet whenever a 402 response is received.

    Args:
        wallet: The agentic wallet used to sign and authorise payments.
        max_amount_usdc: Optional spending cap in USDC (e.g. 1.0 = $1.00).
                         Requests costing more than this will be refused.
    """

    def __init__(self, wallet: AgenticWallet, max_amount_usdc: float | None = None) -> None:
        self.wallet = wallet
        self._x402 = x402ClientSync()
        register_exact_evm_client(self._x402, wallet.signer)

        if max_amount_usdc is not None:
            from x402 import max_amount
            # Convert dollars to micro-USDC (6 decimal places)
            self._x402.register_policy(max_amount(int(max_amount_usdc * 1_000_000)))

    def get(self, url: str, **kwargs: Any) -> requests.Response:
        """Make a GET request, automatically paying any x402 requirement.

        Args:
            url: The full URL to request.
            **kwargs: Extra keyword arguments forwarded to requests.Session.get.

        Returns:
            The requests.Response object.
        """
        with x402_requests(self._x402) as session:
            return session.get(url, **kwargs)

    def post(self, url: str, **kwargs: Any) -> requests.Response:
        """Make a POST request, automatically paying any x402 requirement.

        Args:
            url: The full URL to request.
            **kwargs: Extra keyword arguments forwarded to requests.Session.post.

        Returns:
            The requests.Response object.
        """
        with x402_requests(self._x402) as session:
            return session.post(url, **kwargs)
