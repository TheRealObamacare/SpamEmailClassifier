import imaplib
import email
from email.header import decode_header

# Email account credentials
EMAIL = "your-email@gmail.com"
PASSWORD = "your-password"

# Gmail IMAP settings
IMAP_SERVER = "imap.gmail.com"
IMAP_PORT = 993

def connect_to_email():
    try:
        # Establish a secure connection to the IMAP server
        mail = imaplib.IMAP4_SSL(IMAP_SERVER, IMAP_PORT)
        mail.login(EMAIL, PASSWORD)
        print("Logged in successfully!")
        return mail
    except Exception as e:
        print(f"Failed to connect: {e}")
        return None

def clean_text(text):
    # Helper function to clean and decode text
    try:
        text, encoding = decode_header(text)[0]
        if isinstance(text, bytes):
            text = text.decode(encoding or "utf-8")
    except Exception:
        pass
    return text

def fetch_emails(mail, folder="inbox", max_emails=10):
    try:
        # Select the mailbox (e.g., "inbox")
        mail.select(folder)

        # Search for all emails
        status, messages = mail.search(None, "ALL")
        email_ids = messages[0].split()

        # Fetch the latest emails (up to `max_emails`)
        for i in email_ids[-max_emails:]:
            res, msg = mail.fetch(i, "(RFC822)")
            for response_part in msg:
                if isinstance(response_part, tuple):
                    # Parse the raw email data
                    msg = email.message_from_bytes(response_part[1])

                    # Decode email subject
                    subject = clean_text(msg["subject"]) or "No Subject"

                    # Decode email body
                    body = ""
                    if msg.is_multipart():
                        for part in msg.walk():
                            content_type = part.get_content_type()
                            content_disposition = str(part.get("Content-Disposition"))

                            if content_type == "text/plain" and "attachment" not in content_disposition:
                                body = part.get_payload(decode=True).decode(errors="ignore").strip()
                                break
                    else:
                        # If it's a single-part email
                        body = msg.get_payload(decode=True).decode(errors="ignore").strip()

                    # Combine subject and body into the desired format
                    formatted_email = f"Subject: {subject} {body}"
                    print(formatted_email)
                    print("-" * 50)
    except Exception as e:
        print(f"Failed to fetch emails: {e}")

def main():
    mail = connect_to_email()
    if mail:
        fetch_emails(mail, folder="inbox", max_emails=5)
        mail.logout()

if __name__ == "__main__":
    main()
