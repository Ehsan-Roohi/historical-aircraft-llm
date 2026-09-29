#!/usr/bin/env bash
#SBATCH --job-name=aircraft-v12-install
#SBATCH --partition=cpu-preempt
#SBATCH --array=0-2%2
#SBATCH --cpus-per-task=1
#SBATCH --mem=2G
#SBATCH --time=02:00:00
#SBATCH --output=aircraft-v12-install-%A_%a.log
#SBATCH --mail-type=NONE
#SBATCH --no-requeue
set -euo pipefail
umask 077
project=/work/pi_roohie_umass_edu/wright1900-benchmark/wright1900
attempt="$project/v12_installation_attempt01"
cd "$attempt"
set -a
source "$HOME/.config/wright1900/keys.env"
set +a
models=(gpt-6-astra claude-fable-5-1 claude-opus-5-5)
python -u run_v12_installation.py \
  --model "${models[$SLURM_ARRAY_TASK_ID]}" \
  --attempt-dir "$attempt" \
  --transport-dir "$project"
