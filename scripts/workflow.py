"""Local stage ledger; file checks are not scientific approval or authentication."""
import argparse
import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def save(path, value):
    temp = path.with_suffix('.tmp')
    temp.write_text(json.dumps(value, ensure_ascii=False, indent=2) + '\n')
    temp.replace(path)

def initialize(project):
    project = Path(project)
    if project.exists() and any(project.iterdir()):
        raise ValueError('Project directory must be empty; existing research is preserved')
    project.mkdir(parents=True, exist_ok=True)
    spec = json.loads((ROOT / 'workflow.json').read_text())
    for stage in spec['stages']:
        folder = project / stage['id']
        folder.mkdir()
        stage.update(status='pending', hashes={})
    spec['history'] = []
    save(project / 'state.json', spec)
    return spec

def load(project):
    project = Path(project)
    state = json.loads((project / 'state.json').read_text())
    for stage in state['stages']:
        if stage['status'] == 'approved':
            for name, expected in stage['hashes'].items():
                path = project / stage['id'] / name
                if not path.is_file() or digest(path) != expected:
                    raise ValueError('Approved artifact changed: ' + stage['id'] + '/' + name)
    return state

def current(state):
    return next((s for s in state['stages'] if s['status'] != 'approved'), None)

def decide(project, decision, actor, note):
    if decision not in ('approved', 'revision_required', 'rejected'):
        raise ValueError('Unknown decision')
    if not actor.strip() or not note.strip():
        raise ValueError('Researcher identity and rationale are required')
    state = load(project)
    stage = current(state)
    if stage is None:
        raise ValueError('All stages already approved')
    if stage['status'] == 'rejected':
        raise ValueError('Rejected project is stopped; start an explicitly revised project')
    hashes = {}
    if decision == 'approved':
        for name in (stage['artifact'], stage['review']):
            path = Path(project) / stage['id'] / name
            if not path.is_file() or not path.read_text().strip():
                raise ValueError('Missing or empty artifact: ' + str(path))
            hashes[name] = digest(path)
    stage.update(status=decision, hashes=hashes)
    state['history'].append(dict(stage=stage['id'], decision=decision, actor=actor,
                                note=note, utc=datetime.now(timezone.utc).isoformat(), hashes=hashes))
    save(Path(project) / 'state.json', state)
    return state

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('command', choices=['init', 'status', 'decide'])
    parser.add_argument('--project', type=Path, required=True)
    parser.add_argument('--decision', choices=['approved', 'revision_required', 'rejected'])
    parser.add_argument('--by', dest='actor')
    parser.add_argument('--note')
    args = parser.parse_args()
    try:
        if args.command == 'init':
            state = initialize(args.project)
        elif args.command == 'decide':
            if not all((args.decision, args.actor, args.note)):
                parser.error('decide requires --decision, --by and --note')
            state = decide(args.project, args.decision, args.actor, args.note)
        else:
            state = load(args.project)
        print(json.dumps({'current': current(state), 'history_count': len(state['history']),
                          'complete': current(state) is None}, ensure_ascii=False, indent=2))
    except (ValueError, OSError, KeyError) as error:
        parser.exit(1, str(error) + '\n')

if __name__ == '__main__':
    main()
