import json
import re
from bs4 import BeautifulSoup
from dateutil import parser
from dateutil.tz import tzutc
from tqdm import tqdm

INPUT_FILE = "/home/eunjo/Desktop/Outlook_LLM_v3/data/outlook_raw.jsonl"
OUTPUT_FILE = "/home/eunjo/Desktop/Outlook_LLM_v3/data/outlook_clean.jsonl"

seen_message_ids = set()

SIGNATURE_PATTERNS = [
    r"(?i)(--\s*|\nThanks[^\n]*|Best regards[^\n]*|Sent from [^\n]*|Regards[^\n]*)"
]
HISTORY_PATTERNS = [
    r"(?i)^[-\s]*Original Message[-\s]*$",
    r"(?i)^From: .+",
    r"(?i)^Sent: .+",
    r"(?i)^To: .+",
    r"(?i)^Subject: .+",
    r"(?i)^On .+ wrote:",
    r"(?i)^> .+",
]

def clean_whitespace(text):
    if not isinstance(text, str):
        return text
    return re.sub(r'\s+', ' ', text).strip()

def clean_list(lst):
    if not isinstance(lst, list):
        return lst
    return [clean_whitespace(item) for item in lst if isinstance(item, str)]

def clean_dict(dct):
    if not isinstance(dct, dict):
        return dct
    return {
        re.sub(r'^[,\s]+', '', clean_whitespace(k)): clean_whitespace(v)
        for k, v in dct.items()
        if isinstance(k, str) and isinstance(v, str)
    }

def clean_body(text):
    if not text:
        return ""
    soup = BeautifulSoup(text, "html.parser")
    text = soup.get_text()

    for pattern in HISTORY_PATTERNS:
        matches = list(re.finditer(pattern, text, flags=re.MULTILINE))
        if matches:
            text = text[:matches[0].start()]
            break

    for pattern in SIGNATURE_PATTERNS:
        text = re.split(pattern, text)[0]

    return clean_whitespace(text)

def normalize_date(iso_date_str):
    try:
        dt = parser.isoparse(iso_date_str)
        return dt.astimezone(tzutc()).isoformat()
    except Exception:
        return iso_date_str

with open(INPUT_FILE, 'r', encoding='utf-8') as infile, open(OUTPUT_FILE, 'w', encoding='utf-8') as outfile:
    for line in tqdm(infile, desc="Preprocessing emails"):
        try:
            email = json.loads(line)

            if "[SOCIAL NETWORK]" in email.get("subject", ""):
                continue

            msg_id = email.get("message_id")
            if msg_id in seen_message_ids:
                continue
            seen_message_ids.add(msg_id)

            # body
            email["body"] = clean_body(email.get("body", ""))

            # subject, from, to, cc, bcc, attachments, etc.
            for field in ["subject", "from", "to", "cc", "bcc", "attachments"]:
                if isinstance(email.get(field), list):
                    email[field] = clean_list(email.get(field))
                elif isinstance(email.get(field), str):
                    email[field] = clean_whitespace(email.get(field))

            # name_email_map 딕셔너리 정제
            if "name_email_map" in email:
                email["name_email_map"] = clean_dict(email["name_email_map"])

            # 날짜
            email["date_iso"] = normalize_date(email.get("date_iso", ""))
            email.pop("date_display", None)
            email.pop("date_display_kst", None)

            outfile.write(json.dumps(email, ensure_ascii=False) + "\n")

        except Exception as e:
            print(f"[ERROR] 처리 실패: {e}")