
import React, { useEffect, useState } from "react";
import { Text, View } from "react-native";
import { api, money } from "../api";
import { img } from "../config";
import { useBooking } from "../booking";
import { C } from "../theme";
import { Card, Chip, Err, Loading, Muted, Row, Screen, Stars, Thumb, Field } from "../ui";

const SORTS = [["rating", "Top rated"], ["price", "Lowest price"], ["distance", "Nearest"], ["pickup", "Fastest pickup"]];

export default function Providers({ navigation }) {
  const { booking, update } = useBooking();
  const [sort, setSort] = useState("rating"), [minRating, setMinRating] = useState(false), [cheap, setCheap] = useState(false), [q, setQ] = useState("");
  const [rows, setRows] = useState(null), [err, setErr] = useState("");

  useEffect(() => {
    let live = true;
    const qs = `service=${booking.service}&sort=${sort}${minRating ? "&rating=4.8" : ""}${cheap ? "&price=80" : ""}&q=${encodeURIComponent(q)}`;
    api(`/providers?${qs}`).then((d) => live && (setRows(d), setErr(""))).catch((e) => live && setErr(e.message));
    return () => { live = false; };
  }, [booking.service, sort, minRating, cheap, q]);

  return (
    <Screen>
      <Field value={q} onChangeText={setQ} placeholder="Search providers" />
      <Row style={{ flexWrap: "wrap" }}>{SORTS.map(([k, l]) => <Chip key={k} label={l} active={sort === k} onPress={() => setSort(k)} />)}</Row>
      <Row style={{ flexWrap: "wrap", marginBottom: 8 }}>
        <Chip label="Rating 4.8+" active={minRating} onPress={() => setMinRating(!minRating)} />
        <Chip label="Under ₹80/kg" active={cheap} onPress={() => setCheap(!cheap)} />
      </Row>
      <Err text={err} />
      {!rows && !err ? <Loading /> : null}
      {rows && rows.length === 0 ? <Muted>No providers match these filters.</Muted> : null}
      {(rows || []).map((p) => (
        <Card key={p.id} onPress={() => { update({ providerId: p.id, weight: null }); navigation.navigate("Details"); }}>
          <Row>
            <Thumb uri={img(p.image_list)} size={72} />
            <View style={{ flex: 1, marginLeft: 12 }}>
              <Text style={{ fontSize: 16, fontWeight: "700", color: C.navy }}>{p.name}</Text>
              <Row style={{ marginVertical: 3 }}><Stars value={p.rating} size={13} /><Muted style={{ marginLeft: 6 }}>{p.rating} ({p.review_count})</Muted></Row>
              <Muted>{p.distance_km} km · {p.pickup_text}</Muted>
            </View>
            <View style={{ alignItems: "flex-end" }}>
              <Text style={{ fontWeight: "800", color: C.primary, fontSize: 16 }}>{money(p.unit_price)}</Text><Muted>per kg</Muted>
            </View>
          </Row>
        </Card>))}
    </Screen>
  );
}
