def test_migrate_repo_sessions(tmp_path):
    # create a repo-local sessions file and ensure it's migrated into app-data dir
    from gui.scenario_manager import ScenarioManager
    import os
    repo_local = os.path.abspath(os.path.join(os.path.dirname(__import__('gui.scenario_manager').__file__), '..', 'sessions'))
    os.makedirs(repo_local, exist_ok=True)
    fname = 'migrate-me.json'
    fpath = os.path.join(repo_local, fname)
    try:
        with open(fpath, 'w', encoding='utf-8') as f:
            f.write('{"migrated":1}')
        os.environ['INFLUENCEOPT_SESSIONS_DIR'] = str(tmp_path)
        mgr = ScenarioManager()
        target = os.path.join(str(tmp_path), fname)
        assert os.path.exists(target)
    finally:
        try:
            os.remove(fpath)
        except Exception:
            pass
