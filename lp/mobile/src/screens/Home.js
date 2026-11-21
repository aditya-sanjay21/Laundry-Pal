
import React from "react";
import { Pressable, RefreshControl, Text, View } from "react-native";
import { Ionicons } from "@expo/vector-icons";
import { api } from "../api";
import { img } from "../config";
import { useBooking } from "../booking";
import { C } from "../theme";
import { Card, H, LoadState, Muted, Pill, Row, Screen, Thumb, useFocusLoad } from "../ui";

export default function Home({ navigation }) {
  const { update } = useBooking();
  const { data, error, loading, reload } = useFocusLoad(async () => {
    const [me, services] = await Promise.all([api("/me"), api("/services")]);
    let latest = null;
    try { latest = await api("/orders/latest"); } catch { /* no orders yet */ }
    return { me, services, latest };
  }, []);
  if (!data) return <LoadState loading={loading} error={error} data={data} reload={reload} />;
  const { me, services, latest } = data, active = latest && !latest.cancelled && latest.stage < 4;
  return (
    <Screen refreshControl={<RefreshControl refreshing={false} onRefresh={reload} />}>
      <Text style={{ fontSize: 24, fontWeight: "800", color: C.navy }}>Hi, {me.user.name.split(" ")[0]}</Text>
      <Row style={{ marginTop: 4, marginBottom: 16 }}>
        <Ionicons name="location-outline" size={16} color={C.primary} />
        <Muted style={{ marginLeft: 4, flex: 1 }}>{me.default_address ? me.default_address.short : "Add a pickup address in Profile"}</Muted>
      </Row>
      {active ? (
        <Card onPress={() => navigation.navigate("Tracking", { orderId: latest.id })} style={{ backgroundColor: C.tint, borderColor: C.primary }}>
          <Row style={{ justifyContent: "space-between" }}>
            <Text style={{ fontWeight: "700", color: C.navy }}>Active order {latest.code}</Text><Pill text={latest.status} />
          </Row>
          <Muted style={{ marginTop: 4 }}>{latest.service} · {latest.provider} · Tap to track</Muted>
        </Card>) : null}
      <H>What do you need?</H>
      {services.map((s) => (
        <Card key={s.key} onPress={() => { update({ service: s.key, providerId: null, weight: null }); navigation.navigate("Providers"); }}>
          <Row>
            <Thumb uri={img(s.image)} size={72} />
            <View style={{ flex: 1, marginLeft: 12 }}>
              <Text style={{ fontSize: 17, fontWeight: "700", color: C.navy }}>{s.name}</Text>
              <Muted>{s.subtitle}</Muted>
            </View>
            <Ionicons name="chevron-forward" size={20} color={C.muted} />
          </Row>
        </Card>))}
    </Screen>
  );
}
