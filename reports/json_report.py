import json
from dataclasses import asdict
from pathlib import Path


def result_to_dict(result):
    return asdict(result)


def write_json_report(result, file_path):
    Path(file_path).parent.mkdir(parents=True, exist_ok=True)
    with open(file_path, "w", encoding="utf-8") as output:
        json.dump(result_to_dict(result), output, indent=2, default=str)


def write_error_report(input_file, error, file_path):
    Path(file_path).parent.mkdir(parents=True, exist_ok=True)
    report = {
        "file": str(input_file),
        "verdict": "UNKNOWN",
        "error": str(error),
    }
    with open(file_path, "w", encoding="utf-8") as output:
        json.dump(report, output, indent=2)


def write_verdict_log(entries, file_path):
    Path(file_path).parent.mkdir(parents=True, exist_ok=True)
    with open(file_path, "w", encoding="utf-8") as output:
        for filename, verdict in entries:
            output.write(f"{filename} -> {verdict}\n")