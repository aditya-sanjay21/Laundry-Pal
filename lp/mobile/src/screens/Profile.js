
import React, { useState } from "react";
import { Text, View } from "react-native";
import { api } from "../api";
import { img } from "../config";
import { useAuth } from "../auth";
import { C } from "../theme";
import { Btn, Card, Err, Field, LoadState, Muted, Row, Screen, Thumb, useFocusLoad } from "../ui";

export default function Profile({ navigation }) {
  const { signOut } = useAuth();
  const { data, error, loading, reload } = useFocusLoad(() => api("/me"), []);
  const [edit, setEdit] = useState(false), [f, setF] = useState({}), [err, setErr] = useState(""), [busy, setBusy] = useState(false);
  if (!data) return <LoadState loading={loading} error={error} data={data} reload={reload} />;
  const { user, counters } = data;
  const set = (k) => (v) => setF((x) => ({ ...x, [k]: v }));
  async function save() {
    setErr(""); setBusy(true);
    try { await api("/me", { method: "PUT", body: f }); setEdit(false); await reload(); } catch (e) { setErr(e.message); }
    setBusy(false);
  }
  return (
    <Screen>
      <Card>
        <Row>
          <Thumb uri={img(user.photo)} size={64} round />
          <View style={{ marginLeft: 14, flex: 1 }}>
            <Text style={{ fontSize: 19, fontWeight: "800", color: C.navy }}>{user.name}</Text><Muted>{user.email}</Muted><Muted>{user.phone_pretty}</Muted>
          </View>
        </Row>
        {edit ? (
          <View style={{ marginTop: 14 }}>
            <Field label="Full name" value={f.name} onChangeText={set("name")} autoCapitalize="words" />
            <Field label="Email" value={f.email} onChangeText={set("email")} keyboardType="email-address" />
            <Field label="Mobile number" value={f.phone} onChangeText={set("phone")} keyboardType="phone-pad" />
            <Err text={err} />
            <Btn title="Save changes" onPress={save} busy={busy} /><Btn title="Cancel" kind="outline" onPress={() => setEdit(false)} />
          </View>) : <Btn title="Edit profile" kind="outline" onPress={() => { setF({ name: user.name, email: user.email, phone: user.phone }); setEdit(true); }} />}
      </Card>
      <Card>
        <Text style={{ fontWeight: "700", color: C.navy, marginBottom: 10 }}>My orders</Text>
        <Row style={{ justifyContent: "space-around" }}>
          {[["Current", counters.current], ["In progress", counters.picked], ["Delivered", counters.delivered], ["Cancelled", counters.cancelled]].map(([k, v]) => (
            <View key={k} style={{ alignItems: "center" }}><Text style={{ fontSize: 22, fontWeight: "800", color: C.primary }}>{v}</Text><Muted>{k}</Muted></View>))}
        </Row>
        <Btn title="View all orders" kind="outline" onPress={() => navigation.navigate("Orders")} />
      </Card>
      <Btn title="Manage addresses" kind="outline" onPress={() => navigation.navigate("Addresses")} />
      <Btn title="Sign out" kind="danger" onPress={signOut} />
    </Screen>
  );
}
