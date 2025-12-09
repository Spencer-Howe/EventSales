document.addEventListener('DOMContentLoaded', function () {
    paypal.Buttons({
        createOrder: function (data, actions) {
            // Get form data for webhook metadata
            var phoneInput = document.getElementById('phone') ? document.getElementById('phone').value : '';
            var emailInput = document.getElementById('email') ? document.getElementById('email').value : '';
            
            // Create metadata for webhook processing
            var bookingMetadata = {
                event_id: eventId,
                tickets: tickets,
                phone: phoneInput,
                email: emailInput
            };
            
            return actions.order.create({
                purchase_units: [{
                    amount: {
                        value: totalAmount.toString()
                    },
                    custom_id: JSON.stringify(bookingMetadata)
                }]
            });
        },
        onApprove: function (data, actions) {
            return actions.order.capture().then(function (details) {
                // Transaction is successfully captured
                var phoneInput = document.getElementById('phone').value;
                var emailInput = document.getElementById('email') ? document.getElementById('email').value : '';
                
                // Verify the transaction and send instant receipt email
                fetch('/verify_transaction', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({
                        orderID: data.orderID,
                        phone: phoneInput,
                        email: emailInput,
                        event_id: eventId,
                        tickets: tickets
                    }),
                })
                .then(response => response.json())
                .then(verifyData => {
                    if (verifyData.verified) {
                        // Handle successful verification - go directly to receipt page
                        console.log("Transaction verified:", verifyData.details);
                        
                        // Redirect to receipt page with parameters
                        const receiptUrl = `/receipt/${data.orderID}?event_id=${eventId}&tickets=${tickets}&phone=${encodeURIComponent(phoneInput || '')}&email=${encodeURIComponent(emailInput || '')}`;
                        window.location.href = receiptUrl;
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



