import http from "./http";

export function loginDriver(payload) {
  return http.post("/login/", payload);
}

export function fetchDeliveryOrders(userId) {
  return http.get("/delivery/orders/", { params: { user_id: userId } });
}

export function acceptDeliveryOrder(userId, orderId) {
  return http.post(`/delivery/orders/${orderId}/accept/`, { user_id: userId });
}

export function pickupDeliveryOrder(userId, orderId) {
  return http.post(`/delivery/orders/${orderId}/pickup/`, { user_id: userId });
}

export function deliveredDeliveryOrder(userId, orderId) {
  return http.post(`/delivery/orders/${orderId}/delivered/`, { user_id: userId });
}
