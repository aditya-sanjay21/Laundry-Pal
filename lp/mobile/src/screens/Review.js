
import React, { useState } from "react";
import { Text } from "react-native";
import { api } from "../api";
import { C } from "../theme";
import { Btn, Err, Field, Muted, Screen, Stars } from "../ui";

export default function Review({ route, navigation }) {
  const [rating, setRating] = useState(0), [comment, setComment] = useState(""), [err, setErr] = useState(""), [busy, setBusy] = useState(false);
  async function submit() {
    if (!rating) return setErr("Please choose a rating from 1 to 5.");
    setErr(""); setBusy(true);
    try { await api(`/orders/${route.params.orderId}/review`, { method: "POST", body: { rating, comment } }); navigation.goBack(); }
    catch (e) { setErr(e.message); setBusy(false); }
  }
  return (
    <Screen>
      <Text style={{ fontSize: 20, fontWeight: "800", color: C.navy, marginBottom: 4 }}>How was your order?</Text>
      <Muted style={{ marginBottom: 14 }}>Your rating helps other customers choose a provider.</Muted>
      <Stars value={rating} size={40} onChange={setRating} />
      <Field label="Comment (optional)" value={comment} onChangeText={setComment} multiline style={{ height: 100, paddingTop: 10, textAlignVertical: "top" }} autoCapitalize="sentences" />
      <Err text={err} />
      <Btn title="Submit review" onPress={submit} busy={busy} />
    </Screen>
  );
}
