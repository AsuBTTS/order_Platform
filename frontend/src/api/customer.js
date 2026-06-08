import http from "./http";

export function login(payload) {
  return http.post("/login/", payload);
}

export function register(payload) {
  return http.post("/register/", payload);
}

export function fetchDishes() {
  return http.get("/dishes/");
}

export function fetchStores() {
  return http.get("/stores/");
}

export function fetchDishesByCategory(category, merchantId = null) {
  return http.get("/dishes/", {
    params: {
      ...(category ? { category } : {}),
      ...(merchantId ? { merchant_id: merchantId } : {}),
    },
  });
}

export function fetchDish(id) {
  return http.get(`/dishes/${id}/`);
}

export function fetchCart(userId) {
  return http.get("/cart/items/", { params: { user_id: userId } });
}

export function addCartItem(userId, dishId, quantity = 1, merchantId = null, customization = null) {
  return http.post("/cart/items/", {
    user_id: userId,
    dish_id: dishId,
    quantity,
    merchant_id: merchantId,
    customization,
  });
}

export function updateCartItem(userId, itemId, quantity) {
  return http.put(`/cart/items/${itemId}/`, {
    user_id: userId,
    quantity,
  });
}

export function deleteCartItem(userId, itemId) {
  return http.delete(`/cart/items/${itemId}/`, {
    params: { user_id: userId },
  });
}

export function createOrder(userId, deliveryType, couponId = null, merchantId = null) {
  return http.post("/orders/", {
    user_id: userId,
    delivery_type: deliveryType,
    coupon_id: couponId,
    merchant_id: merchantId,
  });
}

export function fetchOrders(userId) {
  return http.get("/orders/", { params: { user_id: userId } });
}

export function fetchOrder(userId, orderId) {
  return http.get(`/orders/${orderId}/`, { params: { user_id: userId } });
}

export function completeOrder(userId, orderId) {
  return http.post(`/orders/${orderId}/complete/`, { user_id: userId });
}

export function createPayment(userId, orderId, paymentType) {
  return http.post("/payments/", {
    user_id: userId,
    order_id: orderId,
    payment_type: paymentType,
  });
}

export function paySuccess(userId, paymentId) {
  return http.post(`/payments/${paymentId}/success/`, { user_id: userId });
}

export function payFail(userId, paymentId) {
  return http.post(`/payments/${paymentId}/fail/`, { user_id: userId });
}

export function submitReview(userId, orderId, score, content) {
  return http.post("/reviews/", {
    user_id: userId,
    order_id: orderId,
    score,
    content,
  });
}

export function fetchUserCoupons(userId) {
  return http.get("/user/coupons/", { params: { user_id: userId } });
}

export function updateProfile(userId, payload) {
  return http.post("/user/profile/", {
    user_id: userId,
    ...payload,
  });
}

export function changePassword(userId, oldPassword, newPassword) {
  return http.post("/user/change-password/", {
    user_id: userId,
    old_password: oldPassword,
    new_password: newPassword,
  });
}
