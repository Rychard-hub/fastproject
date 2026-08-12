const STORAGE_KEY = "admin_api_key";

export function getAdminKey() {
  return localStorage.getItem(STORAGE_KEY) || "";
}

export function setAdminKey(key) {
  if (key) {
    localStorage.setItem(STORAGE_KEY, key);
  } else {
    localStorage.removeItem(STORAGE_KEY);
  }
}

export function adminHeaders() {
  const key = getAdminKey();
  return key ? { "X-Admin-Key": key } : {};
}
