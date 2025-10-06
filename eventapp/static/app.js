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
                        // Redirect to receipt page with all necessary URL parameters
                        window.location.href = `/receipt/${data.orderID}?event_id=${eventId}&tickets=${tickets}&phone=${encodeURIComponent(phoneInput)}`;
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


