"""
utils/email_sender.py

Crediwise — Email Integration via Gmail SMTP.

Setup:
    1. Go to Google Account → Security → 2-Step Verification → App Passwords
    2. Create an App Password for "Mail"
    3. Add to your .env file:
         CREDIWISE_EMAIL=shreeyavora37@gmail.com
         CREDIWISE_EMAIL_PASSWORD=udzlnixfblxczlwg
         CREDIWISE_SUPPORT_EMAIL=shreeyavora37@student.sfit.ac.in   # where you RECEIVE emails

    pip install python-dotenv  (if not already installed)
"""

import os
import smtplib
import traceback
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from pathlib import Path

try:
    from dotenv import load_dotenv
    load_dotenv(Path(__file__).parent.parent / ".env")
except ImportError:
    pass

# ── Config ────────────────────────────────────────────────────────────────────
SENDER_EMAIL    = os.getenv("CREDIWISE_EMAIL", "shreeyavora37@gmail.com")            # your Gmail address
SENDER_PASSWORD = os.getenv("CREDIWISE_EMAIL_PASSWORD", "gbnclwxsnecsuvpg")  # Gmail App Password (16 chars, no spaces)
SUPPORT_EMAIL   = os.getenv("CREDIWISE_SUPPORT_EMAIL", "shreeyavora37@student.sfit.ac.in")  # where you receive notifications


def _is_configured() -> bool:
    return bool(SENDER_EMAIL and SENDER_PASSWORD and "@" in SENDER_EMAIL)


def _send(subject: str, html_body: str, to: str, reply_to: str = "") -> tuple[bool, str]:
    """
    Core SMTP send function.
    Returns (success, error_message).
    """
    if not _is_configured():
        return False, "Email not configured. Add CREDIWISE_EMAIL and CREDIWISE_EMAIL_PASSWORD to .env"

    try:
        msg = MIMEMultipart("alternative")
        msg["Subject"] = subject
        msg["From"]    = f"Crediwise <{SENDER_EMAIL}>"
        msg["To"]      = to
        if reply_to:
            msg["Reply-To"] = reply_to

        msg.attach(MIMEText(html_body, "html"))

        with smtplib.SMTP_SSL("smtp.gmail.com", 465, timeout=10) as server:
            server.login(SENDER_EMAIL, SENDER_PASSWORD)
            server.sendmail(SENDER_EMAIL, to, msg.as_string())

        return True, ""
    except smtplib.SMTPAuthenticationError:
        return False, "Gmail authentication failed. Check your App Password in .env"
    except smtplib.SMTPException as e:
        return False, f"SMTP error: {e}"
    except Exception:
        return False, traceback.format_exc()


# ── Public API ─────────────────────────────────────────────────────────────────

def send_contact_notification(name: str, email: str, phone: str, subject: str, message: str) -> tuple[bool, str]:
    """
    Sends a notification email to SUPPORT_EMAIL when someone submits the contact form.
    Also sends a confirmation email to the user.
    """
    # 1. Internal notification to your team
    internal_html = f"""
    <div style="font-family:Arial,sans-serif;max-width:600px;margin:0 auto;border:1px solid #e2e8f0;border-radius:12px;overflow:hidden;">
        <div style="background:#003399;padding:24px 28px;">
            <h2 style="color:#fff;margin:0;font-size:1.2rem;">📬 New Contact Form Submission</h2>
            <p style="color:rgba(255,255,255,0.75);margin:6px 0 0;font-size:0.85rem;">Crediwise Contact Form</p>
        </div>
        <div style="padding:28px;">
            <table style="width:100%;border-collapse:collapse;">
                <tr><td style="padding:10px 0;border-bottom:1px solid #f1f5f9;font-weight:600;color:#475569;width:120px;">Name</td>
                    <td style="padding:10px 0;border-bottom:1px solid #f1f5f9;color:#1a2540;">{name}</td></tr>
                <tr><td style="padding:10px 0;border-bottom:1px solid #f1f5f9;font-weight:600;color:#475569;">Email</td>
                    <td style="padding:10px 0;border-bottom:1px solid #f1f5f9;"><a href="mailto:{email}" style="color:#003399;">{email}</a></td></tr>
                <tr><td style="padding:10px 0;border-bottom:1px solid #f1f5f9;font-weight:600;color:#475569;">Phone</td>
                    <td style="padding:10px 0;border-bottom:1px solid #f1f5f9;color:#1a2540;">{phone or "Not provided"}</td></tr>
                <tr><td style="padding:10px 0;border-bottom:1px solid #f1f5f9;font-weight:600;color:#475569;">Subject</td>
                    <td style="padding:10px 0;border-bottom:1px solid #f1f5f9;color:#1a2540;">{subject}</td></tr>
            </table>
            <div style="margin-top:20px;">
                <p style="font-weight:600;color:#475569;margin-bottom:8px;">Message</p>
                <div style="background:#f8faff;border:1px solid #e2e8f0;border-radius:8px;padding:16px;color:#334155;line-height:1.7;">
                    {message.replace(chr(10), "<br>")}
                </div>
            </div>
            <div style="margin-top:20px;padding:14px;background:#eff6ff;border-radius:8px;font-size:0.83rem;color:#1e40af;">
                ⏰ Please respond within 4 business hours as promised on the contact page.
            </div>
        </div>
        <div style="padding:16px 28px;background:#f8faff;font-size:0.78rem;color:#94a3b8;border-top:1px solid #e2e8f0;">
            Crediwise · AI Loan Intelligence · India &nbsp;|&nbsp; This is an automated notification.
        </div>
    </div>
    """
    ok1, err1 = _send(
        subject=f"[Crediwise Contact] {subject} — from {name}",
        html_body=internal_html,
        to=SUPPORT_EMAIL,
        reply_to=email,
    )

    # 2. Confirmation to the user
    user_html = f"""
    <div style="font-family:Arial,sans-serif;max-width:600px;margin:0 auto;border:1px solid #e2e8f0;border-radius:12px;overflow:hidden;">
        <div style="background:#003399;padding:24px 28px;">
            <h2 style="color:#fff;margin:0;font-size:1.2rem;">✅ We've received your message</h2>
            <p style="color:rgba(255,255,255,0.75);margin:6px 0 0;font-size:0.85rem;">Crediwise Support</p>
        </div>
        <div style="padding:28px;">
            <p style="color:#1a2540;font-size:0.96rem;line-height:1.7;">Hi <strong>{name.split()[0]}</strong>,</p>
            <p style="color:#475569;line-height:1.7;">
                Thank you for reaching out! We've received your message about <strong>"{subject}"</strong>
                and will get back to you at <strong>{email}</strong> within <strong>4 business hours</strong>.
            </p>
            <div style="background:#f0f5ff;border-left:4px solid #003399;border-radius:0 8px 8px 0;padding:14px 18px;margin:20px 0;color:#334155;font-size:0.88rem;line-height:1.65;">
                <strong>Your message:</strong><br><br>{message.replace(chr(10), "<br>")}
            </div>
            <p style="color:#475569;font-size:0.88rem;line-height:1.7;">
                If this is urgent, you can also reach us at <strong>1800-123-4567</strong>
                (Mon–Sat, 9 AM – 6 PM IST).
            </p>
        </div>
        <div style="padding:16px 28px;background:#f8faff;font-size:0.78rem;color:#94a3b8;border-top:1px solid #e2e8f0;">
            © 2025 Crediwise · AI Loan Intelligence · India &nbsp;|&nbsp; 🔒 256-bit SSL · ✅ RBI Compliant
        </div>
    </div>
    """
    ok2, err2 = _send(
        subject="We received your message — Crediwise Support",
        html_body=user_html,
        to=email,
    )

    if ok1:
        return True, ""
    return False, err1 or err2


def send_feedback_notification(name: str, email: str, fb_type: str, rating: str,
                                nps: int, message: str, features: list) -> tuple[bool, str]:
    """
    Sends feedback notification to SUPPORT_EMAIL when someone submits the feedback form.
    """
    features_str = ", ".join(features) if features else "None selected"
    internal_html = f"""
    <div style="font-family:Arial,sans-serif;max-width:600px;margin:0 auto;border:1px solid #e2e8f0;border-radius:12px;overflow:hidden;">
        <div style="background:#003399;padding:24px 28px;">
            <h2 style="color:#fff;margin:0;font-size:1.2rem;">⭐ New Feedback Received</h2>
            <p style="color:rgba(255,255,255,0.75);margin:6px 0 0;font-size:0.85rem;">Crediwise Feedback Form</p>
        </div>
        <div style="padding:28px;">
            <table style="width:100%;border-collapse:collapse;">
                <tr><td style="padding:10px 0;border-bottom:1px solid #f1f5f9;font-weight:600;color:#475569;width:160px;">Name</td>
                    <td style="padding:10px 0;border-bottom:1px solid #f1f5f9;color:#1a2540;">{name}</td></tr>
                <tr><td style="padding:10px 0;border-bottom:1px solid #f1f5f9;font-weight:600;color:#475569;">Email</td>
                    <td style="padding:10px 0;border-bottom:1px solid #f1f5f9;color:#1a2540;">{email or "Anonymous"}</td></tr>
                <tr><td style="padding:10px 0;border-bottom:1px solid #f1f5f9;font-weight:600;color:#475569;">Feedback Type</td>
                    <td style="padding:10px 0;border-bottom:1px solid #f1f5f9;color:#1a2540;">{fb_type}</td></tr>
                <tr><td style="padding:10px 0;border-bottom:1px solid #f1f5f9;font-weight:600;color:#475569;">Rating</td>
                    <td style="padding:10px 0;border-bottom:1px solid #f1f5f9;color:#1a2540;">⭐ {rating}</td></tr>
                <tr><td style="padding:10px 0;border-bottom:1px solid #f1f5f9;font-weight:600;color:#475569;">NPS Score</td>
                    <td style="padding:10px 0;border-bottom:1px solid #f1f5f9;color:#1a2540;">{nps}/10</td></tr>
                <tr><td style="padding:10px 0;border-bottom:1px solid #f1f5f9;font-weight:600;color:#475569;">Features Used</td>
                    <td style="padding:10px 0;border-bottom:1px solid #f1f5f9;color:#1a2540;">{features_str}</td></tr>
            </table>
            <div style="margin-top:20px;">
                <p style="font-weight:600;color:#475569;margin-bottom:8px;">Feedback Message</p>
                <div style="background:#f8faff;border:1px solid #e2e8f0;border-radius:8px;padding:16px;color:#334155;line-height:1.7;">
                    {message.replace(chr(10), "<br>")}
                </div>
            </div>
        </div>
        <div style="padding:16px 28px;background:#f8faff;font-size:0.78rem;color:#94a3b8;border-top:1px solid #e2e8f0;">
            Crediwise · AI Loan Intelligence · India
        </div>
    </div>
    """
    reply_to = email if email and "@" in email else ""
    return _send(
        subject=f"[Crediwise Feedback] {fb_type} · Rating: {rating} · NPS: {nps}/10",
        html_body=internal_html,
        to=SUPPORT_EMAIL,
        reply_to=reply_to,
    )


def is_email_configured() -> bool:
    """Call this in UI to decide whether to show 'email sent' or just success message."""
    return _is_configured()