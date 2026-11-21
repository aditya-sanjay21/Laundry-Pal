
import React, { useRef, useState } from "react";
import { Pressable, Switch, Text, View } from "react-native";
import { Ionicons } from "@expo/vector-icons";
import { api, money } from "../api";
import { useBooking } from "../booking";
import { C, PAYMENTS } from "../theme";
import { Btn, Card, Err, H, LoadState, Muted, Row, Screen, useFocusLoad } from "../ui";

export default function Checkout({ navigation }) {
  const { booking: b, update, reset } = useBooking();
  const { data, error, loading, reload } = useFocusLoad(async () => {
    const [d, addresses, quote] = await Promise.all([api(`/providers/${b.providerId}?service=${b.service}`), api("/addresses"),
      api("/quote", { method: "POST", body: { provider_id: b.providerId, service: b.service, weight: b.weight } })]);
    return { ...d, address: addresses.find((a) => a.id === b.addressId), quote };
  }, []);
  const [err, setErr] = useState(""), [busy, setBusy] = useState(false), [fail, setFail] = useState(false);
  const orderRef = useRef(null);                       // the order created on the first attempt (reused on retry)

  if (!data) return <LoadState loading={loading} error={error} data={data} reload={reload} />;
  const { provider: p, service, address, quote } = data;

  async function pay() {
    setErr(""); setBusy(true);
    try {
      if (!orderRef.current) {
        orderRef.current = await api("/orders", { method: "POST", body: { provider_id: b.providerId, service: b.service,
          weight: b.weight, day: b.day, slot: b.slot, address_id: b.addressId, payment: b.payment } });
      }
      await api(`/orders/${orderRef.current.id}/payment`, { method: "POST", body: { payment: b.payment, simulate_fail: fail } });
      const id = orderRef.current.id;
      reset();
      navigation.reset({ index: 1, routes: [{ name: "Tabs" }, { name: "Tracking", params: { orderId: id } }] });
    } catch (e) { setErr(e.message); setBusy(false); }
  }

  const Line = ({ k, v, bold }) => <Row style={{ justifyContent: "space-between", marginVertical: 3 }}>
    <Muted>{k}</Muted><Text style={{ fontWeight: bold ? "800" : "600", color: C.navy, flexShrink: 1, textAlign: "right", marginLeft: 12 }}>{v}</Text></Row>;
  return (
    <Screen>
      <H>Order review</H>
      <Card>
        <Line k="Provider" v={p.name} /><Line k="Service" v={service.label} /><Line k="Weight" v={`${b.weight} kg`} />
        <Line k="Pickup" v={`${b.day}, ${b.slot}`} /><Line k="Address" v={address ? address.short : "-"} />
      </Card>
      <Card>
        <Line k={`${b.weight} kg × ${money(quote.unit)}`} v={money(quote.subtotal)} />
        <Line k="Delivery" v={quote.delivery === 0 ? "Free" : money(quote.delivery)} />
        <Line k="Total" v={money(quote.total)} bold />
      </Card>
      <H>Payment method</H>
      {PAYMENTS.map((m) => (
        <Card key={m.key} onPress={() => update({ payment: m.key })} style={b.payment === m.key ? { borderColor: C.primary, borderWidth: 2 } : null}>
          <Row><Ionicons name={m.icon} size={24} color={C.primary} />
            <View style={{ flex: 1, marginLeft: 12 }}><Text style={{ fontWeight: "700" }}>{m.title}</Text><Muted>{m.sub}</Muted></View>
            <Ionicons name={b.payment === m.key ? "radio-button-on" : "radio-button-off"} size={20} color={C.primary} /></Row>
        </Card>))}
      {__DEV__ ? <Row style={{ justifyContent: "space-between", marginTop: 4 }}><Muted>Demo: simulate a failed payment</Muted><Switch value={fail} onValueChange={setFail} /></Row> : null}
      <Err text={err} />
      <Btn title={orderRef.current ? `Retry payment · ${money(quote.total)}` : `Place Order · ${money(quote.total)}`} onPress={pay} busy={busy} />
      {orderRef.current ? <Muted style={{ textAlign: "center", marginTop: 8 }}>Your order is saved. You can also pay later from Orders.</Muted> : null}
    </Screen>
  );
}
