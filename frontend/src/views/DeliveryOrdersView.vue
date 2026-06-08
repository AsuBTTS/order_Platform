<template>
  <section class="delivery-view">
    <header class="delivery-hero">
      <div>
        <p class="eyebrow">Delivery Desk</p>
        <h2 class="title">配送任务</h2>
        <span>花神咖啡馆 · 骑手端</span>
      </div>
      <button class="ghost-btn" @click="loadOrders">刷新</button>
    </header>

    <section class="card driver-card">
      <div>
        <span>当前骑手</span>
        <strong>{{ driver?.username || "driver" }}</strong>
      </div>
      <button class="secondary-btn logout-text" type="button" @click="logout">退出登录</button>
    </section>

    <section class="task-summary">
      <div class="card">
        <span>新任务</span>
        <strong>{{ newOrders.length }}</strong>
      </div>
      <div class="card">
        <span>待取餐</span>
        <strong>{{ acceptedOrders.length }}</strong>
      </div>
      <div class="card">
        <span>配送中</span>
        <strong>{{ deliveringOrders.length }}</strong>
      </div>
    </section>

    <nav class="task-tabs" aria-label="配送任务分类">
      <button
        v-for="tab in tabs"
        :key="tab.key"
        :class="{ active: activeTab === tab.key }"
        type="button"
        @click="activeTab = tab.key"
      >
        {{ tab.label }}
      </button>
    </nav>

    <p v-if="error" class="danger-text">{{ error }}</p>
    <p v-if="message" class="success-text">{{ message }}</p>
    <div v-if="loading" class="loading">正在加载配送订单...</div>

    <div v-else-if="visibleOrders.length === 0" class="empty-state card">
      <strong>{{ emptyTitle }}</strong>
      <p class="muted">商家完成外送订单制作后，可接任务会出现在这里。</p>
    </div>

    <div v-else class="delivery-list">
      <article v-for="order in visibleOrders" :key="order.id" class="card delivery-order">
        <div class="order-head">
          <div>
            <strong>{{ order.order_no }}</strong>
            <p>{{ order.customer_username }} · {{ deliveryText(order.delivery_type) }}</p>
          </div>
          <span class="status-pill">{{ riderStatusText(order) }}</span>
        </div>

        <div class="route-card">
          <div>
            <span>取餐门店</span>
            <strong>{{ order.merchant_username || "花神咖啡馆" }}</strong>
          </div>
          <div>
            <span>送达顾客</span>
            <strong>{{ order.customer_username }}</strong>
          </div>
        </div>

        <div class="order-items">
          <div v-for="item in order.items" :key="item.id">
            <span>{{ item.dish_name }}</span>
            <em>x{{ item.quantity }}</em>
            <b>{{ money(item.subtotal) }}</b>
          </div>
        </div>

        <div class="order-total">
          <span>{{ actionMeta(order).hint }}</span>
          <strong>{{ money(order.total_amount) }}</strong>
        </div>

        <div class="order-actions">
          <button class="primary-btn" :disabled="operatingId === order.id" @click="handlePrimaryAction(order)">
            {{ operatingId === order.id ? "处理中..." : actionMeta(order).button }}
          </button>
        </div>
      </article>
    </div>
  </section>
</template>

<script setup>
import { computed, onMounted, ref } from "vue";
import { useRouter } from "vue-router";

import {
  acceptDeliveryOrder,
  deliveredDeliveryOrder,
  fetchDeliveryOrders,
  pickupDeliveryOrder,
} from "../api/delivery";
import { deliveryText, money } from "../utils/format";
import { clearStoredDriver, getDriverId, getStoredDriver } from "../utils/session";

const router = useRouter();
const driver = ref(getStoredDriver());
const orders = ref([]);
const activeTab = ref("new");
const loading = ref(true);
const operatingId = ref(null);
const error = ref("");
const message = ref("");

const newOrders = computed(() => orders.value.filter((order) => order.status === "waiting_delivery" && !order.driver));
const acceptedOrders = computed(() =>
  orders.value.filter((order) => order.status === "waiting_delivery" && Number(order.driver) === Number(getDriverId())),
);
const deliveringOrders = computed(() =>
  orders.value.filter((order) => order.status === "delivering" && Number(order.driver) === Number(getDriverId())),
);

const tabs = computed(() => [
  { key: "new", label: `新任务 ${newOrders.value.length}` },
  { key: "accepted", label: `待取餐 ${acceptedOrders.value.length}` },
  { key: "delivering", label: `配送中 ${deliveringOrders.value.length}` },
]);

const visibleOrders = computed(() => {
  if (activeTab.value === "accepted") {
    return acceptedOrders.value;
  }
  if (activeTab.value === "delivering") {
    return deliveringOrders.value;
  }
  return newOrders.value;
});

const emptyTitle = computed(() => {
  if (activeTab.value === "accepted") {
    return "暂无待取餐订单";
  }
  if (activeTab.value === "delivering") {
    return "暂无配送中订单";
  }
  return "暂无新任务";
});

function riderStatusText(order) {
  if (order.status === "waiting_delivery" && !order.driver) {
    return "可接单";
  }
  if (order.status === "waiting_delivery") {
    return "待取餐";
  }
  if (order.status === "delivering") {
    return "配送中";
  }
  return order.status;
}

function actionMeta(order) {
  if (order.status === "waiting_delivery" && !order.driver) {
    return { button: "接单", hint: "新任务 · 等待骑手接单" };
  }
  if (order.status === "waiting_delivery") {
    return { button: "取餐", hint: "已接单 · 前往门店取餐" };
  }
  return { button: "送达", hint: "配送中 · 尽快送达顾客" };
}

async function loadOrders() {
  loading.value = true;
  error.value = "";
  message.value = "";

  try {
    const { data } = await fetchDeliveryOrders(getDriverId());
    orders.value = data.orders;
  } catch (err) {
    error.value = err.message;
  } finally {
    loading.value = false;
  }
}

async function handlePrimaryAction(order) {
  if (order.status === "waiting_delivery" && !order.driver) {
    await acceptOrder(order);
  } else if (order.status === "waiting_delivery") {
    await pickupOrder(order);
  } else if (order.status === "delivering") {
    await deliveredOrder(order);
  }
}

async function acceptOrder(order) {
  operatingId.value = order.id;
  error.value = "";
  message.value = "";
  try {
    await acceptDeliveryOrder(getDriverId(), order.id);
    message.value = "接单成功，请前往门店取餐。";
    activeTab.value = "accepted";
    await loadOrders();
  } catch (err) {
    error.value = err.message;
  } finally {
    operatingId.value = null;
  }
}

async function pickupOrder(order) {
  operatingId.value = order.id;
  error.value = "";
  message.value = "";
  try {
    await pickupDeliveryOrder(getDriverId(), order.id);
    message.value = "已取餐，订单进入配送中。";
    activeTab.value = "delivering";
    await loadOrders();
  } catch (err) {
    error.value = err.message;
  } finally {
    operatingId.value = null;
  }
}

async function deliveredOrder(order) {
  operatingId.value = order.id;
  error.value = "";
  message.value = "";
  try {
    await deliveredDeliveryOrder(getDriverId(), order.id);
    message.value = "已送达，订单已完成。";
    await loadOrders();
  } catch (err) {
    error.value = err.message;
  } finally {
    operatingId.value = null;
  }
}

function logout() {
  clearStoredDriver();
  router.push("/delivery/login");
}

onMounted(loadOrders);
</script>

<style scoped>
.delivery-view {
  display: grid;
  gap: 14px;
}

.delivery-hero {
  align-items: end;
  background:
    linear-gradient(135deg, rgba(16, 63, 52, 0.95), rgba(16, 63, 52, 0.42)),
    url("/hero.png") center / cover;
  border-radius: 30px;
  color: #ffffff;
  display: flex;
  justify-content: space-between;
  min-height: 210px;
  padding: 20px;
}

.delivery-hero .eyebrow,
.delivery-hero span {
  color: rgba(255, 255, 255, 0.9);
}

.driver-card {
  align-items: center;
  display: flex;
  gap: 14px;
  justify-content: space-between;
  padding: 16px;
}

.driver-card span,
.task-summary span,
.route-card span {
  color: #6d766f;
  font-size: 13px;
  font-weight: 800;
}

.driver-card strong {
  display: block;
  font-size: 24px;
  margin-top: 6px;
}

.task-summary {
  display: grid;
  gap: 10px;
  grid-template-columns: repeat(3, 1fr);
}

.task-summary .card {
  display: grid;
  gap: 6px;
  padding: 13px 10px;
}

.task-summary strong {
  color: #103f34;
  font-size: 28px;
}

.task-tabs {
  background: #ffffff;
  border: 1px solid #e8ded0;
  border-radius: 18px;
  display: grid;
  gap: 5px;
  grid-template-columns: repeat(3, 1fr);
  padding: 5px;
}

.task-tabs button {
  background: transparent;
  border-radius: 14px;
  color: #68736d;
  font-size: 13px;
  font-weight: 900;
  min-height: 40px;
  padding: 0;
}

.task-tabs button.active {
  background: #dff2ea;
  color: #0e7a55;
}

.delivery-list {
  display: grid;
  gap: 14px;
}

.delivery-order {
  display: grid;
  gap: 14px;
  padding: 16px;
}

.order-head,
.order-total {
  align-items: center;
  display: flex;
  gap: 10px;
  justify-content: space-between;
}

.order-head strong {
  font-size: 17px;
}

.order-head p {
  color: #7a827d;
  margin: 5px 0 0;
}

.route-card {
  background: #f7f1e8;
  border-radius: 18px;
  display: grid;
  gap: 12px;
  padding: 14px;
}

.route-card div {
  display: grid;
  gap: 4px;
}

.route-card strong {
  color: #172920;
  font-size: 17px;
}

.order-items {
  background: #fbf8f3;
  border-radius: 16px;
  display: grid;
  gap: 9px;
  padding: 12px;
}

.order-items div {
  align-items: center;
  display: grid;
  gap: 8px;
  grid-template-columns: minmax(0, 1fr) auto auto;
}

.order-items span {
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.order-items em {
  color: #7b837e;
  font-style: normal;
}

.order-items b,
.order-total strong {
  color: #103f34;
}

.order-total span {
  color: #7a827d;
  font-size: 13px;
  font-weight: 800;
}

.order-total strong {
  font-size: 22px;
}

.order-actions {
  display: grid;
}
</style>
