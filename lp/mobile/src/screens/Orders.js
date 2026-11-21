
import React, { useState } from "react";
import { RefreshControl, Text, View } from "react-native";
import { api, money } from "../api";
import { C } from "../theme";
import { Card, Chip, LoadState, Muted, Pill, Row, Screen, useFocusLoad } from "../ui";

export default function Orders({ navigation }) {
  const [tab, setTab] = useState("active");
  const { data, error, loading, reload } = useFocusLoad(() => api("/orders"), []);
  if (!data) return <LoadState loading={loading} error={error} data={data} reload={reload} />;
  const rows = data.filter((o) => (tab === "active") === (!o.cancelled && o.stage < 4));
  return (
    <Screen refreshControl={<RefreshControl refreshing={false} onRefresh={reload} />}>
      <Row><Chip label="Active" active={tab === "active"} onPress={() => setTab("active")} /><Chip label="Past" active={tab === "past"} onPress={() => setTab("past")} /></Row>
      {rows.length === 0 ? <Muted style={{ marginTop: 20, textAlign: "center" }}>{tab === "active" ? "No active orders. Book a pickup from Home." : "No past orders yet."}</Muted> : null}
      {rows.map((o) => (
        <Card key={o.id} onPress={() => navigation.navigate("Tracking", { orderId: o.id })}>
          <Row style={{ justifyContent: "space-between" }}><Text style={{ fontWeight: "800", color: C.navy }}>{o.code}</Text>
            <Pill text={o.status} color={o.cancelled ? C.danger : o.stage === 4 ? C.ok : C.primary} /></Row>
          <Muted style={{ marginTop: 4 }}>{o.service} · {o.provider} · {o.weight} kg</Muted>
          <Row style={{ justifyContent: "space-between", marginTop: 6 }}><Muted>{o.created_text}</Muted><Text style={{ fontWeight: "700" }}>{money(o.total)}</Text></Row>
          {!o.cancelled && o.payment_status !== "paid" ? <View style={{ marginTop: 6 }}><Pill text="Payment pending" color={C.warn} /></View> : null}
          {o.stage === 4 && !o.reviewed ? <View style={{ marginTop: 6 }}><Pill text="Rate this order" color={C.warn} /></View> : null}
        </Card>))}
    </Screen>
  );
}
