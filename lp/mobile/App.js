import React from "react";
import { StatusBar } from "expo-status-bar";
import { NavigationContainer, DefaultTheme } from "@react-navigation/native";
import { createNativeStackNavigator } from "@react-navigation/native-stack";
import { createBottomTabNavigator } from "@react-navigation/bottom-tabs";
import { SafeAreaProvider } from "react-native-safe-area-context";
import { Ionicons } from "@expo/vector-icons";
import { AuthProvider, useAuth } from "./src/auth";
import { BookingProvider } from "./src/booking";
import { C } from "./src/theme";
import { Loading } from "./src/ui";
import { Login, Signup } from "./src/screens/Auth";
import Home from "./src/screens/Home";
import Providers from "./src/screens/Providers";
import Details from "./src/screens/Details";
import Schedule from "./src/screens/Schedule";
import Checkout from "./src/screens/Checkout";
import Tracking from "./src/screens/Tracking";
import Orders from "./src/screens/Orders";
import Review from "./src/screens/Review";
import Profile from "./src/screens/Profile";
import Addresses from "./src/screens/Addresses";

const Stack = createNativeStackNavigator();
const Tab = createBottomTabNavigator();
const theme = { ...DefaultTheme, colors: { ...DefaultTheme.colors, background: C.bg, primary: C.primary } };
const header = { headerTintColor: C.navy, headerStyle: { backgroundColor: "#fff" }, headerTitleStyle: { fontWeight: "700" } };

function Tabs() {
  const icons = { Home: "home", Orders: "receipt", Profile: "person" };
  return (
    <Tab.Navigator screenOptions={({ route }) => ({ ...header, tabBarActiveTintColor: C.primary,
      tabBarIcon: ({ color, size }) => <Ionicons name={icons[route.name]} size={size} color={color} /> })}>
      <Tab.Screen name="Home" component={Home} options={{ title: "Laundry Pal" }} />
      <Tab.Screen name="Orders" component={Orders} options={{ title: "My Orders" }} />
      <Tab.Screen name="Profile" component={Profile} />
    </Tab.Navigator>
  );
}

function Root() {
  const { token, ready } = useAuth();
  if (!ready) return <Loading />;
  if (!token) {
    return (
      <Stack.Navigator screenOptions={{ headerShown: false }}>
        <Stack.Screen name="Login" component={Login} /><Stack.Screen name="Signup" component={Signup} />
      </Stack.Navigator>);
  }
  return (
    <Stack.Navigator screenOptions={header}>
      <Stack.Screen name="Tabs" component={Tabs} options={{ headerShown: false }} />
      <Stack.Screen name="Providers" component={Providers} options={{ title: "Nearby providers" }} />
      <Stack.Screen name="Details" component={Details} options={{ title: "Provider details" }} />
      <Stack.Screen name="Schedule" component={Schedule} options={{ title: "Schedule pickup" }} />
      <Stack.Screen name="Checkout" component={Checkout} options={{ title: "Review & Payment" }} />
      <Stack.Screen name="Tracking" component={Tracking} options={{ title: "Track order" }} />
      <Stack.Screen name="Review" component={Review} options={{ title: "Rate provider" }} />
      <Stack.Screen name="Addresses" component={Addresses} options={{ title: "My addresses" }} />
    </Stack.Navigator>);
}

export default function App() {
  return (
    <SafeAreaProvider>
      <AuthProvider><BookingProvider>
        <NavigationContainer theme={theme}><Root /></NavigationContainer>
        <StatusBar style="dark" />
      </BookingProvider></AuthProvider>
    </SafeAreaProvider>
  );
}
