"""
generate_dataset.py
--------------------
Generates a realistic synthetic customer-support dataset with:
    - customer query text
    - intent label      (Complaint, Refund, Technical Issue, Account Issue, Order Status, General Inquiry)
    - sentiment label    (Positive, Neutral, Negative)
    - expected response  (template-based agent reply)

Output: dataset/customer_support_dataset.csv  (>= 10,000 rows)
Also writes dataset/faq.csv used by the RAG / FAQ retrieval engine.

Run:
    python generate_dataset.py
"""

import csv
import random
from pathlib import Path

random.seed(42)

OUTPUT_DIR = Path(__file__).parent
N_ROWS = 10500

INTENTS = [
    "Complaint",
    "Refund",
    "Technical Issue",
    "Account Issue",
    "Order Status",
    "General Inquiry",
]

SENTIMENTS = ["Positive", "Neutral", "Negative"]

# ---------------------------------------------------------------------------
# Templates per intent, each with a sentiment tag so we can build realistic
# combinations. {product}, {order_id}, {days}, {amount} are filled in.
# ---------------------------------------------------------------------------
PRODUCTS = [
    "wireless headphones", "laptop charger", "smartphone", "running shoes",
    "coffee maker", "bluetooth speaker", "office chair", "backpack",
    "smartwatch", "gaming mouse", "monitor", "keyboard", "air fryer",
    "yoga mat", "desk lamp", "tablet", "router", "camera", "printer",
    "external hard drive",
]

TEMPLATES = {
    "Complaint": {
        "Negative": [
            "I am extremely disappointed with my {product}, it stopped working after {days} days.",
            "This is the worst {product} I have ever bought, completely unusable.",
            "My {product} arrived damaged and no one from support has responded in {days} days.",
            "I've complained about my {product} three times and nothing has been fixed.",
            "Absolutely furious, my {product} broke down and support keeps ignoring me.",
            "The {product} I purchased is defective and customer service has been terrible.",
        ],
        "Neutral": [
            "I want to file a complaint regarding the quality of my {product}.",
            "There seems to be an issue with my {product}, please look into it.",
            "I'm reporting a problem with the {product} I ordered order id {order_id}.",
        ],
    },
    "Refund": {
        "Negative": [
            "I demand a refund immediately for my {product}, it's been {days} days with no response.",
            "This {product} is faulty, I want my money of ${amount} back right now.",
            "I'm furious, refund my order {order_id} for the {product} now!",
        ],
        "Neutral": [
            "Can you process a refund for order {order_id}, the {product} did not meet my expectations.",
            "I would like to request a refund of ${amount} for my {product} purchase.",
            "Please initiate a refund for the {product} under order id {order_id}.",
            "How long does a refund for a {product} usually take to process?",
        ],
        "Positive": [
            "Thanks for approving my refund for the {product}, just confirming the amount ${amount}.",
        ],
    },
    "Technical Issue": {
        "Negative": [
            "My {product} keeps crashing and it's ruining my work, please help urgently.",
            "The app for my {product} won't connect and I've tried everything, so frustrating.",
            "I'm getting constant error messages on my {product}, this is unacceptable.",
        ],
        "Neutral": [
            "My {product} is not syncing with my phone, can you help me troubleshoot?",
            "I'm facing a technical issue where my {product} won't turn on.",
            "The firmware update for my {product} failed, what should I do?",
            "How do I reset my {product} to factory settings?",
            "My {product} shows a battery error, need technical assistance.",
        ],
    },
    "Account Issue": {
        "Negative": [
            "I've been locked out of my account for {days} days and nobody is helping me.",
            "Someone accessed my account without permission, this is a serious security issue.",
        ],
        "Neutral": [
            "I forgot my password and need help resetting my account.",
            "Can you update the email address linked to my account?",
            "I want to delete my account permanently, please guide me.",
            "My account shows incorrect billing information, please correct it.",
            "I am unable to log into my account since yesterday.",
            "How do I change my account phone number?",
        ],
    },
    "Order Status": {
        "Neutral": [
            "Can you tell me the current status of order {order_id}?",
            "When will my {product} from order {order_id} be delivered?",
            "I haven't received tracking info for my {product} order yet.",
            "Is my order {order_id} still on schedule for delivery in {days} days?",
            "Please provide an update on the shipping status of my {product}.",
        ],
        "Negative": [
            "My order {order_id} for the {product} is delayed by {days} days already!",
            "It's been {days} days and my {product} still hasn't shipped, unacceptable.",
        ],
        "Positive": [
            "Just checking, is order {order_id} for my {product} on track? Thanks!",
        ],
    },
    "General Inquiry": {
        "Neutral": [
            "Do you offer international shipping for the {product}?",
            "What is the warranty period on the {product}?",
            "Can you tell me more about the specifications of the {product}?",
            "Do you have the {product} available in different colors?",
            "What payment methods do you accept for buying a {product}?",
            "Is there a student discount available on the {product}?",
            "What are your customer support working hours?",
        ],
        "Positive": [
            "I love your {product}! Can you tell me if a newer version is coming soon?",
            "Great service so far, just wondering if the {product} comes with accessories.",
            "Your support team has been amazing, quick question about the {product} warranty.",
        ],
    },
}

RESPONSES = {
    "Complaint": "We're sorry to hear about the trouble with your {product}. We have logged your complaint and a support specialist will reach out within 24 hours to resolve this.",
    "Refund": "Your refund request for the {product} has been received. Refunds are typically processed within 5-7 business days to your original payment method.",
    "Technical Issue": "We understand the technical difficulty you're facing with your {product}. Please try restarting the device; if the issue persists, our technical team will assist you further.",
    "Account Issue": "We take account security and access seriously. Our team has been notified and will help you regain access or resolve the account issue shortly.",
    "Order Status": "Thank you for checking in. Your order is being processed and tracking details will be shared via email as soon as it ships.",
    "General Inquiry": "Thanks for reaching out! Here is the information you requested; feel free to ask if you need further clarification.",
}


def build_row():
    intent = random.choice(INTENTS)
    sentiment_options = list(TEMPLATES[intent].keys())
    sentiment = random.choice(sentiment_options)
    template = random.choice(TEMPLATES[intent][sentiment])

    product = random.choice(PRODUCTS)
    order_id = f"ORD{random.randint(100000, 999999)}"
    days = random.randint(1, 30)
    amount = round(random.uniform(15, 500), 2)

    query = template.format(product=product, order_id=order_id, days=days, amount=amount)
    response = RESPONSES[intent].format(product=product)

    return query, intent, sentiment, response


def main():
    rows = set()
    data = []
    while len(data) < N_ROWS:
        query, intent, sentiment, response = build_row()
        key = (query, intent, sentiment)
        if key in rows:
            continue
        rows.add(key)
        data.append([query, intent, sentiment, response])

    out_path = OUTPUT_DIR / "customer_support_dataset.csv"
    with open(out_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["query", "intent", "sentiment", "response"])
        writer.writerows(data)

    print(f"Generated {len(data)} rows -> {out_path}")

    # --------------------------------------------------------------
    # FAQ dataset used by the RAG / vector retrieval engine
    # --------------------------------------------------------------
    faqs = [
        ("What is your return policy?", "You can return any item within 30 days of delivery for a full refund, provided it is unused and in original packaging."),
        ("How long does shipping take?", "Standard shipping takes 3-5 business days. Express shipping takes 1-2 business days."),
        ("How do I track my order?", "You can track your order using the tracking link sent to your email, or by checking the 'Order Status' section in your account."),
        ("Do you ship internationally?", "Yes, we ship to over 50 countries. International delivery typically takes 7-14 business days."),
        ("How do I reset my password?", "Go to the login page and click 'Forgot Password'. You'll receive a reset link via email within a few minutes."),
        ("What payment methods are accepted?", "We accept all major credit/debit cards, UPI, PayPal, and net banking."),
        ("How do I cancel my order?", "You can cancel an order within 1 hour of placing it from the 'My Orders' page. After that, please contact support."),
        ("What is your warranty policy?", "Most electronics come with a 1-year manufacturer warranty covering defects in materials and workmanship."),
        ("How can I contact customer support?", "You can chat with us right here, email support@example.com, or call our 24/7 helpline."),
        ("Do you offer student discounts?", "Yes, students get 10% off with a valid student ID verified through our partner platform."),
        ("How do I update my shipping address?", "Go to Account Settings > Addresses to add or edit your shipping address before placing an order."),
        ("Can I change my order after placing it?", "Orders can be modified within 1 hour of placement. Please contact support immediately for changes."),
        ("What should I do if I received a damaged product?", "Please raise a complaint with photos of the damaged item within 48 hours of delivery for a replacement or refund."),
        ("How do refunds work?", "Refunds are credited to your original payment method within 5-7 business days after the returned item is received and inspected."),
        ("Is there a loyalty or rewards program?", "Yes, our Rewards Program lets you earn points on every purchase, redeemable for discounts on future orders."),
    ]
    faq_path = OUTPUT_DIR / "faq.csv"
    with open(faq_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["question", "answer"])
        writer.writerows(faqs)
    print(f"Generated {len(faqs)} FAQ entries -> {faq_path}")


if __name__ == "__main__":
    main()
