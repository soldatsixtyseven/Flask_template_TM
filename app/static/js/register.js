function restrictInputToDigits(event) {
    const input = event.target;
    const value = input.value.replace(/[^\d+]/g, '');
    input.value = value;
}

function formatPhoneNumber(event) {
    const input = event.target;
    const value = input.value.replace(/[^\d ]/g, '');
    const trimmedValue = value.replace(/\s+/g, '');
    const formattedValue = trimmedValue.replace(/(\d{2})(\d{2})(\d{3})(\d{2})(\d{2})/, '+$1 $2 $3 $4 $5');
    input.value = formattedValue.trim();
}

function updatePhoneCode() {
    const countrySelect = document.getElementById('country');
    const phoneInput = document.getElementById('telephone');
    const countryCode = countrySelect.options[countrySelect.selectedIndex].dataset.code;
    phoneInput.value = countryCode;
    const exampleNumber = countrySelect.options[countrySelect.selectedIndex].dataset.example;
    phoneInput.placeholder = exampleNumber;
}