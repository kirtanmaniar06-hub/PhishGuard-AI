"""
PhishGuard AI — Random Forest Model Training Pipeline

Defines the training routine, builds a default dataset of representative
safe and phishing URLs, trains the Random Forest model, and saves the serialized file.
"""

import sys
from typing import List, Tuple
from app.ml.features import MLFeatureExtractor
from app.ml.classifier import PhishingClassifier

# A list of representative training URLs to seed the model with baseline knowledge
DEFAULT_TRAINING_DATA: List[Tuple[str, int]] = [
    # Safe URLs (Label: 0)
    ("https://www.google.com", 0),
    ("https://www.microsoft.com", 0),
    ("https://github.com", 0),
    ("https://stackoverflow.com", 0),
    ("https://www.amazon.com", 0),
    ("https://www.wikipedia.org", 0),
    ("https://www.paypal.com", 0),
    ("https://www.netflix.com", 0),
    ("https://www.apple.com", 0),
    ("https://www.linkedin.com", 0),
    ("https://news.ycombinator.com", 0),
    ("https://www.reddit.com", 0),
    ("https://www.bbc.com", 0),
    ("https://www.nytimes.com", 0),
    ("https://www.cnn.com", 0),
    ("https://www.dropbox.com", 0),
    ("https://slack.com", 0),
    ("https://zoom.us", 0),
    ("https://www.spotify.com", 0),
    ("https://www.ebay.com", 0),
    
    # Phishing URLs (Label: 1)
    ("http://login-paypal-verify-security.com", 1),
    ("http://secure-signin-chase-update.info", 1),
    ("http://netflix-billing-recovery.support", 1),
    ("http://login.microsoft-auth-update.xyz", 1),
    ("http://paypal-verification-account-confirm.net", 1),
    ("http://192.168.1.105/login.html", 1),
    ("http://apple-secure-id-support.org/login.php", 1),
    ("http://chasebank-account-signin-security.xyz", 1),
    ("http://wellsfargo-confirm-card-online.info", 1),
    ("http://login-facebook-account-recovery.com", 1),
    ("http://signin.amazon.security-alert-billing.net", 1),
    ("http://secure-billing-support-helpdesk.top", 1),
    ("http://login.google-account-verify-support.com", 1),
    ("http://dropbox-auth-share-view.cn", 1),
    ("http://bank-verification-billing-secure.com", 1),
    ("http://urgency-account-billing-support.net", 1),
    ("http://phish-secure-login-chase-update.com", 1),
    ("http://auth-paypal-confirm-billing.org", 1),
    ("http://signin-netflix-account-recovery.xyz", 1),
    ("http://evil-hack-virus-malicious-domain.net", 1),
]


def run_training() -> Tuple[float, float]:
    """
    Extracts features for the training data, trains the Random Forest classifier,
    evaluates simple training accuracy, and saves the trained model to disk.
    """
    extractor = MLFeatureExtractor()
    classifier = PhishingClassifier()

    X = []
    y = []

    for url, label in DEFAULT_TRAINING_DATA:
        vec = extractor.extract_vector(url)
        X.append(vec)
        y.append(label)

    # Train model
    classifier.train(X, y, n_estimators=50, max_depth=6)
    classifier.save_model()

    # Calculate simple training accuracy
    correct = 0
    for idx, (url, label) in enumerate(DEFAULT_TRAINING_DATA):
        pred_res = classifier.predict(url)
        pred_label = 1 if pred_res["prediction"] == "phishing" else 0
        if pred_label == label:
            correct += 1
            
    accuracy = correct / len(DEFAULT_TRAINING_DATA)
    return accuracy


if __name__ == "__main__":
    print("Extracting features and training Random Forest model...")
    acc = run_training()
    print(f"Training completed successfully. Base accuracy: {acc:.2%}")
