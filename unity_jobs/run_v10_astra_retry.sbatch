#!/usr/bin/env bash
#SBATCH --job-name=aircraft-v10-astra-retry
#SBATCH --partition=cpu-preempt
#SBATCH --cpus-per-task=1
#SBATCH --mem=2G
#SBATCH --time=02:00:00
#SBATCH --output=aircraft-v10-astra-retry-%j.log
#SBATCH --mail-type=NONE
#SBATCH --no-requeue
set -euo pipefail
umask 077
project=/work/pi_roohie_umass_edu/wright1900-benchmark/wright1900
attempt="$project/v10_astra_retry01"
cd "$attempt"
set -a
source "$HOME/.config/wright1900/keys.env"
set +a
python -u run_v10_astra_retry.py \
  --attempt-dir "$attempt" \
  --transport-dir "$project"
