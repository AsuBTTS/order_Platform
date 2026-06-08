import { createRouter, createWebHistory } from "vue-router";

import HomeView from "../views/HomeView.vue";
import LoginView from "../views/LoginView.vue";
import RegisterView from "../views/RegisterView.vue";
import DishListView from "../views/DishListView.vue";
import DishDetailView from "../views/DishDetailView.vue";
import CartView from "../views/CartView.vue";
import OrderListView from "../views/OrderListView.vue";
import OrderDetailView from "../views/OrderDetailView.vue";
import PaymentView from "../views/PaymentView.vue";
import ProfileView from "../views/ProfileView.vue";
import ProfileEditView from "../views/ProfileEditView.vue";
import ChangePasswordView from "../views/ChangePasswordView.vue";
import MerchantHomeView from "../views/MerchantHomeView.vue";
import MerchantLoginView from "../views/MerchantLoginView.vue";
import MerchantInventoryView from "../views/MerchantInventoryView.vue";
import MerchantOrdersView from "../views/MerchantOrdersView.vue";
import DeliveryLoginView from "../views/DeliveryLoginView.vue";
import DeliveryOrdersView from "../views/DeliveryOrdersView.vue";
import PlatformLoginView from "../views/PlatformLoginView.vue";
import PlatformDashboardView from "../views/PlatformDashboardView.vue";
import { getCustomerId, getDriverId, getMerchantId, getPlatformAdminId } from "../utils/session";

const routes = [
  { path: "/", redirect: "/home" },
  { path: "/home", name: "home", component: HomeView, meta: { requiresCustomer: true } },
  { path: "/login", name: "login", component: LoginView },
  { path: "/register", name: "register", component: RegisterView },
  { path: "/dishes", name: "dishes", component: DishListView, meta: { requiresCustomer: true } },
  { path: "/dishes/:id", name: "dish-detail", component: DishDetailView, meta: { requiresCustomer: true } },
  { path: "/cart", name: "cart", component: CartView, meta: { requiresCustomer: true } },
  { path: "/orders", name: "orders", component: OrderListView, meta: { requiresCustomer: true } },
  { path: "/orders/:id", name: "order-detail", component: OrderDetailView, meta: { requiresCustomer: true } },
  { path: "/payment/:orderId", name: "payment", component: PaymentView, meta: { requiresCustomer: true } },
  { path: "/profile", name: "profile", component: ProfileView, meta: { requiresCustomer: true } },
  { path: "/profile/edit", name: "profile-edit", component: ProfileEditView, meta: { requiresCustomer: true } },
  { path: "/profile/password", name: "change-password", component: ChangePasswordView, meta: { requiresCustomer: true } },
  { path: "/merchant", redirect: "/merchant/home" },
  { path: "/merchant/login", name: "merchant-login", component: MerchantLoginView, meta: { merchantLayout: true } },
  { path: "/merchant/home", name: "merchant-home", component: MerchantHomeView, meta: { requiresMerchant: true, merchantLayout: true } },
  { path: "/merchant/inventory", name: "merchant-inventory", component: MerchantInventoryView, meta: { requiresMerchant: true, merchantLayout: true } },
  { path: "/merchant/orders", name: "merchant-orders", component: MerchantOrdersView, meta: { requiresMerchant: true, merchantLayout: true } },
  { path: "/delivery", redirect: "/delivery/orders" },
  { path: "/delivery/login", name: "delivery-login", component: DeliveryLoginView, meta: { deliveryLayout: true } },
  { path: "/delivery/orders", name: "delivery-orders", component: DeliveryOrdersView, meta: { requiresDriver: true, deliveryLayout: true } },
  { path: "/platform", redirect: "/platform/dashboard" },
  { path: "/platform/login", name: "platform-login", component: PlatformLoginView, meta: { platformLayout: true } },
  { path: "/platform/dashboard", name: "platform-dashboard", component: PlatformDashboardView, meta: { requiresPlatformAdmin: true, platformLayout: true } },
];

const router = createRouter({
  history: createWebHistory(),
  routes,
});

router.beforeEach((to) => {
  if (to.meta.requiresMerchant && !getMerchantId()) {
    return { name: "merchant-login", query: { redirect: to.fullPath } };
  }
  if (to.name === "merchant-login" && getMerchantId()) {
    return { name: "merchant-home" };
  }
  if (to.meta.requiresDriver && !getDriverId()) {
    return { name: "delivery-login", query: { redirect: to.fullPath } };
  }
  if (to.name === "delivery-login" && getDriverId()) {
    return { name: "delivery-orders" };
  }
  if (to.meta.requiresPlatformAdmin && !getPlatformAdminId()) {
    return { name: "platform-login", query: { redirect: to.fullPath } };
  }
  if (to.name === "platform-login" && getPlatformAdminId()) {
    return { name: "platform-dashboard" };
  }
  if (to.meta.requiresCustomer && !getCustomerId()) {
    return { name: "login", query: { redirect: to.fullPath } };
  }
  if (to.name === "login" && getCustomerId()) {
    return { name: "home" };
  }
  if (to.name === "register" && getCustomerId()) {
    return { name: "home" };
  }
  return true;
});

export default router;
