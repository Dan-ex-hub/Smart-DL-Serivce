document.addEventListener('DOMContentLoaded', function() {
    // Enable form validation
    const forms = document.querySelectorAll('.needs-validation');
    
    Array.from(forms).forEach(form => {
        form.addEventListener('submit', event => {
            if (!form.checkValidity()) {
                event.preventDefault();
                event.stopPropagation();
            }
            
            form.classList.add('was-validated');
        }, false);
    });
    
    // File upload preview
    const fileInput = document.getElementById('document');
    const filePreview = document.getElementById('document-preview');
    const fileLabel = document.getElementById('document-label');
    
    if (fileInput && fileLabel) {
        fileInput.addEventListener('change', function() {
            const fileName = this.files[0]?.name;
            if (fileName) {
                fileLabel.textContent = fileName;
            } else {
                fileLabel.textContent = 'Choose file';
            }
        });
    }
    
    // Date validation for test booking
    const testDateInput = document.getElementById('test_date');
    if (testDateInput) {
        // Set minimum date (7 days from now)
        const today = new Date();
        const minDate = new Date(today);
        minDate.setDate(today.getDate() + 7);
        
        // Set maximum date (60 days from now)
        const maxDate = new Date(today);
        maxDate.setDate(today.getDate() + 60);
        
        // Format dates for the input field
        const formatDate = date => {
            const year = date.getFullYear();
            const month = String(date.getMonth() + 1).padStart(2, '0');
            const day = String(date.getDate()).padStart(2, '0');
            return `${year}-${month}-${day}`;
        };
        
        testDateInput.setAttribute('min', formatDate(minDate));
        testDateInput.setAttribute('max', formatDate(maxDate));
    }
    
    // Enhance payment form validation
    const paymentForm = document.getElementById('payment-form');
    if (paymentForm) {
        const cardNumberInput = document.getElementById('card_number');
        const cardExpiryInput = document.getElementById('expiry_date');
        const cardCvvInput = document.getElementById('cvv');
        
        // Format card number with spaces
        if (cardNumberInput) {
            cardNumberInput.addEventListener('input', function() {
                // Remove non-digits
                let value = this.value.replace(/\D/g, '');
                
                // Limit to 16 digits
                if (value.length > 16) {
                    value = value.slice(0, 16);
                }
                
                // Format with spaces every 4 digits
                this.value = value.replace(/(\d{4})(?=\d)/g, '$1 ').trim();
            });
        }
        
        // Format expiry date as MM/YY
        if (cardExpiryInput) {
            cardExpiryInput.addEventListener('input', function() {
                // Remove non-digits
                let value = this.value.replace(/\D/g, '');
                
                // Limit to 4 digits
                if (value.length > 4) {
                    value = value.slice(0, 4);
                }
                
                // Format as MM/YY
                if (value.length > 2) {
                    this.value = value.slice(0, 2) + '/' + value.slice(2);
                } else {
                    this.value = value;
                }
            });
        }
        
        // Limit CVV to 3 digits
        if (cardCvvInput) {
            cardCvvInput.addEventListener('input', function() {
                // Remove non-digits
                let value = this.value.replace(/\D/g, '');
                
                // Limit to 3 digits
                if (value.length > 3) {
                    value = value.slice(0, 3);
                }
                
                this.value = value;
            });
        }
    }
});
