"""Scenario management for InfluenceOpt

Provides Scenario dataclass and utilities to store and compare scenarios.
"""
from dataclasses import dataclass, asdict
from typing import Dict, Any, List
import json
import networkx as nx


@dataclass
class Scenario:
    name: str
    params: Dict[str, Any]
    result: Dict[str, Any]

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


class ScenarioStore:
    def __init__(self) -> None:
        self.scenarios: List[Scenario] = []

    def add(self, s: Scenario) -> None:
        self.scenarios.append(s)

    def remove(self, idx: int) -> None:
        del self.scenarios[idx]

    def to_json(self) -> str:
        return json.dumps([s.to_dict() for s in self.scenarios], indent=2)

    def save_to_file(self, path: str) -> None:
        with open(path, 'w', encoding='utf-8') as f:
            f.write(self.to_json())

    def load_from_file(self, path: str) -> None:
        with open(path, 'r', encoding='utf-8') as f:
            arr = json.load(f)
        self.scenarios = [Scenario(**x) for x in arr]

    def compare_metrics(self, indices: List[int]) -> Dict[str, List[float]]:
        """Return metrics (budget, reach, risk, roi) for given scenario indices as lists."""
        metrics = {'budget': [], 'reach': [], 'risk': [], 'roi': []}
        for i in indices:
            s = self.scenarios[i]
            p = s.params
            r = s.result
            metrics['budget'].append(p.get('budget', 0.0))
            # reach: total followers reached if present in result or 0
            metrics['reach'].append(r.get('reach', r.get('total_followers', 0)))
            metrics['risk'].append(p.get('risk_max', 0.0))
            metrics['roi'].append(r.get('roi', 0.0))
        return metrics


def make_session_dict(graph: nx.Graph, params: Dict[str, Any], store: ScenarioStore) -> Dict[str, Any]:
    """Serialize graph, params and scenarios into a JSON-serializable dict."""
    nodes = []
    for n, d in graph.nodes(data=True):
        nd = {'id': n}
        nd.update({k: d[k] for k in d})
        nodes.append(nd)
    edges = []
    for u, v, d in graph.edges(data=True):
        ed = {'source': u, 'target': v}
        ed.update({k: d[k] for k in d})
        edges.append(ed)
    return {
        'nodes': nodes,
        'edges': edges,
        'params': params,
        'scenarios': [s.to_dict() for s in store.scenarios],
    }


def save_session(path: str, graph: nx.Graph, params: Dict[str, Any], store: ScenarioStore) -> None:
    d = make_session_dict(graph, params, store)
    with open(path, 'w', encoding='utf-8') as f:
        json.dump(d, f, indent=2)


def load_session(path: str) -> Dict[str, Any]:
    with open(path, 'r', encoding='utf-8') as f:
        d = json.load(f)
    # build graph
    G = nx.Graph()
    for nd in d.get('nodes', []):
        nid = nd.pop('id')
        G.add_node(nid, **nd)
    for ed in d.get('edges', []):
        u = ed.pop('source')
        v = ed.pop('target')
        G.add_edge(u, v, **ed)
    store = ScenarioStore()
    for s in d.get('scenarios', []):
        store.add(Scenario(**s))
    return {'graph': G, 'params': d.get('params', {}), 'store': store}


def save_named_session(name: str, base_dir: str, graph: nx.Graph, params: Dict[str, Any], store: ScenarioStore) -> str:
    """Save a named session under `base_dir/name.json`. Returns the path."""
    import os
    os.makedirs(base_dir, exist_ok=True)
    safe = f"{name}.json"
    path = os.path.join(base_dir, safe)
    save_session(path, graph, params, store)
    return path


def list_named_sessions(base_dir: str) -> List[Dict[str, Any]]:
    """List named sessions in base_dir returning dicts with name and path and mtime."""
    import os, glob, time
    out = []
    pattern = os.path.join(base_dir, "*.json")
    for p in glob.glob(pattern):
        try:
            st = os.stat(p)
            name = os.path.splitext(os.path.basename(p))[0]
            out.append({'name': name, 'path': p, 'mtime': st.st_mtime})
        except Exception:
            continue
    out.sort(key=lambda x: x['mtime'], reverse=True)
    return out


def load_named_session(name: str, base_dir: str) -> Dict[str, Any]:
    import os
    path = os.path.join(base_dir, f"{name}.json")
    if not os.path.exists(path):
        raise FileNotFoundError(path)
    return load_session(path)


def save_versioned_autosave(base_dir: str, graph: nx.Graph, params: Dict[str, Any], store: ScenarioStore, max_versions: int = 5) -> str:
    """Save an autosave with a timestamped filename and keep at most `max_versions` files."""
    import os, time, glob
    os.makedirs(base_dir, exist_ok=True)
    ts = int(time.time())
    fname = f"autosave-{ts}.json"
    path = os.path.join(base_dir, fname)
    save_session(path, graph, params, store)
    # prune older autosaves keeping newest `max_versions`
    pattern = os.path.join(base_dir, 'autosave-*.json')
    files = sorted(glob.glob(pattern), key=lambda p: os.stat(p).st_mtime, reverse=True)
    for f in files[max_versions:]:
        try:
            os.remove(f)
        except Exception:
            pass
    return path


def list_autosave_versions(base_dir: str) -> List[Dict[str, Any]]:
    """Return list of autosave files (name,path,mtime) sorted by mtime desc."""
    import os, glob
    pattern = os.path.join(base_dir, 'autosave-*.json')
    out = []
    for p in glob.glob(pattern):
        try:
            st = os.stat(p)
            name = os.path.basename(p)
            out.append({'name': name, 'path': p, 'mtime': st.st_mtime})
        except Exception:
            continue
    out.sort(key=lambda x: x['mtime'], reverse=True)
    return out


def get_default_appdir(app_name: str = 'InfluenceOpt') -> str:
    """Return a platform-appropriate sessions directory for the application.

    Can be overridden in tests or by setting the environment variable
    `INFLUENCEOPT_SESSIONS_DIR` to a custom path.
    """
    import os, sys
    env = os.environ.get('INFLUENCEOPT_SESSIONS_DIR')
    if env:
        return env
    if sys.platform.startswith('win'):
        base = os.environ.get('APPDATA') or os.path.expanduser('~')
        return os.path.join(base, app_name, 'sessions')
    if sys.platform == 'darwin':
        return os.path.join(os.path.expanduser('~/Library/Application Support'), app_name, 'sessions')
    # default: Linux / XDG
    base = os.environ.get('XDG_DATA_HOME') or os.path.expanduser('~/.local/share')
    return os.path.join(base, app_name, 'sessions')


def migrate_repo_sessions(repo_dir: str, target_dir: str) -> None:
    """Copy any session JSON files from a repo-local `repo_dir` into `target_dir`.

    This is idempotent and will not overwrite existing files in `target_dir`.
    """
    import os, glob, shutil
    if not os.path.exists(repo_dir):
        return
    os.makedirs(target_dir, exist_ok=True)
    pattern = os.path.join(repo_dir, '*.json')
    for p in glob.glob(pattern):
        dest = os.path.join(target_dir, os.path.basename(p))
        if not os.path.exists(dest):
            try:
                shutil.copy2(p, dest)
            except Exception:
                pass
