const RAW_API_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';

// Ensure API_URL is an absolute URL. Some dev setups may set only a port
// like ":8000"; normalize that to include the current host/protocol.
function getApiBase() {
  const v = RAW_API_URL;
  if (!v) return `${window.location.protocol}//${window.location.hostname}:8000`;
  // port-only like ":8000"
  if (/^:\d+$/.test(v)) {
    return `${window.location.protocol}//${window.location.hostname}${v}`;
  }
  // already absolute (http(s)://...)
  if (/^https?:\/\//.test(v)) return v.replace(/\/$/, '');
  // host:port or hostname only
  if (/^[\w.-]+(:\d+)?$/.test(v)) return `${window.location.protocol}//${v}`;
  return v;
}

const API_URL = getApiBase();

export async function refreshAuth() {
  try {
    const res = await fetch(`${API_URL}/api/auth/refresh`, {
      method: "POST",
      credentials: "include",
      headers: {
        "Content-Type": "application/json",
      },
    });

    if (!res.ok) {
      return null;
    }

    const data = await res.json();
    return data;
  } catch (err) {
    console.error("refreshAuth error", err);
    return null;
  }
}
