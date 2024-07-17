// initialize the payment amount
let originalAmount = parseFloat(document.getElementById("final_amount").value);
let currentAmount = originalAmount;
let giftCardBalance = 0;
let giftCardModal = new bootstrap.Modal(document.getElementById('giftCardModal'));
let giftCardId = null;

// update the payment amount
function updatePaymentAmount() {
    document.getElementById("amount").innerHTML = `<strong>Total: $${currentAmount.toFixed(2)}</strong>`;
    document.getElementById("cart_total_price").textContent = `$${currentAmount.toFixed(2)}`;
    document.getElementById("final_amount").value = currentAmount.toFixed(2);
    if (currentAmount === 0) {
        document.getElementById("payment_method").required = false;
    }
}

// update the gift card balance
function updateGiftCardBalance() {
    document.getElementById("gift_card_balance").innerHTML = `<strong>Your Gift Card Balance: $${giftCardBalance}</strong>`;
}

// Function to apply the promo code
function applyPromoCode() {
    const promoCode = document.getElementById("promo_code").value.trim();
    const promoMessageElement = document.getElementById("promo_message");
    const applyPromoButton = document.getElementById("apply_promo_button");

    if (!promoCode) {
        promoMessageElement.textContent = "Please enter a promo code.";
        promoMessageElement.style.color = "red";
        return;
    }

    applyPromoButton.disabled = true;           // Disable the Apply Promo Code button

    // Send a POST request to validate the promo code
    fetch("/accommodation/api/validate_promo", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ promo_code: promoCode })
    })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                const discountRate = data.discount_rate;
                // calculate the new amount after applying the discount
                currentAmount = currentAmount * discountRate;
                updatePaymentAmount(); // update the displayed total amount
                document.getElementById("used_promo_id").value = data.promo_id
                promoMessageElement.textContent = data.message;
                promoMessageElement.style.color = "green";
            } else {
                promoMessageElement.textContent = data.message;
                promoMessageElement.style.color = "red";
                applyPromoButton.disabled = false;
            }
        })
        .catch(error => {
            if (!response.ok) {
                console.error("Error:", error);
                promoMessageElement.textContent = "An error occurred. Please try again.";
                
            }
        });
}

// Function to apply the gift card
function verifyGiftCard() {
    const giftCardCode = document.getElementById("gift_card_code").value.trim();
    const giftCardPassword = document.getElementById("gift_card_password").value.trim();
    const giftCardMessageElement = document.getElementById("gift_card_message");

    if (!giftCardCode || !giftCardPassword) {
        giftCardMessageElement.textContent = "Please enter the redemption code and password.";
        giftCardMessageElement.style.color = "red";
        giftCardModal.hide();
        return;
    }

    fetch('/accommodation/api/validate_gift_card', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ gift_card_code: giftCardCode, gift_card_password: giftCardPassword })
    })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                giftCardMessageElement.textContent = "";
                giftCardId = data.gift_card_id;
                giftCardBalance = data.balance;
                const giftCardSection = document.getElementById('gift_card_section');
                giftCardSection.innerHTML = `
                    <h5 class="text-color pt-2" id="gift_card_balance"><strong>Your Gift Card Balance: $${giftCardBalance}</strong></h5>
                    <div class="input-group mb-3">
                        <div class="input-group-prepend">
                            <span class="input-group-text">$</span>
                        </div>
                        <input type="number" class="form-control" placeholder="Enter amount to use" aria-label="Amount" id="gift_card_use_amount">
                        <button class="btn btn-outline-warning" type="button" id="use_gift_card_button">Use</button>
                    </div>
                `;
                document.getElementById('use_gift_card_button').addEventListener('click', useGiftCard);
            } else {
                giftCardMessageElement.textContent = data.message;
                giftCardMessageElement.style.color = "red";
            }
            giftCardModal.hide();
        })
        .catch(error => {
            console.error("Error:", error);
            giftCardMessageElement.textContent = "An error occurred. Please try again.";
            giftCardMessageElement.style.color = "red";
            giftCardModal.hide();
        });
};

function useGiftCard() {
    const useAmountInput = document.getElementById('gift_card_use_amount').value;
    const giftCardMessageElement = document.getElementById('gift_card_message');

    if (isNaN(useAmountInput) || useAmountInput <= 0) {
        giftCardMessageElement.textContent = "Please enter a valid amount.";
        giftCardMessageElement.style.color = "red";
        return;
    }

    const useAmount = Math.min(useAmountInput, giftCardBalance, currentAmount);

    if (useAmount > 0) {
        giftCardBalance -= useAmount;
        updateGiftCardBalance();
        // Update remaining payment amount
        currentAmount -= useAmount;
        updatePaymentAmount();
        // Maybe trigger some backend update here as well
        document.getElementById('use_gift_card').value = "True";
        document.getElementById('gift_card_amount').value = useAmount;
        document.getElementById('gift_card_id').value = giftCardId;
        giftCardMessageElement.textContent = `You have used $${useAmount} from your gift card.`;
        giftCardMessageElement.style.color = "green";
    } else {
        giftCardMessageElement.textContent = "The amount exceeds the balance or Payment Amount.";
        giftCardMessageElement.style.color = "red";
    }
}

// Function to toggle the visibility of the card payment section
function toggleCardPaymentSection() {
    const paymentMethod = document.getElementById("payment_method").value;
    const cardPaymentSection = document.querySelector(".card-section");

    if (paymentMethod === "card") {
        cardPaymentSection.style.display = "block";
    } else {
        cardPaymentSection.style.display = "none";
    }
}
// Initially hide the card payment section if "Pay During Collection" is selected
toggleCardPaymentSection();

// Function to toggle visibility of pickup time
function toggleSchedule() {
    const pickupOption = document.getElementById("pickup_option").value;
    const scheduleTime = document.getElementById("schedule_time");
    const pickupTime = document.getElementById("pickup_time");

    if (pickupOption === "schedule") {
        scheduleTime.style.display = "block";
        pickupTime.required = true;
    } else {
        scheduleTime.style.display = "none";
        pickupTime.required = false;
    }
}

// Add an event listener to the "Apply Promo Code" button
document.getElementById("apply_promo_button").addEventListener("click", applyPromoCode);
document.getElementById("verify_gift_card").addEventListener("click", verifyGiftCard);
document.getElementById("payment_method").addEventListener("change", toggleCardPaymentSection);
document.getElementById("pickup_option").addEventListener("change", toggleSchedule);