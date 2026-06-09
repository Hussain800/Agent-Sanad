"""Run the full benchmark. Usage: python benchmark/run.py [path_to_workbook.xlsx]"""
import sys, json
from benchmark.normalize import load
from benchmark.replay import replay
from benchmark.score import score

def main(path):
    df = replay(load(path))
    out = {"all_years": score(df), "held_out_2025": score(df, 2025)}
    print(json.dumps(out, indent=2))
    return out

if __name__ == "__main__":
    p = sys.argv[1] if len(sys.argv) > 1 else "benchmark/data/RescheduleArrears.xlsx"
    main(p)
