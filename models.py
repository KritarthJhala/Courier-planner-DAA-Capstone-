"""Data models for the Mini-Courier Planner (Phase 1 design)."""
from dataclasses import dataclass


@dataclass
class Parcel:
    """A parcel to deliver.

    pid       : unique id
    dest      : graph node (delivery point) the parcel must reach
    weight    : integer weight in kg (knapsack weight)
    priority  : 1 (low) .. 5 (urgent customer tier)
    deadline  : hours from now by which it must be delivered
    """
    pid: int
    dest: str
    weight: int
    priority: int
    deadline: int

    @property
    def value(self) -> int:
        """Knapsack value: higher priority and tighter deadline => more valuable
        to put on the *current* trip. Range roughly 10..74."""
        return self.priority * 10 + max(0, 24 - self.deadline)
