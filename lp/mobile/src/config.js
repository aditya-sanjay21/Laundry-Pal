
import Constants from "expo-constants";

const MANUAL_URL = "";

function detect() {
  const hostUri = Constants.expoConfig?.hostUri || Constants.expoGoConfig?.debuggerHost || "";
  const host = hostUri.split(":")[0];
  return host ? `http://${host}:5000` : "http://10.0.2.2:5000"; // 10.0.2.2 = Android emulator -> your computer
}

export const BASE_URL = MANUAL_URL || detect();
export const API = `${BASE_URL}/api`;
export const img = (name) => (name ? `${BASE_URL}/images/${name}` : null);
