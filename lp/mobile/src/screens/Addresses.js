
import React, { useState } from "react";
import { Alert, Switch, Text, View } from "react-native";
import { api } from "../api";
import { C } from "../theme";
import { Btn, Card, Err, Field, H, LoadState, Muted, Pill, Row, Screen, useFocusLoad } from "../ui";

const EMPTY = { label: "", street: "", area: "", city: "", pincode: "", make_default: false };

export default function Addresses() {
  const { data, error, loading, reload } = useFocusLoad(() => api("/addresses"), []);
  const [form, setForm] = useState(null), [err, setErr] = useState(""), [busy, setBusy] = useState(false);
  if (!data) return <LoadState loading={loading} error={error} data={data} reload={reload} />;
  const set = (k) => (v) => setForm((x) => ({ ...x, [k]: v }));
  const act = async (fn) => { setErr(""); try { await fn(); await reload(); } catch (e) { setErr(e.message); } };
  async function save() {
    setBusy(true); setErr("");
    try { await api("/addresses", { method: "POST", body: form }); setForm(null); await reload(); } catch (e) { setErr(e.message); }
    setBusy(false);
  }
  const remove = (a) => Alert.alert("Delete address?", a.full, [{ text: "Keep" },
    { text: "Delete", style: "destructive", onPress: () => act(() => api(`/addresses/${a.id}`, { method: "DELETE" })) }]);
  return (
    <Screen>
      {data.map((a) => (
        <Card key={a.id}>
          <Row style={{ justifyContent: "space-between" }}><Text style={{ fontWeight: "800", color: C.navy }}>{a.label}</Text>{a.is_default ? <Pill text="Default" /> : null}</Row>
          <Muted style={{ marginVertical: 4 }}>{a.full}</Muted>
          <Row>
            {!a.is_default ? <Btn title="Make default" kind="outline" style={{ height: 40, marginRight: 8 }} onPress={() => act(() => api(`/addresses/${a.id}/default`, { method: "PUT" }))} /> : null}
            <Btn title="Delete" kind="danger" style={{ height: 40 }} onPress={() => remove(a)} />
          </Row>
        </Card>))}
      <Err text={err} />
      {form ? (
        <View>
          <H>New address</H>
          <Field label="Label" value={form.label} onChangeText={set("label")} placeholder="Home, Work..." autoCapitalize="words" />
          <Field label="House and street" value={form.street} onChangeText={set("street")} autoCapitalize="words" />
          <Field label="Area" value={form.area} onChangeText={set("area")} autoCapitalize="words" />
          <Field label="City" value={form.city} onChangeText={set("city")} autoCapitalize="words" />
          <Field label="Pincode" value={form.pincode} onChangeText={set("pincode")} keyboardType="number-pad" maxLength={6} />
          <Row style={{ justifyContent: "space-between" }}><Muted>Make this my default address</Muted><Switch value={form.make_default} onValueChange={set("make_default")} /></Row>
          <Btn title="Save address" onPress={save} busy={busy} /><Btn title="Cancel" kind="outline" onPress={() => setForm(null)} />
        </View>) : <Btn title="Add a new address" onPress={() => setForm(EMPTY)} />}
    </Screen>
  );
}
