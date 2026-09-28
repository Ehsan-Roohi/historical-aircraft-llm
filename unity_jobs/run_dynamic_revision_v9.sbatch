#!/usr/bin/env bash
#SBATCH --job-name=aircraft-dynamics-v9
#SBATCH --partition=cpu
#SBATCH --array=0-2%3
#SBATCH --cpus-per-task=1
#SBATCH --mem=2G
#SBATCH --time=02:00:00
#SBATCH --output=aircraft-dynamics-v9-%A_%a.log
#SBATCH --mail-type=NONE
#SBATCH --no-requeue
set -euo pipefail
umask 077
project=/work/pi_roohie_umass_edu/wright1900-benchmark/wright1900
cd "$project/dynamic_revision_v9_attempt01"
set -a
source "$HOME/.config/wright1900/keys.env"
set +a
models=(gpt-6-astra claude-fable-5-1 claude-opus-5-5)
python -u run_dynamic_revision_v9.py \
  --model "${models[$SLURM_ARRAY_TASK_ID]}" \
  --prompt-dir prompts \
  --output-dir responses \
  --transport-dir "$project"
