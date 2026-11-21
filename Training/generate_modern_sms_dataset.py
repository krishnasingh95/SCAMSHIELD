"""
Generate modern Smishing (SMS Scam) and modern Legitimate (Ham) dataset
specifically covering Indian and global real-world attack vectors:
1. Bank Account Suspension / Block / KYC / PAN linking (SBI, HDFC, ICICI, Axis, PNB, etc.)
2. Electricity Bill Disconnection threats (Power office, 9:30 PM cut, fake officer contact)
3. Income Tax / Government refund scams
4. Traffic e-Challan / Court summons threats
5. Courier / Customs / India Post / FedEx delivery fee fraud
6. Work-from-home / Telegram / YouTube like & earn job scams
7. KBC / Lottery / Cash prize / Reward points expiration
8. Malicious APK updates (SBI YONO, WhatsApp Pink)
9. Defanged variants (hxxp://, bit[dot]ly, [dot], [:])
10. Modern Indian HAM messages (real transactional SMS, OTPs, utility receipts, food delivery, IRCTC, personal chats)
"""

import random
import csv
from pathlib import Path

BANKS = ["SBI", "HDFC Bank", "ICICI Bank", "Axis Bank", "PNB", "Canara Bank", "Bank of Baroda", "Kotak Bank", "Union Bank"]
SHORT_URLS = [
    "http://bit.ly/{slug}",
    "https://tinyurl.com/{slug}",
    "http://is.gd/{slug}",
    "https://rb.gy/{slug}",
    "http://cutt.ly/{slug}",
    "http://sbi-pan-kyc.in/{slug}",
    "https://hdfc-netbanking-verify.top/{slug}",
    "http://icici-kyc-update.xyz/{slug}",
    "http://netbanking-alert.club/{slug}",
    "http://power-bill-pay.site/{slug}",
    "http://echallan-parivahan.online/{slug}",
    "http://customs-clearance.cc/{slug}",
    # Defanged variants
    "hxxp://bit[dot]ly/{slug}",
    "hxxps://tinyurl[dot]com/{slug}",
    "hxxp://sbi-verify[dot]top/{slug}",
    "hxxps://kyc-update[dot]xyz/{slug}",
]

NAMES = ["Rahul", "Priya", "Amit", "Sneha", "Rohan", "Ananya", "Vikram", "Pooja", "Suresh", "Deepak"]
AMOUNTS = ["12,450", "25,000", "5,490", "15,800", "50,000", "2,50,000", "5,00,000", "1,200", "850", "180"]
OFFICER_NAMES = ["Mr. Sharma", "Officer Rajesh", "R.K. Verma", "P.K. Mishra", "S.K. Gupta"]

def random_slug():
    chars = "abcdefghijklmnopqrstuvwxyz0123456789"
    return "".join(random.choices(chars, k=random.randint(6, 10)))

def random_phone():
    return f"{random.choice(['9', '8', '7'])}{random.randint(100000000, 999999999)}"

def generate_samples():
    random.seed(42)
    records = []

    # ─────────────────────────────────────────────────────────────
    # 1. BANKING / KYC / ACCOUNT SUSPENSION SCAMS (Spam)
    # ─────────────────────────────────────────────────────────────
    bank_scam_templates = [
        "{bank} ALERT: Your account will be blocked today. Verify immediately at {url} to avoid suspension.",
        "Dear Customer, your {bank} net banking account has been locked due to pending KYC! Update immediately at {url} to prevent account closure.",
        "Dear Customer, your {bank} account has been suspended due to PAN card not linked. Please click here {url} to update immediately.",
        "{bank} WARNING: Your debit card ending in {last4} has been blocked due to suspicious activity. Verify details at {url} to unblock.",
        "Important notification from {bank}: Your account #XX{last4} is scheduled for deactivation within 24 hours. Submit KYC documents here: {url}",
        "Dear User, your {bank} YONO account is locked. Download update app to reactivate: {url}",
        "Urgent Notice: Your {bank} credit card points of Rs. {amount} will expire today. Redeem immediately into cash at {url}",
        "Dear customer, your {bank} savings account is temporarily frozen. Call bank officer at +91-{phone} or update KYC at {url}",
        "{bank} Security Alert: Unauthorized login attempt from New Delhi. If this wasn't you, verify identity immediately at {url}",
        "Action Required: Your {bank} A/C will be permanently closed by midnight due to non-verification of Aadhaar. Link now at {url}",
        "Dear customer, congratulations! You have pre-approved loan of Rs. {amount} from {bank}. Click to claim in 10 mins: {url}",
        "{bank} SMS Alert: Immediate action required. Your online banking services are disabled. Visit {url} to reactivate without visiting branch.",
    ]

    for bank in BANKS:
        for tmpl in bank_scam_templates:
            for _ in range(4):
                slug = random_slug()
                url_t = random.choice(SHORT_URLS).format(slug=slug)
                text = tmpl.format(
                    bank=bank,
                    url=url_t,
                    last4=random.randint(1000, 9999),
                    amount=random.choice(AMOUNTS),
                    phone=random_phone(),
                )
                records.append(("spam", text))

    # ─────────────────────────────────────────────────────────────
    # 2. ELECTRICITY BILL DISCONNECTION SCAMS (Spam)
    # ─────────────────────────────────────────────────────────────
    power_boards = ["electricity office", "Electricity Department", "Power Corporation", "BSES", "BESCOM", "TNEB", "Mahavitaran", "UPPCL"]
    power_templates = [
        "Dear consumer, your electricity power will be disconnected tonight at 9:30 PM from {board} because your previous month bill was not updated. Please immediately contact our electricity officer {officer} at {phone}.",
        "URGENT: Electricity bill unpaid for connection #{conn_id}. Supply will be cut at 10:00 PM today. Pay immediately via {url} or call {phone}.",
        "Notice: Power disconnection ordered for meter #{conn_id}. To avoid power cut tonight, immediately update payment at {url} or call electricity office {phone}.",
        "Dear consumer your bill is pending. Your power will be disconnected tonight. Call electricity officer at +91-{phone} immediately.",
        "Alert: Your light connection will be disconnected tonight by 8:30 PM from head office. Contact electricity helpline at {phone} to stop disconnection.",
    ]

    for board in power_boards:
        for tmpl in power_templates:
            for _ in range(3):
                slug = random_slug()
                url_t = random.choice(SHORT_URLS).format(slug=slug)
                text = tmpl.format(
                    board=board,
                    officer=random.choice(OFFICER_NAMES),
                    phone=random_phone(),
                    conn_id=random.randint(10000000, 99999999),
                    url=url_t,
                )
                records.append(("spam", text))

    # ─────────────────────────────────────────────────────────────
    # 3. INCOME TAX & GOVERNMENT REFUNDS (Spam)
    # ─────────────────────────────────────────────────────────────
    tax_templates = [
        "Income Tax Department Alert: An IT refund of Rs. {amount} has been approved for your PAN. Confirm your bank account details at {url} to disburse funds.",
        "Dear Taxpayer, refund of Rs. {amount} has been processed for AY 2025-26. Click {url} to verify bank account for instant transfer.",
        "Govt of India PM-Kisan Yojana: Rs. {amount} credited to your beneficiary wallet. Verify Aadhaar to withdraw: {url}",
        "EPFO Notice: Unclaimed PF balance of Rs. {amount} detected on your UAN. Submit online claim form before deadline: {url}",
    ]

    for tmpl in tax_templates:
        for _ in range(15):
            slug = random_slug()
            url_t = random.choice(SHORT_URLS).format(slug=slug)
            text = tmpl.format(
                amount=random.choice(["15,490", "28,750", "42,100", "8,920"]),
                url=url_t,
            )
            records.append(("spam", text))

    # ─────────────────────────────────────────────────────────────
    # 4. TRAFFIC E-CHALLAN / COURT THREATS (Spam)
    # ─────────────────────────────────────────────────────────────
    challan_templates = [
        "Traffic Police Alert: Pending e-Challan of Rs. {fine} recorded against vehicle DL{r1}AB{r2}. Pay within 24 hours to avoid court summons: {url}",
        "E-Challan Notice: Speed violation recorded. Fine Rs. {fine}. Non-payment will lead to DL suspension and warrant. Pay now at {url}",
        "Court Notice: Legal summons issued in case #CR-{r2} for unpaid penalties. View case files and settle immediately: {url}",
        "Delhi Police Traffic Unit: Unpaid violation challan pending on your vehicle. Clear fine before vehicle impoundment: {url}",
    ]

    for tmpl in challan_templates:
        for _ in range(12):
            slug = random_slug()
            url_t = random.choice(SHORT_URLS).format(slug=slug)
            text = tmpl.format(
                fine=random.choice(["500", "1,000", "2,000", "5,000"]),
                r1=random.randint(1, 9),
                r2=random.randint(1000, 9999),
                url=url_t,
            )
            records.append(("spam", text))

    # ─────────────────────────────────────────────────────────────
    # 5. COURIER / CUSTOMS / INDIA POST (Spam)
    # ─────────────────────────────────────────────────────────────
    courier_templates = [
        "India Post Notice: Your parcel #{trk} cannot be delivered due to incomplete address. Update address within 24h at {url} or parcel will be returned.",
        "FedEx Express: Parcel #{trk} is on hold at customs clearance. Outstanding duty fee of Rs. {fee} required: {url}",
        "BlueDart Courier: Shipment delivery failed. Reschedule delivery date and verify contact info at {url}",
        "Customs Notice: Your international parcel has been intercepted. Pay duty penalty of Rs. {fee} at {url} to avoid legal seizure.",
    ]

    for tmpl in courier_templates:
        for _ in range(12):
            slug = random_slug()
            url_t = random.choice(SHORT_URLS).format(slug=slug)
            text = tmpl.format(
                trk=f"IN{random.randint(1000000, 9999999)}",
                fee=random.choice(["48", "99", "149", "250"]),
                url=url_t,
            )
            records.append(("spam", text))

    # ─────────────────────────────────────────────────────────────
    # 6. JOB / PART-TIME / TELEGRAM / WORK FROM HOME (Spam)
    # ─────────────────────────────────────────────────────────────
    job_templates = [
        "Earn Rs. 3,000 to Rs. 8,000 daily working 1-2 hours from mobile. Just like YouTube videos & rate hotels. WhatsApp now: https://wa.me/91{phone}",
        "Hiring Part-Time: Amazon/Flipkart review tasks. Daily payout Rs. {amount}. No experience needed. Join Telegram channel: {url}",
        "Part-time job offer: Work from home and earn Rs. {amount} per day. Contact hiring manager on WhatsApp: +91-{phone}",
        "Dear {name}, your resume has been shortlisted for international remote data entry job. Daily income Rs. 5,000. Apply at {url}",
    ]

    for tmpl in job_templates:
        for _ in range(12):
            slug = random_slug()
            url_t = random.choice(SHORT_URLS).format(slug=slug)
            text = tmpl.format(
                phone=random_phone(),
                amount=random.choice(["2,500", "4,000", "6,500"]),
                name=random.choice(NAMES),
                url=url_t,
            )
            records.append(("spam", text))

    # ─────────────────────────────────────────────────────────────
    # 7. LOTTERY / KBC / CASH PRIZE SCAMS (Spam)
    # ─────────────────────────────────────────────────────────────
    lottery_templates = [
        "Dear Customer, congratulations! Your mobile number won Rs. 25,00,000 in KBC Jio Lucky Draw 2026. Call KBC Manager {officer} at +91-{phone} to claim.",
        "Congratulations! You won a cash reward of Rs. {amount} from Google Pay scratch card. Claim reward straight to bank: {url}",
        "Dear winner, you have won Rs. 50 Lakhs in WhatsApp mega lottery. Contact lottery office at {phone} to receive your cheque.",
        "Lucky Draw Winner: Your SIM card #XX{last4} is chosen for Tata Safari car or cash prize. Claim today at {url}",
    ]

    for tmpl in lottery_templates:
        for _ in range(12):
            slug = random_slug()
            url_t = random.choice(SHORT_URLS).format(slug=slug)
            text = tmpl.format(
                amount=random.choice(["25,000", "50,000", "1,00,000"]),
                officer=random.choice(OFFICER_NAMES),
                phone=random_phone(),
                last4=random.randint(1000, 9999),
                url=url_t,
            )
            records.append(("spam", text))

    # ─────────────────────────────────────────────────────────────
    # 8. LEGITIMATE MODERN INDIAN HAM MESSAGES (Ham)
    # ─────────────────────────────────────────────────────────────
    # Real transactional debits & credits
    ham_bank_templates = [
        "Dear Customer, INR {amount}.00 debited from A/C XX{last4} on {day}-Nov-26 at ATM WDL. Avail Bal: INR {bal}.00. - {bank}",
        "Dear Customer, your A/C XX{last4} is credited with INR {amount}.00 on {day}-Nov-26 by UPI. Avail Bal: INR {bal}.00. - {bank}",
        "{bank}: Payment of INR {amount}.00 to Swiggy via UPI reference #{upi_ref} is successful. Available Balance: INR {bal}.00.",
        "{otp} is your secret OTP for transaction of INR {amount}.00 at Amazon Pay. Valid for 10 mins. Do not share with anyone. - {bank}",
        "{bank} Alert: Account XX{last4} has been registered for NetBanking. If not done by you, call 1800-425-3800.",
        "Your {bank} credit card ending in {last4} statement for month of Oct is ready. Total due: INR {amount}. Due date: 28-Nov-26.",
        "Dear Customer, your cheque #{chk} for INR {amount}.00 has been cleared in your A/C XX{last4}. - {bank}",
    ]

    for bank in BANKS:
        for tmpl in ham_bank_templates:
            for _ in range(4):
                text = tmpl.format(
                    bank=bank,
                    last4=random.randint(1000, 9999),
                    amount=random.choice(["450", "1,200", "3,500", "14,800", "500"]),
                    bal=random.choice(["24,510", "68,900", "12,430", "1,05,200"]),
                    day=random.randint(1, 28),
                    upi_ref=random.randint(100000000000, 999999999999),
                    otp=random.randint(100000, 999999),
                    chk=random.randint(100000, 999999),
                )
                records.append(("ham", text))

    # Real OTPs and Service Notifications
    ham_service_templates = [
        "{otp} is your verification code for logging into Swiggy. Valid for 5 minutes. Never share this code with anyone.",
        "{otp} is your OTP to login to Zomato. Do not share it with anyone, including delivery partners.",
        "Dear User, your Uber ride OTP is {otp_short}. Please share this OTP with driver once you board the vehicle.",
        "{otp} is your OTP for Flipkart account verification. Valid for 10 minutes. - Flipkart",
        "Your Amazon package #AMZ-{last4} is out for delivery today. Delivery agent will arrive between 2 PM and 5 PM.",
        "Your Domino's pizza order has been placed successfully and is being baked. Order ID: #{last4}.",
        "PNR {pnr} Confirmed. Train 12952 Rajdhani Express from NDLS to BCT. Coach B3 Berth 42. Happy Journey - IRCTC",
        "Your Airtel monthly mobile bill of Rs. 499 for number 98XXXXXX{last4} is generated. Due date is 25-Nov-26.",
        "You have consumed 100% of your daily 1.5 GB high speed data quota. Data speed will be reduced to 64 Kbps. - Jio",
    ]

    for tmpl in ham_service_templates:
        for _ in range(12):
            text = tmpl.format(
                otp=random.randint(100000, 999999),
                otp_short=random.randint(1000, 9999),
                last4=random.randint(1000, 9999),
                pnr=random.randint(1000000000, 9999999999),
            )
            records.append(("ham", text))

    # Real utility bill receipts and legitimate bill notices
    ham_bill_templates = [
        "Dear consumer, payment of Rs. {amount} for electricity bill CA {conn_id} received with thanks on {day}-Nov-26. - BSES",
        "Dear BESCOM consumer, your electricity bill of Rs. {amount} for account {conn_id} is generated. Due date: {day}-Nov-26. Pay online at official portal bescom.karnataka.gov.in",
        "Tata Power: Payment received for consumer #{conn_id}. Amount: Rs. {amount}. Thank you for timely payment.",
        "Adani Electricity: Bill of Rs. {amount} for CA #{conn_id} is due on {day}-Nov-26. Pay via Adani Electricity app.",
        "Dear Customer, your Airtel broadband bill of Rs. {amount} for account {conn_id} is due on {day}-Nov-26. Pay on Airtel Thanks app.",
        "Mahanagar Gas: Your PNG gas bill of Rs. {amount} for CA #{conn_id} is due on {day}-Nov-26. Pay via mgl.com.",
        "Dear Customer, your payment of Rs. {amount} for Tata Play DTH account {conn_id} was successful. Balance updated.",
        "HDFC Bank: Total payment of INR {amount} for credit card ending in {last4} is due on {day}-Nov-26. Pay via NetBanking.",
        "SBI Card: Payment of INR {amount} received towards your credit card ending in {last4} on {day}-Nov-26 with thanks.",
        "ICICI Bank: Minimum due for credit card XX{last4} is INR {amount}. Due date {day}-Nov-26. Net banking login at icicibank.com.",
    ]

    for tmpl in ham_bill_templates:
        for _ in range(15):
            records.append(("ham", tmpl.format(
                amount=random.choice(["450", "850", "1,240", "2,100", "3,400"]),
                conn_id=random.randint(10000000, 99999999),
                day=random.randint(10, 28),
                last4=random.randint(1000, 9999),
            )))

    for tmpl in ham_service_templates:
        for _ in range(12):
            text = tmpl.format(
                otp=random.randint(100000, 999999),
                otp_short=random.randint(1000, 9999),
                last4=random.randint(1000, 9999),
                pnr=random.randint(1000000000, 9999999999),
                amount=random.choice(["750", "1,240", "2,100"]),
                conn_id=random.randint(10000000, 99999999),
                day=random.randint(1, 28),
            )
            records.append(("ham", text))

    # Real personal/college conversations
    ham_personal = [
        "Hey {name}, are you coming to college tomorrow for the AIML lecture?",
        "Bro please send the lab experiment 4 writeup before 4 PM today.",
        "Let's meet at the campus cafeteria after the afternoon project review.",
        "Faculty said everyone must bring their printed synopsis tomorrow morning.",
        "Are we submitting the project report in hard copy or soft copy?",
        "I am at the library right now, let me know when you reach campus.",
        "Did you finish running the random forest training on the dataset?",
        "Hey, can you share the presentation slides link on WhatsApp?",
        "Yes, I will bring my laptop to class. See you tomorrow at 9 AM.",
        "Thanks a lot for the notes, that was really helpful for the exam!",
        "Sir has scheduled the viva for our batch on Wednesday at 11 AM.",
        "Mom said we should leave for home right after the seminar ends.",
    ]

    for tmpl in ham_personal:
        for _ in range(12):
            records.append(("ham", tmpl.format(name=random.choice(NAMES))))

    # Shuffle records
    random.shuffle(records)
    print(f"Generated {len(records)} augmentation records.")
    spam_cnt = sum(1 for r in records if r[0] == "spam")
    ham_cnt = sum(1 for r in records if r[0] == "ham")
    print(f"  Spam: {spam_cnt} | Ham: {ham_cnt}")

    out_file = Path("Training/datasets/raw/modern_smishing_augmentation.csv")
    out_file.parent.mkdir(parents=True, exist_ok=True)
    with open(out_file, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["label", "text"])
        for r in records:
            writer.writerow(r)
    print(f"Saved to {out_file}")

if __name__ == "__main__":
    generate_samples()
