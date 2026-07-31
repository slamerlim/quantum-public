```python
"""
execution_flow.py

Simplified execution pipeline demonstrating the architecture of the
Quantum System.

This example intentionally omits any proprietary trading logic IN A VERY BASIC DEMO MANNER.

Its purpose is to demonstrate:

- Event-driven architecture
- Separation of concerns
- Validation pipeline
- Risk management
- Execution orchestration
- Structured telemetry

Author:
Danil Zhdanov
"""

from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import Optional


# ============================================================
# Domain Models
# ============================================================

class SignalSide(str, Enum):
    BUY = "BUY"
    SELL = "SELL"


@dataclass
class MarketEvent:
    symbol: str
    price: float
    timestamp: datetime


@dataclass
class TradingSignal:
    symbol: str
    side: SignalSide
    confidence: float


@dataclass
class Order:
    symbol: str
    side: SignalSide
    quantity: float


# ============================================================
# Services
# ============================================================

class SignalEngine:
    """
    Generates trading opportunities.

    Real implementation would evaluate dozens of indicators,
    market structure, liquidity, volatility, etc.
    """

    def generate(self, event: MarketEvent) -> Optional[TradingSignal]:

        if event.price > 100:
            return TradingSignal(
                symbol=event.symbol,
                side=SignalSide.BUY,
                confidence=0.91,
            )

        return None


class ValidationPipeline:
    """
    Multi-stage validation.

    Production systems typically include:

    - data quality
    - liquidity
    - volatility
    - exchange status
    - confidence threshold
    """

    def validate(self, signal: TradingSignal) -> bool:

        return signal.confidence > 0.85


class RiskEngine:
    """
    Portfolio-level risk management.
    """

    def approve(self, signal: TradingSignal) -> bool:

        return True

    def calculate_position_size(
        self,
        signal: TradingSignal,
    ) -> float:

        return 0.10


class ExecutionEngine:
    """
    Responsible only for execution.

    No strategy logic belongs here.
    """

    def submit(self, order: Order):

        print(
            f"[EXECUTION] "
            f"{order.side} "
            f"{order.quantity} "
            f"{order.symbol}"
        )


class Telemetry:
    """
    Simplified structured telemetry.
    """

    @staticmethod
    def event(name: str, **fields):

        print(
            {
                "event": name,
                "timestamp": datetime.utcnow().isoformat(),
                **fields,
            }
        )


# ============================================================
# Coordinator
# ============================================================

class TradingCoordinator:

    def __init__(self):

        self.signal_engine = SignalEngine()
        self.validation = ValidationPipeline()
        self.risk = RiskEngine()
        self.execution = ExecutionEngine()

    def process(self, event: MarketEvent):

        Telemetry.event(
            "market_event",
            symbol=event.symbol,
            price=event.price,
        )

        signal = self.signal_engine.generate(event)

        if signal is None:

            Telemetry.event(
                "no_signal",
                symbol=event.symbol,
            )

            return

        Telemetry.event(
            "signal_generated",
            symbol=signal.symbol,
            confidence=signal.confidence,
        )

        if not self.validation.validate(signal):

            Telemetry.event(
                "signal_rejected",
                reason="validation",
            )

            return

        Telemetry.event(
            "validation_passed",
            symbol=signal.symbol,
        )

        if not self.risk.approve(signal):

            Telemetry.event(
                "signal_rejected",
                reason="risk",
            )

            return

        Telemetry.event(
            "risk_approved",
            symbol=signal.symbol,
        )

        quantity = self.risk.calculate_position_size(signal)

        order = Order(
            symbol=signal.symbol,
            side=signal.side,
            quantity=quantity,
        )

        self.execution.submit(order)

        Telemetry.event(
            "order_submitted",
            symbol=order.symbol,
            quantity=order.quantity,
        )


# ============================================================
# Example
# ============================================================

if __name__ == "__main__":

    coordinator = TradingCoordinator()

    coordinator.process(
        MarketEvent(
            symbol="BTCUSDT",
            price=108_350,
            timestamp=datetime.utcnow(),
        )
    )
```
