
import React, { useState } from 'react';

function ShoppingCart() {
  const [cartItems, setCartItems] = useState([]);
  const [totalCost, setTotalCost] = useState(0);

  function handleAddToCart(product) {
    setCartItems(cartItems => [...cartItems, product]);
  }

  function handleRemoveFromCart(productId) {
    setCartItems(cartItems => cartItems.filter(item => item.id !== productId));
  }

  return (
    <div>
      <h2>Shopping Cart</h2>
      <ul>
        {cartItems.map((item, index) => (
          <li key={index}>
            {item.name} - ${item.price}
            <button onClick={() => handleRemoveFromCart(item.id)}>Remove</button>
          </li>
        ))}
      </ul>
      <p>Total Cost: ${totalCost}</p>
    </div>
  );
}

export default ShoppingCart;
