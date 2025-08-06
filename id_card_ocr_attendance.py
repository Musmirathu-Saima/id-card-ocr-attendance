import cv2
import pytesseract
import sqlite3
import re
import numpy as np

# Tesseract path for Mac (adjust if yours is different)
pytesseract.pytesseract.tesseract_cmd = '/usr/local/bin/tesseract'

# Connect to database
conn = sqlite3.connect('students.db')
cursor = conn.cursor()

# Preprocessing function for better OCR
def preprocess_image(image):
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    gray = cv2.resize(gray, None, fx=2, fy=2, interpolation=cv2.INTER_CUBIC)
    blur = cv2.GaussianBlur(gray, (5,5), 0)
    _, thresh = cv2.threshold(blur, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
    return thresh

# OCR Function
def extract_text(frame):
    processed = preprocess_image(frame)
    text = pytesseract.image_to_string(processed)
    print("\n[DEBUG] Extracted Text:\n", text)
    return text

# Match student details using regex and DB
def match_student(text):
    usn_match = re.search(r'1RG\d{2}CS\d{3}', text.upper())
    id_match = re.search(r'\b\d{4,5}\b', text)
    name_match = re.search(r'([A-Z][a-z]+\s[A-Z][a-z]+(\s[A-Z][a-z]+)?)', text)

    print("[DEBUG] USN Match:", usn_match)
    print("[DEBUG] ID No Match:", id_match)
    print("[DEBUG] Name Match:", name_match)

    if usn_match and id_match and name_match:
        usn = usn_match.group().upper()
        id_no = id_match.group()
        name = name_match.group()

        print(f"[INFO] Matched Details -> USN: {usn}, ID: {id_no}, Name: {name}")

        # Use LIKE for flexible name matching
        cursor.execute("SELECT * FROM students WHERE usn=? AND id_no=? AND name LIKE ?", (usn, id_no, name + "%"))
        student = cursor.fetchone()

        if student:
            cursor.execute("UPDATE students SET marked_present=1 WHERE usn=?", (usn,))
            conn.commit()
            print("[INFO] Marked Present in Database")
            return True, name, usn

    return False, None, None

# Open webcam
cap = cv2.VideoCapture(0)
print("[INFO] Show your ID card to the webcam. Press 'q' to quit.")

while True:
    ret, frame = cap.read()
    if not ret:
        break

    # Define ROI
    cv2.rectangle(frame, (50, 50), (600, 400), (0, 255, 0), 2)
    roi = frame[50:400, 50:600]

    # Extract & Match
    text = extract_text(roi)
    matched, name, usn = match_student(text)

    # Display result
    if matched:
        message = f"Marked Present: {name} ({usn})"
        color = (0, 255, 0)
    else:
        message = "Show valid ID card"
        color = (0, 0, 255)

    cv2.putText(frame, message, (30, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.8, color, 2)
    cv2.imshow("ID Card Scanner", frame)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
conn.close()
