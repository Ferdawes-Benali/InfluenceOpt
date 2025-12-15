"""Helpers to build graphs from CSV"""
import csv
import networkx as nx
from typing import Tuple

from .data_models import User, Edge


def build_graph_from_csv(users_csv: str, edges_csv: str) -> nx.Graph:
    G = nx.Graph()
    with open(users_csv, newline='', encoding='utf-8') as f:
        r = csv.DictReader(f)
        for row in r:
            uid = row['id']
            attrs = {
                'name': row.get('name', uid),
                'platform': row.get('platform', 'IG'),
                'followers': int(row.get('followers', 0)),
                'cost': float(row.get('cost', 0)),
                'risk': float(row.get('risk', 0)),
                'fake': float(row.get('fake', 0)),
                'age': int(row['age']) if row.get('age') else None,
                'region': row.get('region'),
                'gender': row.get('gender'),
                'eng_rate': float(row['eng_rate']) if row.get('eng_rate') else None,
            }
            G.add_node(uid, **attrs)
    with open(edges_csv, newline='', encoding='utf-8') as f:
        r = csv.DictReader(f)
        for row in r:
            G.add_edge(row['source'], row['target'], weight=float(row.get('weight', 1.0)), prob=float(row.get('prob', 1.0)))
    return G
