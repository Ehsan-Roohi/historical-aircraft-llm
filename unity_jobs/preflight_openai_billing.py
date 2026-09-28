"""One bounded, non-archival API billing probe before an expensive Astra run.

Reads OPENAI_API_KEY from the environment and never prints its value or the
model's text. The probe does not replace the archived design request.
"""

import json
import os
import re
import sys
import urllib.error
import urllib.request


def safe_label(value):
    return value if isinstance(value, str) and re.fullmatch(r"[a-z_0-9-]{1,80}", value) else None


def main():
    key = os.environ.get("OPENAI_API_KEY")
    if not key:
        print(json.dumps({"probe": "not_sent", "reason": "key_absent"}))
        return 2
    payload = {
        "model": "gpt-6-astra",
        "input": "Reply with OK.",
        "reasoning": {"effort": "low"},
        "max_output_tokens": 64,
        "store": False,
    }
    request = urllib.request.Request(
        "https://api.openai.com/v1/responses",
        data=json.dumps(payload).encode("utf-8"),
        headers={"Authorization": "Bearer " + key, "Content-Type": "application/json"},
        method="POST",
    )
    try:
        with urllib.request.urlopen(request, timeout=60) as response:
            data = json.load(response)
            print(json.dumps({"probe": "accepted", "http_status": response.status,
                              "model": data.get("model"), "status": data.get("status"),
                              "output_tokens": data.get("usage", {}).get("output_tokens")}))
            return 0
    except urllib.error.HTTPError as error:
        try:
            details = json.loads(error.read(2048)).get("error", {})
        except (ValueError, AttributeError):
            details = {}
        print(json.dumps({"probe": "rejected", "http_status": error.code,
                          "error_code": safe_label(details.get("code")),
                          "error_type": safe_label(details.get("type"))}))
        return 2
    except urllib.error.URLError as error:
        print(json.dumps({"probe": "uncertain", "error_type": type(error).__name__}))
        return 3


if __name__ == "__main__":
    sys.exit(main())
