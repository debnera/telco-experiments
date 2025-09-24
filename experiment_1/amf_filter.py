#!/usr/bin/env python3
import sys
import re
from datetime import datetime

# Simple log summarizer for amf-like traces
# - Emits one compact line per detected key event
# - Annotates with tags and identifiers (IMSI, NAS event, NGAP, UE state, etc.)
# - Skips large payload blocks unless a key event occurs

TIMESTAMP_RE = re.compile(r'^\[(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}\.\d+)\]')
IMSI_RE = re.compile(r'IMSI\s+([A-Za-z0-9]+[-A-Za-z0-9]*)')
NAS_KEYS = [
    "Registration Request",
    "Registration Accept",
    "Registration Complete",
    "Authentication",
    "Security Mode",
]

def extract_imsi(line):
    m = IMSI_RE.search(line)
    if m:
        return m.group(1)
    m = re.search(r'IMSI[:\s]+(\d{6,20})', line)
    if m:
        return m.group(1)
    return None

def extract_timestamp(line):
    m = TIMESTAMP_RE.match(line)
    if m:
        ts_str = m.group(1)
        return ts_str
    return None

def print_event(event, last_event_ref, ts_str):
    # Avoid duplicates; print with the original log timestamp if available
    if event == last_event_ref:
        return
    ts_out = ts_str if ts_str is not None else datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    print(f"[{ts_out}] {event}")

def main():
    if len(sys.argv) > 1:
        infile = open(sys.argv[1], 'r')
    else:
        infile = sys.stdin

    last_event = None
    for line in infile:
        line = line.rstrip('\n')

        # Track and preserve line timestamp
        line_ts = extract_timestamp(line)

        # 1) IMSI seen
        imsi = extract_imsi(line)
        if imsi:
            ev = f"UE IMSI observed | {imsi}"
            print_event(ev, last_event, line_ts)
            last_event = ev
            continue

        # 2) NAS-related events
        if any(re.search(pat, line, re.IGNORECASE) for pat in NAS_KEYS):
            for pat in NAS_KEYS:
                if re.search(pat, line, re.IGNORECASE):
                    ev = f"NAS event | {pat}"
                    print_event(ev, last_event, line_ts)
                    last_event = ev
                    break
            continue
        if re.search(r'Registration', line, re.IGNORECASE) and re.search(r'(Request|Accept|Complete)', line, re.IGNORECASE):
            ev = "NAS event | Registration"
            print_event(ev, last_event, line_ts)
            last_event = ev
            continue
        if re.search(r'Authentication', line, re.IGNORECASE) or re.search(r'Security Mode', line, re.IGNORECASE):
            ev = "NAS event | Authentication / Security Mode"
            print_event(ev, last_event, line_ts)
            last_event = ev
            continue

        # 3) NGAP / NG Setup / UE context
        if re.search(r'NGSetup(Request|Response)', line, re.IGNORECASE):
            ev = "NGAP event | NG Setup"
            print_event(ev, last_event, line_ts)
            last_event = ev
            continue
        if re.search(r'Initial UE Message|InitialContextSetup', line, re.IGNORECASE):
            ev = "NGAP event | Initial UE / Context Setup"
            print_event(ev, last_event, line_ts)
            last_event = ev
            continue
        if re.search(r'gNB|Association', line, re.IGNORECASE):
            ev = "NGAP event | gNB/Association"
            print_event(ev, last_event, line_ts)
            last_event = ev
            continue

        # 4) UE state transitions
        if re.search(r'5GMM-REGISTERED|REGISTERED', line, re.IGNORECASE):
            ev = "UE state | 5GMM-REGISTERED"
            print_event(ev, last_event, line_ts)
            last_event = ev
            continue
        if re.search(r'CONNECTED|UE connected', line, re.IGNORECASE):
            ev = "UE connected"
            print_event(ev, last_event, line_ts)
            last_event = ev
            continue

        # 5) Context / PDU Session / SMF actions (high level)
        if re.search(r'Initial Context Setup Request', line, re.IGNORECASE):
            ev = "Context setup | Initial Context Setup Request"
            print_event(ev, last_event, line_ts)
            last_event = ev
            continue
        if re.search(r'Initial Context Setup Response', line, re.IGNORECASE):
            ev = "Context setup | Initial Context Setup Response"
            print_event(ev, last_event, line_ts)
            last_event = ev
            continue
        if re.search(r'SMF|PDUSession|PDU Session', line, re.IGNORECASE):
            ev = "SMF / PDU Session event"
            print_event(ev, last_event, line_ts)
            last_event = ev
            continue

        # 6) Errors / warnings
        if re.search(r'warning', line, re.IGNORECASE) or re.search(r'error', line, re.IGNORECASE) or "[error]" in line:
            tag = "Error/Warn"
            detail = line.strip()
            ev = f"{tag} | {detail}"
            print_event(ev, last_event, line_ts)
            last_event = ev
            continue

def __init__(self, *args, **kwargs):
    pass

if __name__ == "__main__":
    main()