document.addEventListener('DOMContentLoaded', function() {
  const subscribeButtons = document.querySelectorAll('.subscribe-button');

  subscribeButtons.forEach(button => {
    button.addEventListener('click', function() {
      const form = this.closest('.subscription-form');
      const desiredPriceInput = form.querySelector('#desired-price');
      const desiredPrice = desiredPriceInput.value;
      const gpuId = form.querySelector('input[name="gpu-id"]').value;

      form.submit(); // Submit the form
    });
  });
});
