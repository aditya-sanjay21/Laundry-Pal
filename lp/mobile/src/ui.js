import React, { useCallback, useState } from "react";
import { ActivityIndicator, Image, Pressable, ScrollView, StyleSheet, Text, TextInput, View } from "react-native";
import { Ionicons } from "@expo/vector-icons";
import { useFocusEffect } from "@react-navigation/native";
import { C } from "./theme";

// Loads data every time the screen comes into focus (so lists are fresh after booking, cancelling, etc.).
export function useFocusLoad(fn, deps = []) {
  const [data, setData] = useState(null);
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(true);
  const load = useCallback(async () => {
    try { setError(""); setData(await fn()); } catch (e) { setError(e.message); } finally { setLoading(false); }
  }, deps); // eslint-disable-line
  useFocusEffect(useCallback(() => { load(); }, [load]));
  return { data, error, loading, reload: load };
}

export const Screen = ({ children, refreshControl, pad = true }) => (
  <ScrollView style={{ flex: 1, backgroundColor: C.bg }} refreshControl={refreshControl} keyboardShouldPersistTaps="handled"
    contentContainerStyle={pad ? { padding: 16, paddingBottom: 40 } : undefined}>{children}</ScrollView>
);

export const Card = ({ children, style, onPress }) => {
  const Body = onPress ? Pressable : View;
  return <Body onPress={onPress} style={[st.card, style]}>{children}</Body>;
};

export const H = ({ children }) => <Text style={st.h}>{children}</Text>;
export const Muted = ({ children, style }) => <Text style={[{ color: C.muted, fontSize: 13 }, style]}>{children}</Text>;

export function Btn({ title, onPress, kind = "primary", busy, disabled, icon, style }) {
  const solid = kind === "primary", danger = kind === "danger";
  return (
    <Pressable onPress={onPress} disabled={busy || disabled}
      style={[st.btn, solid && { backgroundColor: C.primary }, !solid && { borderWidth: 1.5, borderColor: danger ? C.danger : C.primary },
        (busy || disabled) && { opacity: 0.5 }, style]}>
      {busy ? <ActivityIndicator color={solid ? "#fff" : C.primary} /> : (
        <View style={{ flexDirection: "row", alignItems: "center", gap: 8 }}>
          {icon ? <Ionicons name={icon} size={18} color={solid ? "#fff" : danger ? C.danger : C.primary} /> : null}
          <Text style={{ color: solid ? "#fff" : danger ? C.danger : C.primary, fontWeight: "700", fontSize: 16 }}>{title}</Text>
        </View>)}
    </Pressable>
  );
}

export const Field = ({ label, ...p }) => (
  <View style={{ marginBottom: 12 }}>
    {label ? <Text style={st.label}>{label}</Text> : null}
    <TextInput placeholderTextColor="#9AA7B0" autoCapitalize="none" {...p} style={[st.input, p.style]} />
  </View>
);

export const Chip = ({ label, active, onPress }) => (
  <Pressable onPress={onPress} style={[st.chip, active && { backgroundColor: C.primary, borderColor: C.primary }]}>
    <Text style={{ color: active ? "#fff" : C.text, fontWeight: "600" }}>{label}</Text>
  </Pressable>
);

export const Row = ({ children, style }) => <View style={[{ flexDirection: "row", alignItems: "center" }, style]}>{children}</View>;
export const Err = ({ text }) => (text ? <Text style={{ color: C.danger, marginVertical: 8, fontWeight: "600" }}>{text}</Text> : null);
export const Loading = () => <View style={{ flex: 1, justifyContent: "center", padding: 40 }}><ActivityIndicator size="large" color={C.primary} /></View>;

export function LoadState({ loading, error, data, reload }) {
  if (loading && !data) return <Loading />;
  if (error && !data) return <View style={{ padding: 24 }}><Err text={error} /><Btn title="Try again" onPress={reload} kind="outline" /></View>;
  return null;
}

export function Stars({ value, size = 16, onChange }) {
  return (
    <Row>{[1, 2, 3, 4, 5].map((n) => (
      <Pressable key={n} disabled={!onChange} onPress={() => onChange(n)}>
        <Ionicons name={n <= Math.round(value) ? "star" : "star-outline"} size={size} color="#F5A623" />
      </Pressable>))}</Row>
  );
}

export const Pill = ({ text, color = C.primary }) => (
  <View style={{ backgroundColor: color + "22", paddingHorizontal: 10, paddingVertical: 4, borderRadius: 12 }}>
    <Text style={{ color, fontWeight: "700", fontSize: 12 }}>{text}</Text>
  </View>
);

export const Thumb = ({ uri, size = 64, round }) => (
  uri ? <Image source={{ uri }} style={{ width: size, height: size, borderRadius: round ? size / 2 : 12, backgroundColor: C.line }} />
      : <View style={{ width: size, height: size, borderRadius: round ? size / 2 : 12, backgroundColor: C.line }} />
);

const st = StyleSheet.create({
  card: { backgroundColor: C.card, borderRadius: 14, padding: 14, marginBottom: 12, borderWidth: 1, borderColor: C.line },
  h: { fontSize: 18, fontWeight: "700", color: C.navy, marginBottom: 10, marginTop: 6 },
  btn: { height: 50, borderRadius: 12, alignItems: "center", justifyContent: "center", paddingHorizontal: 16, marginTop: 8 },
  label: { fontSize: 13, color: C.muted, marginBottom: 4, fontWeight: "600" },
  input: { backgroundColor: "#fff", borderWidth: 1, borderColor: C.line, borderRadius: 10, paddingHorizontal: 12, height: 48, fontSize: 16, color: C.text },
  chip: { borderWidth: 1, borderColor: C.line, backgroundColor: "#fff", paddingHorizontal: 14, paddingVertical: 8, borderRadius: 20, marginRight: 8, marginBottom: 8 },
});
