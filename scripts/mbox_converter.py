import os
import mailbox
import json
from email.header import decode_header
from bs4 import BeautifulSoup  # HTML 본문 파싱

def decode_mime_words(s):
    if not s:
        return ""
    decoded = decode_header(s)
    return ''.join([
        part.decode(enc or 'utf-8') if isinstance(part, bytes) else part
        for part, enc in decoded
    ])

def get_body_from_msg(msg):
    """본문 추출 (text/plain 우선, 없으면 text/html fallback)"""
    if msg.is_multipart():
        for part in msg.walk():
            if part.get_content_type() == "text/plain" and "attachment" not in str(part.get("Content-Disposition", "")):
                return part.get_payload(decode=True).decode('utf-8', errors='ignore')
        for part in msg.walk():
            if part.get_content_type() == "text/html":
                html = part.get_payload(decode=True).decode('utf-8', errors='ignore')
                try:
                    return BeautifulSoup(html, "html.parser").get_text()
                except:
                    return html
    else:
        try:
            return msg.get_payload(decode=True).decode('utf-8', errors='ignore')
        except:
            return ""
    return ""

def extract_attachments(msg):
    """첨부파일 메타데이터 추출"""
    attachments = []
    for part in msg.walk():
        content_disposition = str(part.get("Content-Disposition", ""))
        if "attachment" in content_disposition:
            filename = part.get_filename()
            content_type = part.get_content_type()
            payload = part.get_payload(decode=True)
            size = len(payload) if payload else 0
            attachments.append({
                "filename": decode_mime_words(filename) if filename else None,
                "content_type": content_type,
                "size_bytes": size
            })
    return attachments

# === 실행 부분 ===
mbox_dir = "/home/eunjo/Desktop/Outlook_LLM"
output_path = os.path.join(mbox_dir, "data/outlook_2021.jsonl")

# 대상 파일: "2021 01.mbox" ~ "2021 12.mbox"
with open(output_path, 'w', encoding='utf-8') as out:
    for month in range(1, 13):
        mbox_filename = f"2021 {month:02d}.mbox"
        mbox_path = os.path.join(mbox_dir, mbox_filename)

        if not os.path.exists(mbox_path):
            print(f"⚠️ {mbox_filename} 파일 없음. 스킵.")
            continue

        print(f"📦 처리 중: {mbox_filename}...")
        try:
            mbox = mailbox.mbox(mbox_path)
            for msg in mbox:
                try:
                    record = {
                        "subject": decode_mime_words(msg.get("subject")),
                        "from": decode_mime_words(msg.get("from")),
                        "to": decode_mime_words(msg.get("to")),
                        "date": msg.get("date", ""),
                        "body": get_body_from_msg(msg),
                        "attachments": extract_attachments(msg)
                    }
                    out.write(json.dumps(record, ensure_ascii=False) + '\n')
                except Exception as e:
                    print(f"❌ 메시지 처리 오류 (무시): {e}")
        except Exception as e:
            print(f"🚨 파일 열기 실패: {mbox_filename}, 오류: {e}")

print(f"\n✅ 전체 변환 완료! ➤ 결과 파일: {output_path}")