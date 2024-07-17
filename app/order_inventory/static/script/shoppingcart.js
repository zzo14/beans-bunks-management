function showOptions(type, productId) {
  const options = {
      milk: '#milkOptions' + productId,
      syrup: '#syrupOptions' + productId,
      size: '#sizeOptions' + productId,
  };

  for (const key in options) {
      if (options.hasOwnProperty(key)) {
          $(options[key]).toggle(key === type);
      }
  }
}

function addToCart(productId) {
  var selectedVariations = [];
  var quantity = $('#quantity' + productId).val();

  // get selected variations
  $('input[name="variation_id"]:checked').each(function() {
      selectedVariations.push($(this).val());
  });

  $.ajax({
      type: "POST",
      url: "/order_inventory/add_to_cart",
      data: JSON.stringify({
          product_id: productId,
          quantity: quantity,
          variations: selectedVariations,
      }),
      contentType: "application/json",
      success: function(response) {
          if (response.status === 'redirect') {
              if (response.redirect_url === '/auth/login') {
                  window.location.href = response.redirect_url; // redirect to login page
              } else {
                  fetchCartContents();
                  // clear selected variations after adding to cart
                  $('input[name="variation_id"]:checked').prop('checked', false);
                  $('#quantity' + productId).val('1'); // reset the quantity
                  $('#addToCartModal' + productId).modal('hide'); // hide modal
              }
          } 
      },
      error: function(xhr, status, error) {
          console.error('Error:', error);
          alert('Failed to add item to cart. Please try again later.');
      }
  });
  
  return false;
}

function fetchCartContents() {
  $.ajax({
      type: "GET",
      url: "/order_inventory/shopping_cart",
      success: function(response) {                    
          var cartSection = $(response).find('.cart-content').html();      
          var totalPrice = $(response).find('.total-price').html();        
          $('.cart-content').html(cartSection);                            // display cart contents
          $('.total-price').text(totalPrice);                              // display total price

          // Add separator lines
          $('.cart-item').each(function() {
            $(this).after('<hr class="cart-item-divider" style="border-top: 1px solid #6C4E37;">');
          });

          $('.cart-overlay').addClass('showCart');                         // display cart
      },
      error: function(xhr, status, error) {
          console.error('Error fetching cart contents:', error);          // danger message
      }
  });
}

function removeItem(cartDetailId) {
  $.ajax({
      type: "POST",
      url: "/order_inventory/remove_item",
      data: JSON.stringify({
          cart_detail_id: cartDetailId
      }),
      contentType: "application/json",
      success: function(response) {
        var cartItem = $('.cart-item[data-cart-detail-id="' + cartDetailId + '"]');
        var divider = cartItem.next('.cart-item-divider'); 
        cartItem.remove(); // remove item
        divider.remove(); // remove divider
        $('.total-price').text('$' + response.total_price);                               // update total price
      },
      error: function(xhr, status, error) {
          console.error('Error removing item from cart:', error);
          alert('Failed to remove item from cart. Please try again later.')              // danger message
      }
  });
}

function updateQuantity(cartDetailId, action) {
  var quantityElement = $('.cart-item[data-cart-detail-id="' + cartDetailId + '"] .item-quantity');
  var currentQuantity = parseInt(quantityElement.text());
  
  var newQuantity;
  if (action === 'increase') {
    newQuantity = currentQuantity + 1;
  } else if (action === 'decrease') {
    newQuantity = currentQuantity - 1;
  }

  $.ajax({
      type: "POST",
      url: "/order_inventory/update_quantity",
      data: JSON.stringify({
          cart_detail_id: cartDetailId,
          new_quantity: newQuantity
      }),
      contentType: "application/json",
      success: function(response) {
        quantityElement.text(newQuantity);              // update quantity
        $('.total-price').text('$' + response.total_price);          // update total price
        if (newQuantity === 0) {
          removeItem(cartDetailId);                     // remove item if quantity is 0
        }
        
      },
      error: function(xhr, status, error) {
          console.error('Error updating item quantity:', error);
          alert('Failed to update item quantity. Please try again later.');         // danger message
      }
  });
}

document.addEventListener('DOMContentLoaded', function() {
  const cartIcon = document.getElementById('cart-icon');
  const cartOverlay = document.querySelector('.cart-overlay');
  const closeCartBtn = document.querySelector('.cart-close');
  const cartContent = document.querySelector('.cart-content');

  cartIcon.addEventListener('click', function() {
      cartOverlay.classList.add('showCart');
      fetchCartContents(cartContent);
  });

  closeCartBtn.addEventListener('click', function() {
      cartOverlay.classList.remove('showCart');
  });

  document.addEventListener('click', function(event) {
      if (event.target.matches('.remove-item')) {
          const cartDetailId = event.target.closest('.cart-item').dataset.cartDetailId;
          removeItem(cartDetailId);
      } else if (event.target.matches('.increase-quantity')) {
          const cartDetailId = event.target.dataset.cartDetailId;
          updateQuantity(cartDetailId, 'increase');
      } else if (event.target.matches('.decrease-quantity')) {
          const cartDetailId = event.target.dataset.cartDetailId;
          updateQuantity(cartDetailId, 'decrease');
      }
  });
});
