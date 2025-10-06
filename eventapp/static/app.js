document.addEventListener('DOMContentLoaded', function () {
    paypal.Buttons({
        createOrder: function (data, actions) {
            // Use the amount already calculated from URL params (totalAmount is from template)
            return actions.order.create({
                purchase_units: [{
                    amount: {
                        value: totalAmount.toString()
                    }
                }]
            });
        },
        onApprove: function (data, actions) {
            return actions.order.capture().then(function (details) {
                // Transaction is successfully captured
                var phoneInput = document.getElementById('phone').value;
                
                // Verify the transaction
                fetch('/verify_transaction', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({
                        orderID: data.orderID,
                        phone: phoneInput
                    }),
                })
                .then(response => response.json())
                .then(verifyData => {
                    if (verifyData.verified) {
                        // Handle successful verification
                        console.log("Transaction verified:", verifyData.details);
                        
                        // Get PayPal email and show verification popup
                        const paypalEmail = verifyData.details.payer?.email_address || '';
                        showEmailVerificationPopup(paypalEmail, data.orderID, phoneInput);
                    } else {
                        // Handle failed verification
                        console.error("Verification failed:", verifyData.reason);
                        alert("Verification failed. Please try again or contact support.");
                    }
                })
                .catch(error => {
                    console.error('Error verifying transaction:', error);
                    alert('Error verifying payment. Please contact support with order ID: ' + data.orderID);
                });
            });
        },
        onError: function (err) {
            console.error('PayPal error:', err);
            alert('Payment error occurred. Please try again.');
        }
    }).render('#paypal-button-container');
});

// Email verification popup just for papypal
function showEmailVerificationPopup(paypalEmail, orderID, phone) {
    // Create popup HTML
    const popupHTML = `
        <div id="emailVerifyPopup" style="
            position: fixed; 
            top: 0; left: 0; right: 0; bottom: 0; 
            background: rgba(0,0,0,0.8); 
            z-index: 9999; 
            display: flex; 
            align-items: center; 
            justify-content: center;
            padding: 1rem;
        ">
            <div style="
                background: white; 
                border-radius: 12px; 
                padding: 2rem; 
                max-width: 400px; 
                width: 100%;
                text-align: center;
                box-shadow: 0 10px 30px rgba(0,0,0,0.3);
            ">
                <h4 style="color: #667eea; margin-bottom: 1rem;">✅ Payment Successful!</h4>
                <p style="margin-bottom: 1rem;">Please verify your email address for receipts and updates:</p>
                
                <div style="margin-bottom: 1rem;">
                    <label style="font-weight: bold; display: block; margin-bottom: 0.5rem;">Email Address:</label>
                    <input type="email" id="verifyEmail" value="${paypalEmail}" style="
                        width: 100%; 
                        padding: 12px; 
                        border: 2px solid #e9ecef; 
                        border-radius: 8px; 
                        font-size: 1rem;
                        box-sizing: border-box;
                    ">
                    <small style="color: #6c757d; display: block; margin-top: 0.5rem;">
                        PayPal email: ${paypalEmail}
                    </small>
                </div>
                
                <div style="display: flex; gap: 10px; justify-content: center;">
                    <button onclick="proceedToReceipt('${orderID}', '${phone}', false)" style="
                        background: #6c757d; 
                        color: white; 
                        border: none; 
                        padding: 12px 20px; 
                        border-radius: 8px; 
                        font-weight: bold;
                        cursor: pointer;
                    ">Use PayPal Email</button>
                    
                    <button onclick="proceedToReceipt('${orderID}', '${phone}', true)" style="
                        background: #667eea; 
                        color: white; 
                        border: none; 
                        padding: 12px 20px; 
                        border-radius: 8px; 
                        font-weight: bold;
                        cursor: pointer;
                    ">Use Updated Email</button>
                </div>
            </div>
        </div>
    `;
    
    // Add to page
    document.body.insertAdjacentHTML('beforeend', popupHTML);
    
    // Focus on email input
    document.getElementById('verifyEmail').focus();
    document.getElementById('verifyEmail').select();
}

function proceedToReceipt(orderID, phone, useUpdatedEmail) {
    let emailParam = '';
    
    if (useUpdatedEmail) {
        const updatedEmail = document.getElementById('verifyEmail').value.trim();
        if (!updatedEmail || !updatedEmail.includes('@')) {
            alert('Please enter a valid email address.');
            return;
        }
        emailParam = `&email=${encodeURIComponent(updatedEmail)}`;
    }
    
    // Remove popup
    document.getElementById('emailVerifyPopup').remove();
    
    // Redirect to receipt with email parameter if provided
    window.location.href = `/receipt/${orderID}?event_id=${eventId}&tickets=${tickets}&phone=${encodeURIComponent(phone)}${emailParam}`;
}


