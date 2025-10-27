import os
import mailbox
import json
from email.header import decode_header, make_header
from bs4 import BeautifulSoup
from dateutil import parser
import re

# === 설정 ===
mbox_dir = "/home/eunjo/Desktop/Outlook_LLM_v3"
output_path = os.path.join(mbox_dir, "data", "outlook_raw.jsonl")
os.makedirs(os.path.dirname(output_path), exist_ok=True)

# === 유틸리티 함수 ===
def decode_mime_words(s):
    if not s:
        return ""
    try:
        return str(make_header(decode_header(s)))
    except:
        decoded = decode_header(s)
        return ''.join([
            part.decode(enc or 'utf-8', errors='ignore') if isinstance(part, bytes) else str(part)
            for part, enc in decoded
        ])

def parse_address_list(address_str):
    if not address_str:
        return []
    addresses = decode_mime_words(address_str).replace('\n', ' ').replace('\t', ' ').split(',')
    clean_list = []
    for addr in addresses:
        addr = addr.strip()
        if addr:
            if '<' in addr and '>' in addr:
                email = addr[addr.rfind('<')+1:addr.rfind('>')].strip()
            else:
                email = addr.strip()
            if email:
                clean_list.append(email)
    return clean_list

def extract_name_email_map(from_str, to_str, cc_str):
    combined = ','.join(filter(None, [from_str, to_str, cc_str]))
    combined = decode_mime_words(combined)
    name_email_pairs = re.findall(r'(?:"?([^"<@]+)"?\s*)?<([^@]+@[^>]+)>', combined)
    return {name.strip(): email.strip() for name, email in name_email_pairs if name and email}

def get_body_from_msg(msg):
    plain_text = ""
    html_text = ""
    rtf_content = ""

    if msg.is_multipart():
        for part in msg.walk():
            ctype = part.get_content_type()
            if ctype == "text/plain" and "attachment" not in str(part.get("Content-Disposition", "")):
                try:
                    return part.get_payload(decode=True).decode('utf-8', errors='ignore')
                except:
                    continue
            elif ctype == "text/html" and "attachment" not in str(part.get("Content-Disposition", "")):
                try:
                    html = part.get_payload(decode=True).decode('utf-8', errors='ignore')
                    soup = BeautifulSoup(html, "html.parser")
                    html_text = soup.get_text('\n', strip=True)
                except:
                    html_text = html
            elif ctype == "application/rtf":
                rtf_content = "[RTF_BODY_CANDIDATE]"
    else:
        try:
            return msg.get_payload(decode=True).decode('utf-8', errors='ignore')
        except:
            pass

    return plain_text or html_text or rtf_content or ""

def extract_attachment_filenames(msg):
    filenames = []
    for part in msg.walk():
        content_disposition = str(part.get("Content-Disposition", ""))
        filename = part.get_filename()
        if "attachment" in content_disposition and filename:
            decoded_filename = decode_mime_words(filename)
            if decoded_filename.lower() != "rtf-body.rtf":
                filenames.append(decoded_filename)
    return filenames

# === 메시지 처리 ===
message_ids_seen = set()

with open(output_path, 'w', encoding='utf-8') as out_file:
    for month in range(1, 13):
        month_str = f"{month:02d}"
        mbox_filename = f"2021 {month_str}.mbox"
        mbox_path = os.path.join(mbox_dir, mbox_filename)

        if not os.path.exists(mbox_path):
            print(f"{mbox_filename} 파일 없음, 건너뜀")
            continue

        print(f"처리 중: {mbox_filename}...")
        try:
            for msg in mailbox.mbox(mbox_path):
                try:
                    raw_date = msg.get("date", "")
                    try:
                        parsed_date = parser.parse(raw_date)
                        date_iso = parsed_date.isoformat()
                        date_ymd = parsed_date.strftime("%Y-%m-%d")
                    except:
                        date_iso = raw_date
                        date_ymd = ""

                    message_id = decode_mime_words(msg.get("Message-ID"))
                    if message_id in message_ids_seen:
                        continue
                    message_ids_seen.add(message_id)

                    subject = decode_mime_words(msg.get("subject"))
                    from_raw = msg.get("from", "")
                    to_raw = msg.get("to", "")
                    cc_raw = msg.get("cc", "")
                    in_reply_to = decode_mime_words(msg.get("In-Reply-To"))
                    references = decode_mime_words(msg.get("References"))

                    thread_id = in_reply_to or references or message_id

                    record = {
                        "thread_id": thread_id,
                        "subject": subject,
                        "from": decode_mime_words(from_raw),
                        "to": decode_mime_words(to_raw),
                        "cc": decode_mime_words(cc_raw),
                        "from_list": parse_address_list(from_raw),
                        "to_list": parse_address_list(to_raw),
                        "cc_list": parse_address_list(cc_raw),
                        "date_raw": raw_date,
                        "date_iso": date_iso,
                        "date_ymd": date_ymd,
                        "message_id": message_id,
                        "in_reply_to": in_reply_to,
                        "references": references,
                        "body": get_body_from_msg(msg),
                        "attachments": extract_attachment_filenames(msg),
                        "name_email_map": extract_name_email_map(from_raw, to_raw, cc_raw)
                    }

                    out_file.write(json.dumps(record, ensure_ascii=False) + '\n')

                except Exception as e:
                    print(f"메시지 처리 오류: {e}")
        except Exception as e:
            print(f"파일 처리 실패: {e}")

print(f"\n모든 mbox 처리 완료! 저장 위치: {output_path}")