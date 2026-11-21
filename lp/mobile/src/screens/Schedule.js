
import React, { useEffect, useState } from "react";
import { Pressable, Text, View } from "react-native";
import { Ionicons } from "@expo/vector-icons";
import { api, money } from "../api";
import { useBooking } from "../booking";
import { C, DAYS, SLOTS } from "../theme";
import { Btn, Card, Chip, Err, H, LoadState, Muted, Row, Screen, useFocusLoad } from "../ui";

export default function Schedule({ navigation }) {
  const { booking, update } = useBooking();
  const { data, error, loading, reload } = useFocusLoad(async () => {
    const [d, addresses] = await Promise.all([api(`/providers/${booking.providerId}?service=${booking.service}`), api("/addresses")]);
    return { ...d, addresses };
  }, [booking.providerId, booking.service]);
  const [quote, setQuote] = useState(null);
  const weight = booking.weight ?? data?.provider.default_weight ?? 3;
  const addressId = data ? (data.addresses.find((a) => a.id === booking.addressId) || data.addresses[0] || {}).id : null;

  useEffect(() => {
    if (!data) return;
    api("/quote", { method: "POST", body: { provider_id: booking.providerId, service: booking.service, weight } }).then(setQuote).catch(() => {});
  }, [data, weight]);

  if (!data) return <LoadState loading={loading} error={error} data={data} reload={reload} />;
  const step = (n) => update({ weight: Math.max(1, Math.min(25, weight + n)) });
  return (
    <Screen>
      <H>How much laundry?</H>
      <Card>
        <Row style={{ justifyContent: "space-between" }}>
          <Pressable onPress={() => step(-1)} style={btn}><Ionicons name="remove" size={22} color={C.primary} /></Pressable>
          <View style={{ alignItems: "center" }}><Text style={{ fontSize: 28, fontWeight: "800", color: C.navy }}>{weight} kg</Text><Muted>1 to 25 kg · min {data.provider.min_kg} kg</Muted></View>
          <Pressable onPress={() => step(1)} style={btn}><Ionicons name="add" size={22} color={C.primary} /></Pressable>
        </Row>
      </Card>
      <H>Pickup day</H>
      <Row>{DAYS.map((d) => <Chip key={d} label={d} active={booking.day === d} onPress={() => update({ day: d })} />)}</Row>
      <H>Time slot</H>
      <Row style={{ flexWrap: "wrap" }}>{SLOTS.map((s) => <Chip key={s} label={s} active={booking.slot === s} onPress={() => update({ slot: s })} />)}</Row>
      <H>Pickup address</H>
      {data.addresses.map((a) => (
        <Card key={a.id} onPress={() => update({ addressId: a.id })} style={a.id === addressId ? { borderColor: C.primary, borderWidth: 2 } : null}>
          <Row><Ionicons name={a.id === addressId ? "radio-button-on" : "radio-button-off"} size={20} color={C.primary} />
            <View style={{ marginLeft: 10, flex: 1 }}><Text style={{ fontWeight: "700" }}>{a.label}</Text><Muted>{a.full}</Muted></View></Row>
        </Card>))}
      <Btn title="Add or manage addresses" kind="outline" onPress={() => navigation.navigate("Addresses")} />
      {quote ? (quote.error ? <Err text={quote.error} /> : <Muted style={{ marginTop: 14, textAlign: "center" }}>Estimated total {money(quote.total)}</Muted>) : null}
      <Btn title="Continue to payment" disabled={!quote || !!quote.error || !addressId} onPress={() => { update({ weight, addressId }); navigation.navigate("Checkout"); }} />
    </Screen>
  );
}
const btn = { width: 44, height: 44, borderRadius: 22, borderWidth: 1.5, borderColor: C.primary, alignItems: "center", justifyContent: "center" };
