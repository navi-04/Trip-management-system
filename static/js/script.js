document.addEventListener('DOMContentLoaded', function() {
    // Add date validation
    const startDateInput = document.getElementById('start_date');
    const endDateInput = document.getElementById('end_date');
    
    if (startDateInput && endDateInput) {
        // Set minimum date as today
        const today = new Date().toISOString().split('T')[0];
        startDateInput.setAttribute('min', today);
        
        // Update end date min value when start date changes
        startDateInput.addEventListener('change', function() {
            endDateInput.setAttribute('min', this.value);
            
            // Reset end date if it's before start date
            if (endDateInput.value && endDateInput.value < this.value) {
                endDateInput.value = this.value;
            }
        });
    }
});
