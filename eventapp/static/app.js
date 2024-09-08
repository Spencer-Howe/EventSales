document.addEventListener('DOMContentLoaded', function () {
    paypal.Buttons({
        createOrder: function (data, actions) {
            return actions.order.create({
                purchase_units: [{
                    amount: {
                        value: totalAmount // Use the dynamic amount
                    }
                }]
            });
        },
        onApprove: function (data, actions) {
            return actions.order.capture().then(function (details) {
                // Transaction is successfully captured
                // Now, send the order ID to your server for verification
                var phoneInput = document.getElementById('phone').value;
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
                    .then(data => {
                        if (data.verified) {
                            // Handle successful verification
                            console.log("Transaction verified:", data.details);
                            // Redirect to a receipt page
                            window.location.href = `/receipt/${data.orderID}`;
                        } else {
                            // Handle failed verification
                            console.error("Verification failed:", data.reason);
                            alert("Verification failed. Please try again or contact support.");
                        }
                    })
                    .catch(error => {
                        console.error('Error:', error);
                    });
            });
        }
    }).render('#paypal-button-container');
});


