"""
Assignment: Email Crime Investigation using MBOX File
-----------------------------------------------------
Aim:
To analyze emails from an MBOX file, detect spam mails, extract attachments,
and save a summary report in CSV format.
"""

# Import required libraries
import mailbox       # For reading .mbox email files
import os            # For file and folder operations
import csv           # For writing results into a CSV report
import base64        # For decoding attachments (if needed)
import time          # For unique filenames
from email.header import decode_header  # To decode email headers safely
from tqdm import tqdm                   # To show progress bar while processing

# ---------- Global Variables ----------
MBOX_FILE = "sample_mailbox.mbox"       # Input .mbox file
OUTPUT_DIR = "mbox_output"              # Folder where outputs are saved
SPAM_KEYWORDS = ["lottery", "win money", "prize", "free", "urgent", "click here"]  # Spam indicators


# ---------- Function 1: Clean and Decode Text ----------
def clean_text(text):
    """
    Decodes email headers (like From, To, Subject) which may be encoded.
    Converts them into readable strings.
    """
    if text is None:
        return ""
    decoded, charset = decode_header(text)[0]
    if isinstance(decoded, bytes):
        return decoded.decode(charset or "utf-8", errors="ignore")
    return decoded


# ---------- Function 2: Check if Email is Spam ----------
def classify_spam(subject, keywords):
    """
    Simple spam detector:
    If any keyword from SPAM_KEYWORDS appears in the subject → mark as Spam.
    """
    subject_lower = subject.lower()
    return any(keyword.lower() in subject_lower for keyword in keywords)


# ---------- Function 3: Extract Filename from Email ----------
def get_filename(msg):
    """
    Finds the file name of the attachment from email headers.
    Handles cases where filename may be inside Content-Disposition or Content-Type.
    """
    fname = "NO_FILENAME"
    if 'name=' in msg.get("Content-Disposition", ""):
        parts = msg.get("Content-Disposition").split(";")
        for p in parts:
            if "name=" in p:
                fname = p.split("=")[1].strip('"')
                break
    elif 'name=' in msg.get("Content-Type", ""):
        parts = msg.get("Content-Type").split(";")
        for p in parts:
            if "name=" in p:
                fname = p.split("=")[1].strip('"')
                break
    # Keep only safe characters in filename
    fname = "".join(c for c in fname if c.isalnum() or c in " ._-")
    return fname


# ---------- Function 4: Save Attachments ----------
def export_content(msg, out_dir, content):
    """
    Saves attachment content into the output directory.
    Adds timestamp to filename to prevent overwriting.
    """
    filename = get_filename(msg)
    if "." not in filename:
        ext = "bin"  # unknown file extension
    else:
        name, ext = filename.rsplit(".", 1)
        filename = f"{name}_{int(time.time())}.{ext}"
    path = os.path.join(out_dir, filename)
    with open(path, "wb") as f:
        f.write(content)
    return path


# ---------- Function 5: Extract Attachments Recursively ----------
def write_payload(msg, out_dir):
    """
    If email contains attachments, extracts and saves them.
    Handles multipart (emails with text + files).
    """
    paths = []
    if msg.is_multipart():
        for part in msg.get_payload():
            paths += write_payload(part, out_dir)  # Recursive call
    else:
        content_type = msg.get_content_type().lower()
        payload = msg.get_payload(decode=True)
        if payload and ("application/" in content_type or
                        "image/" in content_type or
                        "video/" in content_type or
                        "audio/" in content_type):
            paths.append(export_content(msg, out_dir, payload))
    return paths


# ---------- MAIN FUNCTION ----------
def main():
    """
    Reads all emails from an MBOX file.
    Extracts basic details, checks spam, saves attachments,
    and exports summary to CSV file.
    """
    # Create output directories
    if not os.path.exists(OUTPUT_DIR):
        os.makedirs(OUTPUT_DIR)
    attachments_dir = os.path.join(OUTPUT_DIR, "attachments")
    if not os.path.exists(attachments_dir):
        os.makedirs(attachments_dir)

    # Open and read the MBOX file
    mbox = mailbox.mbox(MBOX_FILE)
    print(f"Reading {len(mbox)} messages...")

    # Create CSV report
    csv_file = os.path.join(OUTPUT_DIR, "emails_report.csv")
    columns = ["From", "To", "Subject", "Date", "Spam", "Num_Attachments", "Attachment_Paths"]

    with open(csv_file, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=columns)
        writer.writeheader()

        # Process each email
        for msg in tqdm(mbox):
            from_ = clean_text(msg["From"]) or msg.get_from()
            to_ = clean_text(msg["To"])
            subject = clean_text(msg["Subject"])
            date_ = clean_text(msg["Date"])

            # Spam Detection
            spam_flag = "Yes" if classify_spam(subject, SPAM_KEYWORDS) else "No"

            # Extract attachments
            attachment_paths = write_payload(msg, attachments_dir)

            # Write all details to CSV
            writer.writerow({
                "From": from_,
                "To": to_,
                "Subject": subject,
                "Date": date_,
                "Spam": spam_flag,
                "Num_Attachments": len(attachment_paths),
                "Attachment_Paths": ", ".join(attachment_paths)
            })

    print(f"\nEmails processed successfully!")
    print(f"CSV report and attachments saved in: '{OUTPUT_DIR}'")


# ---------- Run Program ----------
if __name__ == "__main__":
    main()
