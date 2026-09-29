#!/usr/bin/env bash
#SBATCH --job-name=aircraft-v13-fable
#SBATCH --partition=cpu-preempt
#SBATCH --cpus-per-task=1
#SBATCH --mem=2G
#SBATCH --time=02:00:00
#SBATCH --output=aircraft-v13-fable-%j.log
#SBATCH --mail-type=NONE
#SBATCH --no-requeue
set -euo pipefail
umask 077
project=/work/pi_roohie_umass_edu/wright1900-benchmark/wright1900
attempt="$project/v13_fable_arithmetic_attempt01"
cd "$attempt"
set -a
source "$HOME/.config/wright1900/keys.env"
set +a
python -u run_v13_fable.py \
  --model claude-fable-5-1 \
  --attempt-dir "$attempt" \
  --transport-dir "$project"
