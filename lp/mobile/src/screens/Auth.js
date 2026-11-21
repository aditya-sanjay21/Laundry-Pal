
import React, { useState } from "react";
import { Text, View } from "react-native";
import { SafeAreaView } from "react-native-safe-area-context";
import { api } from "../api";
import { useAuth } from "../auth";
import { Btn, Err, Field, Muted, Screen } from "../ui";
import { C } from "../theme";

const Brand = ({ sub }) => (
  <View style={{ alignItems: "center", marginVertical: 28 }}>
    <Text style={{ fontSize: 34, fontWeight: "800", color: C.primary }}>Laundry Pal</Text>
    <Muted style={{ marginTop: 6 }}>{sub}</Muted>
  </View>
);

export function Login({ navigation }) {
  const { signIn } = useAuth();
  const [id, setId] = useState(""), [pw, setPw] = useState(""), [err, setErr] = useState(""), [busy, setBusy] = useState(false);
  async function submit() {
    setErr(""); setBusy(true);
    try { const d = await api("/auth/login", { method: "POST", body: { identifier: id, password: pw } }); await signIn(d.token); }
    catch (e) { setErr(e.message); setBusy(false); }
  }
  return (
    <SafeAreaView style={{ flex: 1, backgroundColor: C.bg }}>
      <Screen>
        <Brand sub="Laundry picked up and delivered to your door" />
        <Field label="Email or phone" value={id} onChangeText={setId} keyboardType="email-address" placeholder="rahul.sharma@email.com" />
        <Field label="Password" value={pw} onChangeText={setPw} secureTextEntry placeholder="At least 6 characters" />
        <Err text={err} />
        <Btn title="Log in" onPress={submit} busy={busy} />
        <Btn title="Create an account" kind="outline" onPress={() => navigation.navigate("Signup")} />
        <Muted style={{ textAlign: "center", marginTop: 20 }}>Demo account: rahul.sharma@email.com / demo123</Muted>
      </Screen>
    </SafeAreaView>
  );
}

export function Signup({ navigation }) {
  const { signIn } = useAuth();
  const [f, setF] = useState({ name: "", email: "", phone: "", password: "" }), [err, setErr] = useState(""), [busy, setBusy] = useState(false);
  const set = (k) => (v) => setF((x) => ({ ...x, [k]: v }));
  async function submit() {
    setErr(""); setBusy(true);
    try { const d = await api("/auth/signup", { method: "POST", body: f }); await signIn(d.token); }
    catch (e) { setErr(e.message); setBusy(false); }
  }
  return (
    <SafeAreaView style={{ flex: 1, backgroundColor: C.bg }}>
      <Screen>
        <Brand sub="Create your account" />
        <Field label="Full name" value={f.name} onChangeText={set("name")} autoCapitalize="words" />
        <Field label="Email" value={f.email} onChangeText={set("email")} keyboardType="email-address" />
        <Field label="Mobile number" value={f.phone} onChangeText={set("phone")} keyboardType="phone-pad" placeholder="10-digit number" />
        <Field label="Password" value={f.password} onChangeText={set("password")} secureTextEntry placeholder="At least 6 characters" />
        <Err text={err} />
        <Btn title="Sign up" onPress={submit} busy={busy} />
        <Btn title="I already have an account" kind="outline" onPress={() => navigation.goBack()} />
      </Screen>
    </SafeAreaView>
  );
}
