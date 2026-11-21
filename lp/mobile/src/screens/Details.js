
import React, { useCallback } from "react";
import { Image, Text, View } from "react-native";
import { api, money } from "../api";
import { img } from "../config";
import { useBooking } from "../booking";
import { C } from "../theme";
import { Btn, Card, Chip, H, LoadState, Muted, Row, Screen, Stars, useFocusLoad } from "../ui";

export default function Details({ navigation }) {
  const { booking, update } = useBooking();
  const { data, error, loading, reload } = useFocusLoad(async () => {
    const [d, reviews, services] = await Promise.all([api(`/providers/${booking.providerId}?service=${booking.service}`),
      api(`/providers/${booking.providerId}/reviews`), api("/services")]);
    return { ...d, reviews, services };
  }, [booking.providerId, booking.service]);
  if (!data) return <LoadState loading={loading} error={error} data={data} reload={reload} />;
  const { provider: p, service, reviews, services } = data;
  const hero = img(p.image_hero || p.image_list);
  return (
    <Screen pad={false}>
      {hero ? <Image source={{ uri: hero }} style={{ width: "100%", height: 190, backgroundColor: C.line }} /> : null}
      <View style={{ padding: 16, paddingBottom: 40 }}>
        <Text style={{ fontSize: 22, fontWeight: "800", color: C.navy }}>{p.name}</Text>
        <Row style={{ marginVertical: 6 }}><Stars value={p.rating} /><Muted style={{ marginLeft: 6 }}>{p.rating} · {p.review_count} reviews · {p.distance_km} km</Muted></Row>
        <Muted>{p.details_text}</Muted><Muted>{p.quality_text}</Muted>
        <H>Choose a service</H>
        <Row style={{ flexWrap: "wrap" }}>{services.map((s) => <Chip key={s.key} label={s.name} active={s.key === booking.service} onPress={() => update({ service: s.key, weight: null })} />)}</Row>
        <Card>
          <Row style={{ justifyContent: "space-between" }}><Text style={{ fontWeight: "700" }}>{service.label}</Text><Text style={{ fontWeight: "800", color: C.primary }}>{money(p.unit_price)}/kg</Text></Row>
          <Muted style={{ marginTop: 6 }}>Minimum order {money(p.min_order)} ({p.min_kg} kg) · {p.delivery_fee === 0 ? "Free delivery" : `Delivery ${money(p.delivery_fee)}, free above ${money(p.free_above)}`}</Muted>
        </Card>
        <H>Reviews</H>
        {reviews.slice(0, 3).map((r) => (
          <Card key={r.id}><Row style={{ justifyContent: "space-between" }}><Text style={{ fontWeight: "700" }}>{r.reviewer_name}</Text><Stars value={r.rating} size={13} /></Row>
            {r.comment ? <Muted style={{ marginTop: 4 }}>{r.comment}</Muted> : null}</Card>))}
        <Btn title="Book now" onPress={() => navigation.navigate("Schedule")} />
      </View>
    </Screen>
  );
}
