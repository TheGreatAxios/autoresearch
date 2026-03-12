"""Agentic wallet for autonomous research experiments.

Provides an EVM wallet loaded from a local private key in `.env` that
research agents can use to make x402 payments for API access and services.

Usage:
    from wallet import AgenticWallet

    wallet = AgenticWallet.load()
    print(wallet.address)

    # Pass the signer to an x402 client
    from x402_client import X402Client
    client = X402Client(wallet)
    response = client.get("https://api.example.com/data")

Environment variables (set in .env):
    EVM_PRIVATE_KEY  — 0x-prefixed hex private key for the agent wallet
"""

import os
from pathlib import Path

from dotenv import load_dotenv
from eth_account import Account
from eth_account.signers.local import LocalAccount
from x402.mechanisms.evm import EthAccountSigner

# Load .env from the project root
load_dotenv(Path(__file__).parent / ".env")


class AgenticWallet:
    """A local EVM wallet for autonomous research agents.

    Loads a private key from the EVM_PRIVATE_KEY environment variable
    (typically set in .env) and exposes the address and signing capability
    needed to make x402 payments.
    """

    def __init__(self, account: LocalAccount) -> None:
        self._account = account

    @classmethod
    def load(cls, private_key: str | None = None) -> "AgenticWallet":
        """Load the agent wallet from a private key.

        Args:
            private_key: Optional explicit private key (0x-prefixed hex).
                         Falls back to the EVM_PRIVATE_KEY environment variable.

        Raises:
            ValueError: If no private key is available.
        """
        key = private_key or os.environ.get("EVM_PRIVATE_KEY")
        if not key:
            raise ValueError(
                "No private key found. Set EVM_PRIVATE_KEY in your .env file "
                "(see .env.example) or pass private_key directly."
            )
        account: LocalAccount = Account.from_key(key)
        return cls(account)

    @property
    def address(self) -> str:
        """The checksummed EVM address for this wallet."""
        return self._account.address

    @property
    def signer(self) -> EthAccountSigner:
        """An x402-compatible EVM signer backed by this wallet's private key."""
        return EthAccountSigner(self._account)

    def __repr__(self) -> str:
        return f"AgenticWallet(address={self.address})"
