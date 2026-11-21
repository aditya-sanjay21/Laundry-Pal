
import React, { createContext, useContext, useState } from "react";
import { DAYS, SLOTS } from "./theme";

const fresh = () => ({ service: "laundry", providerId: null, weight: null, day: DAYS[0], slot: SLOTS[0], addressId: null, payment: "upi" });
const Ctx = createContext(null);
export const useBooking = () => useContext(Ctx);

export function BookingProvider({ children }) {
  const [booking, setBooking] = useState(fresh());
  const update = (patch) => setBooking((b) => ({ ...b, ...patch }));
  return <Ctx.Provider value={{ booking, update, reset: () => setBooking(fresh()) }}>{children}</Ctx.Provider>;
}
