"""One hash-checked integrated dynamic redesign call per archived model."""
import argparse
import hashlib
import json
import os
import signal
import sys
from datetime import datetime, timezone
from pathlib import Path

MODELS = ('gpt-6-astra', 'claude-fable-5-1', 'claude-opus-5-5')
STAGE = 'v9_integrated_dynamics'


def sha(data):
    return hashlib.sha256(data).hexdigest()


def write_new(path, value):
    with path.open('x', encoding='utf-8') as stream:
        json.dump(value, stream, ensure_ascii=False, indent=2)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--model', choices=MODELS, required=True)
    parser.add_argument('--prompt-dir', type=Path, required=True)
    parser.add_argument('--output-dir', type=Path, required=True)
    parser.add_argument('--transport-dir', type=Path)
    parser.add_argument('--dry-run', action='store_true')
    args = parser.parse_args()
    manifest_bytes = (args.prompt_dir/'manifest.json').read_bytes()
    manifest = json.loads(manifest_bytes)
    if manifest['stage'] != STAGE or manifest['maximum_output_tokens'] != 20000:
        raise ValueError('Unexpected request manifest')
    rows = [row for row in manifest['records'] if row['model_requested'] == args.model]
    if len(rows) != 1 or rows[0]['sent'] is not False:
        raise ValueError('Expected one frozen unsent request')
    row = rows[0]
    if row['prompt_file'] != args.model+'.prompt.txt':
        raise ValueError('Unexpected prompt filename')
    prompt = (args.prompt_dir/row['prompt_file']).read_bytes()
    instructions = (args.prompt_dir/'instructions.txt').read_bytes()
    if sha(prompt) != row['prompt_sha256'] or sha(instructions) != manifest['instructions_sha256']:
        raise ValueError('Prompt or instruction hash mismatch')
    meta = {'stage': STAGE, 'model_requested': args.model,
            'prompt_sha256': sha(prompt), 'instructions_sha256': sha(instructions),
            'manifest_sha256': sha(manifest_bytes), 'maximum_calls': 1,
            'timeout_seconds': 5400, 'parent_v2_sha256': row['parent_v2_sha256'],
            'later_subsystem_sha256': row['later_subsystem_sha256']}
    if args.dry_run:
        print(json.dumps({**meta, 'dry_run': True, 'prompt_bytes': len(prompt)}))
        return 0
    if args.transport_dir is None or not hasattr(signal, 'SIGALRM'):
        raise RuntimeError('Linux transport and timeout required')
    transport = args.transport_dir.resolve()/'frontier_wright_eval.py'
    meta['transport_sha256'] = sha(transport.read_bytes())
    key_name = 'OPENAI_API_KEY' if args.model == MODELS[0] else 'ANTHROPIC_API_KEY'
    key = os.environ.get(key_name)
    if not key:
        raise RuntimeError('Required credential absent; no request sent')
    sys.path.insert(0, str(transport.parent))
    from frontier_wright_eval import generate
    args.output_dir.mkdir(parents=True, exist_ok=True)
    case = args.output_dir/args.model
    case.mkdir(exist_ok=False)
    meta.update(started_utc=datetime.now(timezone.utc).isoformat(),
                slurm_job_id=os.environ.get('SLURM_JOB_ID'))
    write_new(case/'request.json', meta)
    (case/'prompt.txt').write_bytes(prompt)
    (case/'instructions.txt').write_bytes(instructions)

    def expired(signum, frame):
        raise TimeoutError('Bounded model call expired')

    signal.signal(signal.SIGALRM, expired)
    signal.alarm(5400)
    try:
        result = generate(args.model, prompt.decode('utf-8'), 20000, key,
                          reasoning_effort='low',
                          instructions=instructions.decode('utf-8'))
        write_new(case/'response.json', result)
        complete = result.get('status') == 'completed' and bool(result.get('response'))
        outcome = {'status': 'completed' if complete else 'incomplete',
                   'response_sha256': sha((case/'response.json').read_bytes()),
                   'model_returned': result.get('model_returned'),
                   'engineering_validation': 'not_evaluated'}
    except Exception as error:
        outcome = {'status': 'error_or_uncertain', 'error_type': type(error).__name__,
                   'automatic_retry': False}
        complete = False
    finally:
        signal.alarm(0)
    outcome['finished_utc'] = datetime.now(timezone.utc).isoformat()
    write_new(case/'outcome.json', outcome)
    print(args.model, outcome['status'], flush=True)
    return 0 if complete else 2


if __name__ == '__main__':
    raise SystemExit(main())
