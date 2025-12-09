# PayPal Webhook Setup Guide

This guide walks you through setting up the PayPal webhook-driven booking system to eliminate dropped bookings.

## 🎯 Overview

The new system ensures that **ONLY PayPal webhooks create bookings**, making the system 100% reliable even if users close their browsers or experience network issues.

### Key Changes Made:

1. ✅ **Webhook endpoint**: `/paypal/webhook` handles `PAYMENT.CAPTURE.COMPLETED` events
2. ✅ **Idempotent booking creation**: Prevents duplicates, handles retries safely  
3. ✅ **Frontend metadata**: PayPal orders now include booking data in `custom_id`
4. ✅ **Read-only receipt page**: Shows "processing" until webhook creates booking
5. ✅ **Webhook verification**: Validates PayPal signatures (optional for testing)

---

## 🛠 Environment Variables

Add these to your environment (.env file or server config):

```bash
# Existing PayPal vars
PAYPAL_CLIENT_ID=your_sandbox_client_id
PAYPAL_CLIENT_SECRET=your_sandbox_client_secret
PAYPAL_API_BASE=https://api-m.sandbox.paypal.com

# NEW: Webhook verification (optional for testing)
PAYPAL_WEBHOOK_ID=your_webhook_id_from_paypal_dashboard
```

---

## 🚀 Testing with Ngrok

### Step 1: Start Your Flask App
```bash
python app.py
# App should be running on localhost:5000
```

### Step 2: Start Ngrok
```bash
ngrok http 5000
# Copy the HTTPS URL (e.g., https://abc123.ngrok-free.app)
```

### Step 3: Test Webhook Endpoint
```bash
python test_webhook.py
# Enter your ngrok webhook URL when prompted
# Example: https://abc123.ngrok-free.app/paypal/webhook
```

### Step 4: Register Webhook in PayPal

1. Go to [PayPal Developer Dashboard](https://developer.paypal.com/developer/applications)
2. Select your sandbox application
3. Go to "Webhooks" tab
4. Click "Add Webhook"
5. **Webhook URL**: `https://your-ngrok-url.ngrok-free.app/paypal/webhook`
6. **Event types**: Select only `PAYMENT.CAPTURE.COMPLETED`
7. Save and copy the Webhook ID

### Step 5: Test Full Flow

1. Use the booking form on your site
2. Complete PayPal payment in sandbox
3. Check that webhook receives the event
4. Verify booking is created in database
5. Check that emails are sent (admin + customer)

---

## 🔍 Webhook Event Flow

```
1. Customer completes PayPal payment
   ↓
2. PayPal sends PAYMENT.CAPTURE.COMPLETED webhook
   ↓  
3. Webhook extracts order_id and custom_id metadata
   ↓
4. Webhook creates: Customer → Booking → Payment
   ↓
5. Webhook sends: Admin notification + Customer receipt
   ↓
6. Customer receipt page shows QR code
```

---

## ⚠ Important Notes

### Frontend Changes
- **PayPal orders now include metadata** in `custom_id` field
- **Receipt page is read-only** - shows "processing" until webhook completes
- **Auto-refresh** every 5 seconds until booking appears

### Backend Changes  
- **Only webhook creates bookings** - `/receipt` route is now read-only
- **Idempotent design** - webhook can be retried safely
- **Comprehensive logging** for debugging

### Database
- **No schema changes needed** - uses existing Booking, Customer, Payment models
- **order_id uniqueness** prevents duplicate bookings

---

## 📋 Testing Checklist

- [ ] Flask app starts without errors
- [ ] Ngrok tunnel is active  
- [ ] Webhook endpoint responds to test script
- [ ] PayPal webhook is registered and active
- [ ] Test payment creates booking via webhook
- [ ] Receipt page shows "processing" then full receipt
- [ ] Admin receives notification email
- [ ] Customer receives receipt email with QR code
- [ ] Browser refresh/close doesn't affect booking creation

---

## 🐛 Troubleshooting

### Webhook Not Receiving Events
- Check ngrok is running and HTTPS URL is correct
- Verify webhook is registered in PayPal dashboard  
- Check webhook event type is `PAYMENT.CAPTURE.COMPLETED`
- Look at Flask logs for incoming requests

### Booking Not Created
- Check webhook logs in Flask console
- Verify `custom_id` metadata is present in PayPal order
- Check database for partial records (customer, payment)
- Look for Python errors in webhook processing

### Email Issues
- Check SMTP settings in Flask config
- Verify recipient email addresses
- Look for email-specific errors in logs
- Test email settings independently

### Signature Verification Fails
- Set `PAYPAL_WEBHOOK_ID` environment variable
- For testing, webhook allows missing webhook_id
- Check PayPal documentation for signature format

---

## 🚢 Production Deployment

1. **Replace ngrok with real domain**: Update webhook URL in PayPal
2. **Environment variables**: Set all required vars on production server
3. **Webhook monitoring**: Add logging/alerting for webhook failures  
4. **Load testing**: Ensure webhook can handle concurrent payments
5. **Fallback monitoring**: Alert if bookings aren't created within X minutes

---

## 📞 Support

If you encounter issues:

1. Check the Flask console logs for errors
2. Test the webhook endpoint independently with `test_webhook.py`
3. Verify PayPal sandbox transactions are completing successfully
4. Check database for partial records that indicate where the process failed

The webhook system is designed to be bulletproof - if a webhook fails, PayPal will retry it automatically, and our idempotent design ensures duplicate bookings won't be created.