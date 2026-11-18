import json
from pathlib import Path
from fastapi.testclient import TestClient
from app import app

client = TestClient(app)
config = json.loads(Path('config.json').read_text())


def test_metrics_file():
    m = json.loads(Path('artifacts/metrics.json').read_text())
    assert m['student_id'] == config['student_id']
    assert m['training_rows'] >= 100
    assert 0.5 <= m['accuracy'] <= 1.0


def test_metrics_endpoint():
    r = client.get('/metrics')
    assert r.status_code == 200
    for key in ['student_id', 'accuracy', 'training_rows', 'model_version', 'git_sha']:
        assert key in r.json()


def test_predict():
    record = {f: 0 for f in config['features']}
    r = client.post('/predict', json={'records': [record]})
    assert r.status_code == 200
    assert len(r.json()['predictions']) == 1
