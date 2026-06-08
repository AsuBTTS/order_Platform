const USER_KEY = "order_platform_user";
const MERCHANT_KEY = "order_platform_merchant";
const DRIVER_KEY = "order_platform_driver";
const PLATFORM_KEY = "order_platform_platform_admin";
const FULFILLMENT_KEY = "order_platform_fulfillment";
const SELECTED_STORE_KEY = "order_platform_selected_store";
const USER_LOCATION_KEY = "order_platform_user_location";

export function getStoredUser() {
  const raw = localStorage.getItem(USER_KEY);
  if (!raw) {
    return null;
  }

  try {
    return JSON.parse(raw);
  } catch {
    localStorage.removeItem(USER_KEY);
    return null;
  }
}

export function setStoredUser(user) {
  localStorage.setItem(USER_KEY, JSON.stringify(user));
}

export function updateStoredUser(updates) {
  const current = getStoredUser() || {};
  const next = { ...current, ...updates };
  setStoredUser(next);
  return next;
}

export function clearStoredUser() {
  localStorage.removeItem(USER_KEY);
}

export function getCustomerId() {
  const user = getStoredUser();
  return user?.role === "customer" ? user.id : null;
}

export function getStoredMerchant() {
  const raw = localStorage.getItem(MERCHANT_KEY);
  if (!raw) {
    return null;
  }

  try {
    return JSON.parse(raw);
  } catch {
    localStorage.removeItem(MERCHANT_KEY);
    return null;
  }
}

export function setStoredMerchant(user) {
  localStorage.setItem(MERCHANT_KEY, JSON.stringify(user));
}

export function updateStoredMerchant(updates) {
  const current = getStoredMerchant() || {};
  const next = { ...current, ...updates };
  setStoredMerchant(next);
  return next;
}

export function clearStoredMerchant() {
  localStorage.removeItem(MERCHANT_KEY);
}

export function getMerchantId() {
  const user = getStoredMerchant();
  return user?.role === "merchant" ? user.id : null;
}

export function getStoredDriver() {
  const raw = localStorage.getItem(DRIVER_KEY);
  if (!raw) {
    return null;
  }

  try {
    return JSON.parse(raw);
  } catch {
    localStorage.removeItem(DRIVER_KEY);
    return null;
  }
}

export function setStoredDriver(user) {
  localStorage.setItem(DRIVER_KEY, JSON.stringify(user));
}

export function clearStoredDriver() {
  localStorage.removeItem(DRIVER_KEY);
}

export function getDriverId() {
  const user = getStoredDriver();
  return user?.role === "driver" ? user.id : null;
}

export function getStoredPlatformAdmin() {
  const raw = localStorage.getItem(PLATFORM_KEY);
  if (!raw) {
    return null;
  }

  try {
    return JSON.parse(raw);
  } catch {
    localStorage.removeItem(PLATFORM_KEY);
    return null;
  }
}

export function setStoredPlatformAdmin(user) {
  localStorage.setItem(PLATFORM_KEY, JSON.stringify(user));
}

export function clearStoredPlatformAdmin() {
  localStorage.removeItem(PLATFORM_KEY);
}

export function getPlatformAdminId() {
  const user = getStoredPlatformAdmin();
  return user?.is_staff || user?.is_superuser ? user.id : null;
}

export function getFulfillmentType() {
  return localStorage.getItem(FULFILLMENT_KEY) || "self_pickup";
}

export function setFulfillmentType(type) {
  localStorage.setItem(FULFILLMENT_KEY, type);
}

export function getSelectedStore() {
  const raw = localStorage.getItem(SELECTED_STORE_KEY);
  if (!raw) {
    return null;
  }

  try {
    return JSON.parse(raw);
  } catch {
    localStorage.removeItem(SELECTED_STORE_KEY);
    return null;
  }
}

export function setSelectedStore(store) {
  localStorage.setItem(SELECTED_STORE_KEY, JSON.stringify(store));
}

export function getSelectedStoreId() {
  return getSelectedStore()?.id || null;
}

export function getUserLocation() {
  const raw = localStorage.getItem(USER_LOCATION_KEY);
  if (!raw) {
    return null;
  }

  try {
    return JSON.parse(raw);
  } catch {
    localStorage.removeItem(USER_LOCATION_KEY);
    return null;
  }
}

export function setUserLocation(location) {
  localStorage.setItem(USER_LOCATION_KEY, JSON.stringify(location));
}
