export function requestCurrentLocation() {
  return new Promise((resolve, reject) => {
    if (!navigator.geolocation) {
      reject(new Error("当前浏览器不支持定位。"));
      return;
    }

    navigator.geolocation.getCurrentPosition(
      (position) => {
        resolve({
          latitude: position.coords.latitude,
          longitude: position.coords.longitude,
        });
      },
      () => reject(new Error("定位失败，请检查浏览器定位权限。")),
      { enableHighAccuracy: true, timeout: 8000, maximumAge: 60000 },
    );
  });
}

export function distanceKm(from, store) {
  if (!from || !store?.store_latitude || !store?.store_longitude) {
    return null;
  }

  const earthRadiusKm = 6371;
  const lat1 = Number(from.latitude);
  const lon1 = Number(from.longitude);
  const lat2 = Number(store.store_latitude);
  const lon2 = Number(store.store_longitude);
  const dLat = toRad(lat2 - lat1);
  const dLon = toRad(lon2 - lon1);
  const a =
    Math.sin(dLat / 2) * Math.sin(dLat / 2) +
    Math.cos(toRad(lat1)) * Math.cos(toRad(lat2)) * Math.sin(dLon / 2) * Math.sin(dLon / 2);
  return earthRadiusKm * 2 * Math.atan2(Math.sqrt(a), Math.sqrt(1 - a));
}

export function nearestStore(stores, location) {
  if (!stores.length) {
    return null;
  }
  if (!location) {
    return stores[0];
  }

  return [...stores].sort((a, b) => {
    const distanceA = distanceKm(location, a) ?? Number.MAX_SAFE_INTEGER;
    const distanceB = distanceKm(location, b) ?? Number.MAX_SAFE_INTEGER;
    return distanceA - distanceB;
  })[0];
}

function toRad(value) {
  return (value * Math.PI) / 180;
}
