import imaplib
import email
from email.header import decode_header
import pickle
from sklearn.feature_extraction.text import TfidfVectorizer

# Email account credentials
EMAIL = "your-email@gmail.com"
PASSWORD = "your-password"

# Gmail IMAP settings
IMAP_SERVER = "imap.gmail.com"
IMAP_PORT = 993

# Path to your trained model and vectorizer
MODEL_PATH = "trained_model.pkl"
VECTORIZER_PATH = "vectorizer.pkl"

# Load the model
def load_model():
    with open(MODEL_PATH, "rb") as f:
        model = pickle.load(f)
    print("Model loaded successfully!")
    return model

# Load the vectorizer (if necessary)
def load_vectorizer():
    with open(VECTORIZER_PATH, "rb") as f:
        vectorizer = pickle.load(f)
    print("Vectorizer loaded successfully!")
    return vectorizer

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

def fetch_emails(mail, folder="inbox", max_emails=10, model=None, vectorizer=None):
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

                    # Combine subject and body into the email text
                    email_text = subject + " " + body
                    print(f"Fetching email: {subject}")

                    # Preprocess the email text using the vectorizer
                    email_features = vectorizer.transform([email_text])

                    # Predict using the trained model
                    prediction = model.predict(email_features)[0]
                    label = "Spam" if prediction == 1 else "Not Spam"

                    # Print the result with the email content
                    print(f"Subject: {subject}")
                    print(f"Body: {body}")
                    print(f"Prediction: {label}")
                    print("-" * 50)

    except Exception as e:
        print(f"Failed to fetch emails: {e}")

def main():
    # Load the model and vectorizer
    model = load_model()
    vectorizer = load_vectorizer()

    # Connect to the email server and fetch emails
    mail = connect_to_email()
    if mail:
        fetch_emails(mail, folder="inbox", max_emails=5, model=model, vectorizer=vectorizer)
        mail.logout()

if __name__ == "__main__":
    main()
