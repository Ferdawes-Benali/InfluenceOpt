"""Data models for InfluenceOpt"""
from dataclasses import dataclass
from typing import Optional


@dataclass
class User:
    id: str
    name: str
    platform: str
    followers: int
    cost: float
    risk: float
    fake: float
    age: Optional[int] = None
    region: Optional[str] = None
    gender: Optional[str] = None
    eng_rate: Optional[float] = None


@dataclass
class Edge:
    source: str
    target: str
    weight: float = 1.0
    prob: float = 1.0
    delay_hours: Optional[float] = None


@dataclass
class Campaign:
    name: str
    budget: float
    risk_max: float
    coverage: float
    reach_weight: float
    platforms: Optional[list] = None
    notes: Optional[str] = None
