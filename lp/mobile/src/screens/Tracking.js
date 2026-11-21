
import React, { useState } from "react";
import { Alert, Linking, RefreshControl, Text, View } from "react-native";
import { Ionicons } from "@expo/vector-icons";
import { api, money } from "../api";
import { C, DAYS, PAYMENTS, SLOTS } from "../theme";
import { Btn, Card, Chip, Err, H, LoadState, Muted, Pill, Row, Screen, useFocusLoad } from "../ui";

const ICON = { box: "cube-outline", washer: "water-outline", shirt: "shirt-outline", bike: "bicycle-outline" };
const STATE_COLOR = { done: C.ok, active: C.primary, pending: C.line };

export default function Tracking({ route, navigation }) {
  const id = route.params.orderId;
  const { data: o, error, loading, reload } = useFocusLoad(() => api(`/orders/${id}`), [id]);
  const [order, setOrder] = useState(null), [err, setErr] = useState(""), [busy, setBusy] = useState(false);
  const [resched, setResched] = useState(false), [day, setDay] = useState("Today"), [slot, setSlot] = useState(SLOTS[0]), [pay, setPay] = useState("upi");
  const cur = order && order.id === id && o && order.code === o.code ? order : o;       // prefer the freshest copy
  if (!cur) return <LoadState loading={loading} error={error} data={cur} reload={reload} />;

  async function run(fn) {
    setErr(""); setBusy(true);
    try { setOrder(await fn()); setResched(false); } catch (e) { setErr(e.message); }
    setBusy(false);
  }
  const confirmCancel = () => Alert.alert("Cancel this order?", "This cannot be undone.", [{ text: "Keep order" },
    { text: "Cancel order", style: "destructive", onPress: () => run(() => api(`/orders/${id}/cancel`, { method: "POST" })) }]);
  const unpaid = !cur.cancelled && cur.payment_status !== "paid";

  return (
    <Screen refreshControl={<RefreshControl refreshing={false} onRefresh={() => { setOrder(null); reload(); }} />}>
      <Card>
        <Row style={{ justifyContent: "space-between" }}><Text style={{ fontSize: 18, fontWeight: "800", color: C.navy }}>{cur.code}</Text>
          <Pill text={cur.status} color={cur.cancelled ? C.danger : C.primary} /></Row>
        <Muted style={{ marginTop: 6 }}>{cur.service_label} · {cur.provider} · {cur.weight} kg · {money(cur.total)}</Muted>
        <Muted>{cur.cancelled ? "Order cancelled" : cur.stage === 4 ? "Delivered" : `Estimated delivery ${cur.eta_text}`}</Muted>
        <Muted>Pickup {cur.pickup_day}, {cur.pickup_slot}</Muted>
      </Card>

      {unpaid ? (
        <Card style={{ borderColor: C.warn }}>
          <Text style={{ fontWeight: "700", color: C.navy }}>{cur.payment_status === "failed" ? "Payment failed" : "Payment pending"}</Text>
          <Muted style={{ marginBottom: 8 }}>Pay {money(cur.total)} to confirm your pickup.</Muted>
          <Row style={{ flexWrap: "wrap" }}>{PAYMENTS.map((m) => <Chip key={m.key} label={m.title} active={pay === m.key} onPress={() => setPay(m.key)} />)}</Row>
          <Btn title={`Pay ${money(cur.total)}`} busy={busy} onPress={() => run(() => api(`/orders/${id}/payment`, { method: "POST", body: { payment: pay } }))} />
        </Card>) : null}

      <H>Order status</H>
      <Card>
        {cur.timeline.map((t, i) => (
          <Row key={t.title} style={{ marginVertical: 8, alignItems: "flex-start" }}>
            <View style={{ width: 38, height: 38, borderRadius: 19, backgroundColor: STATE_COLOR[t.state], alignItems: "center", justifyContent: "center" }}>
              <Ionicons name={t.state === "done" ? "checkmark" : ICON[t.icon]} size={20} color={t.state === "pending" ? C.muted : "#fff"} /></View>
            <View style={{ marginLeft: 12, flex: 1 }}><Text style={{ fontWeight: "700", color: t.state === "pending" ? C.muted : C.navy }}>{t.title}</Text><Muted>{t.sub}</Muted></View>
          </Row>))}
      </Card>

      {!cur.cancelled && cur.stage < 4 && cur.partner_phone ? (
        <Card><Row style={{ justifyContent: "space-between" }}>
          <View><Text style={{ fontWeight: "700" }}>Your pickup partner</Text><Muted>{cur.partner}</Muted></View>
          <Btn title="Call" icon="call-outline" kind="outline" onPress={() => Linking.openURL(`tel:${cur.partner_phone}`)} style={{ marginTop: 0, height: 44 }} />
        </Row></Card>) : null}

      <Err text={err} />
      {cur.stage === 0 && !cur.cancelled ? (
        <>
          {resched ? (
            <Card>
              <Text style={{ fontWeight: "700", marginBottom: 8 }}>New pickup time</Text>
              <Row>{DAYS.map((d) => <Chip key={d} label={d} active={day === d} onPress={() => setDay(d)} />)}</Row>
              <Row style={{ flexWrap: "wrap" }}>{SLOTS.map((s) => <Chip key={s} label={s} active={slot === s} onPress={() => setSlot(s)} />)}</Row>
              <Btn title="Save new time" busy={busy} onPress={() => run(() => api(`/orders/${id}`, { method: "PUT", body: { day, slot } }))} />
            </Card>) : <Btn title="Reschedule pickup" kind="outline" onPress={() => { setDay(cur.pickup_day); setSlot(cur.pickup_slot); setResched(true); }} />}
          <Btn title="Cancel order" kind="danger" onPress={confirmCancel} />
        </>) : null}

      {cur.stage === 4 && !cur.reviewed ? <Btn title="Rate this provider" icon="star-outline" onPress={() => navigation.navigate("Review", { orderId: id })} /> : null}
      {cur.stage === 4 && cur.reviewed ? <Muted style={{ textAlign: "center", marginTop: 12 }}>Thanks for your review!</Muted> : null}
      {!cur.cancelled && cur.stage < 4 && !unpaid ? (
        <Btn title="Demo: move to next stage" kind="outline" busy={busy} onPress={() => run(() => api(`/orders/${id}/advance`, { method: "POST" }))} />) : null}
    </Screen>
  );
}
