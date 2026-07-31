```python
"""
telemetry_example.py

Example of a lightweight telemetry implementation inspired by the
architecture used in the Quantum System IN A VERY SIMPLIFIED BASIC DEMO MANNER.

This example demonstrates:

- Structured logging
- Business events
- Metrics collection
- Latency measurement
- Context propagation
- Separation of telemetry from business logic

The implementation is intentionally simplified and does not expose
production infrastructure.
"""

from __future__ import annotations

import json
import logging
import time
from dataclasses import dataclass
from datetime import datetime
from functools import wraps
from typing import Callable, Dict


# ============================================================
# Logging
# ============================================================

logging.basicConfig(
    level=logging.INFO,
    format="%(message)s"
)

logger = logging.getLogger("quant-system")


# ============================================================
# Metrics
# ============================================================

class Metrics:

    counters: Dict[str, int] = {}

    @classmethod
    def increment(cls, metric: str):

        cls.counters.setdefault(metric, 0)
        cls.counters[metric] += 1

    @classmethod
    def dump(cls):

        print("\n=== Metrics ===")

        for metric, value in cls.counters.items():
            print(f"{metric:<30} {value}")


# ============================================================
# Telemetry
# ============================================================

@dataclass
class TelemetryContext:

    service: str
    exchange: str
    symbol: str


class Telemetry:

    @staticmethod
    def event(
        name: str,
        context: TelemetryContext,
        **fields,
    ):

        payload = {
            "timestamp": datetime.utcnow().isoformat(),
            "service": context.service,
            "exchange": context.exchange,
            "symbol": context.symbol,
            "event": name,
            **fields,
        }

        logger.info(json.dumps(payload))

        Metrics.increment(name)


# ============================================================
# Latency Decorator
# ============================================================

def measure_latency(metric_name: str):

    def decorator(func: Callable):

        @wraps(func)
        def wrapper(*args, **kwargs):

            started = time.perf_counter()

            result = func(*args, **kwargs)

            elapsed = (
                time.perf_counter() - started
            ) * 1000

            logger.info(
                json.dumps(
                    {
                        "event": "latency",
                        "metric": metric_name,
                        "latency_ms": round(elapsed, 2),
                    }
                )
            )

            Metrics.increment(metric_name)

            return result

        return wrapper

    return decorator


# ============================================================
# Example Business Service
# ============================================================

class ExecutionService:

    def __init__(self):

        self.context = TelemetryContext(
            service="execution-engine",
            exchange="bybit",
            symbol="BTCUSDT",
        )

    @measure_latency("execution_latency")
    def execute_trade(self):

        Telemetry.event(
            "signal_received",
            self.context,
            confidence=0.94,
        )

        Telemetry.event(
            "validation_passed",
            self.context,
        )

        Telemetry.event(
            "risk_check_completed",
            self.context,
            position_size=0.10,
        )

        Telemetry.event(
            "order_submitted",
            self.context,
            order_type="MARKET",
            side="BUY",
        )

        time.sleep(0.04)

        Telemetry.event(
            "order_filled",
            self.context,
            latency_ms=41,
        )

        Telemetry.event(
            "position_opened",
            self.context,
            stop_loss=True,
            take_profit=True,
        )


# ============================================================
# Example
# ============================================================

if __name__ == "__main__":

    service = ExecutionService()

    service.execute_trade()

    Metrics.dump()
```
