import http from "./http";

export function loginMerchant(payload) {
  return http.post("/login/", payload);
}

export function fetchMerchantProfile(userId) {
  return http.get("/user/current/", { params: { user_id: userId } });
}

export function fetchMerchantOrders(userId) {
  return http.get("/merchant/orders/", { params: { user_id: userId } });
}

export function acceptMerchantOrder(userId, orderId) {
  return http.post(`/merchant/orders/${orderId}/accept/`, { user_id: userId });
}

export function finishMerchantOrder(userId, orderId) {
  return http.post(`/merchant/orders/${orderId}/finish/`, { user_id: userId });
}

export function fetchMerchantDishes(userId) {
  return http.get("/merchant/dishes/", { params: { user_id: userId } });
}

export function createMerchantDish(userId, payload) {
  return http.post("/merchant/dishes/create/", {
    user_id: userId,
    ...payload,
  });
}

export function restockMerchantDish(userId, dishId, quantity) {
  return http.post(`/merchant/dishes/${dishId}/restock/`, {
    user_id: userId,
    quantity,
  });
}
