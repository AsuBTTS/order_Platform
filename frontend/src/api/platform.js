import http from "./http";

export function loginPlatformAdmin(payload) {
  return http.post("/login/", payload);
}

export function fetchPlatformDashboard(userId) {
  return http.get("/platform/dashboard/", { params: { user_id: userId } });
}

export function fetchPlatformUsers(userId, filters = {}) {
  return http.get("/platform/users/", {
    params: {
      user_id: userId,
      ...filters,
    },
  });
}

export function updatePlatformUserStatus(adminId, targetUserId, isActive) {
  return http.post(`/platform/users/${targetUserId}/status/`, {
    user_id: adminId,
    is_active: isActive,
  });
}

export function fetchPlatformCoupons(userId) {
  return http.get("/platform/coupons/", { params: { user_id: userId } });
}

export function issuePlatformCoupon(adminId, payload) {
  return http.post("/platform/coupons/", {
    user_id: adminId,
    ...payload,
  });
}

export function fetchPlatformDishes(userId, filters = {}) {
  return http.get("/platform/dishes/", {
    params: {
      user_id: userId,
      ...filters,
    },
  });
}

export function createPlatformDish(userId, payload) {
  return http.post("/platform/dishes/create/", {
    user_id: userId,
    ...payload,
  });
}

export function updatePlatformDish(userId, dishId, payload) {
  return http.post(`/platform/dishes/${dishId}/`, {
    user_id: userId,
    ...payload,
  });
}

export function savePlatformStoreAccount(userId, payload) {
  return http.post("/platform/stores/account/", {
    user_id: userId,
    ...payload,
  });
}
