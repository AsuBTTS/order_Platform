<template>
  <section class="merchant-view">
    <header class="top-bar">
      <div>
        <p class="eyebrow">Order Desk</p>
        <h2 class="title">商家接单</h2>
      </div>
      <button class="ghost-btn" @click="loadOrders">刷新</button>
    </header>

    <div class="desk-summary card">
      <div>
        <span>待接单</span>
        <strong>{{ paidCount }}</strong>
      </div>
      <div>
        <span>制作中</span>
        <strong>{{ preparingCount }}</strong>
      </div>
    </div>

    <p v-if="error" class="danger-text">{{ error }}</p>
    <p v-if="message" class="success-text">{{ message }}</p>
    <div v-if="loading" class="loading">正在加载商家订单...</div>

    <div v-else-if="orders.length === 0" class="empty-state card">
      <strong>暂无可处理订单</strong>
      <p class="muted">顾客支付成功后，订单会出现在这里。</p>
    </div>

    <div v-else class="merchant-list">
      <article v-for="order in orders" :key="order.id" class="card merchant-order">
        <div class="order-head">
          <div>
            <strong>{{ order.order_no }}</strong>
            <p>{{ deliveryText(order.delivery_type) }} · {{ order.customer_username }}</p>
          </div>
          <span class="status-pill">{{ statusText(order.status) }}</span>
        </div>

        <div class="order-items">
          <div v-for="item in order.items" :key="item.id" class="order-item-row">
            <span>
              <strong>{{ item.dish_name }}</strong>
              <em v-if="item.customization_label">{{ item.customization_label }}</em>
            </span>
            <i>x{{ item.quantity }}</i>
            <b>{{ money(item.subtotal) }}</b>
          </div>
        </div>

        <div class="order-total">
          <span>订单金额</span>
          <strong>{{ money(order.total_amount) }}</strong>
        </div>

        <div class="order-actions">
          <button
            v-if="order.status === 'paid'"
            class="primary-btn"
            :disabled="operatingId === order.id"
            @click="acceptOrder(order)"
          >
            {{ operatingId === order.id ? "处理中..." : "接单" }}
          </button>
          <button
            v-if="order.status === 'preparing'"
            class="primary-btn"
            :disabled="operatingId === order.id"
            @click="finishOrder(order)"
          >
            {{ operatingId === order.id ? "处理中..." : "完成制作" }}
          </button>
          <span v-if="!['paid', 'preparing'].includes(order.status)" class="muted">
            当前状态无需商家操作
          </span>
        </div>
      </article>
    </div>
  </section>
</template>

<script setup>
import { computed, onMounted, ref } from "vue";

import { acceptMerchantOrder, fetchMerchantOrders, finishMerchantOrder } from "../api/merchant";
import { deliveryText, money, statusText } from "../utils/format";
import { getMerchantId } from "../utils/session";

const orders = ref([]);
const loading = ref(true);
const operatingId = ref(null);
const error = ref("");
const message = ref("");

const paidCount = computed(() => orders.value.filter((order) => order.status === "paid").length);
const preparingCount = computed(() => orders.value.filter((order) => order.status === "preparing").length);

async function loadOrders() {
  loading.value = true;
  error.value = "";
  message.value = "";

  try {
    const { data } = await fetchMerchantOrders(getMerchantId());
    orders.value = data.orders;
  } catch (err) {
    error.value = err.message;
  } finally {
    loading.value = false;
  }
}

async function acceptOrder(order) {
  operatingId.value = order.id;
  error.value = "";
  message.value = "";
  try {
    await acceptMerchantOrder(getMerchantId(), order.id);
    message.value = "已接单，订单进入制作中。";
    await loadOrders();
  } catch (err) {
    error.value = err.message;
  } finally {
    operatingId.value = null;
  }
}

async function finishOrder(order) {
  operatingId.value = order.id;
  error.value = "";
  message.value = "";
  try {
    await finishMerchantOrder(getMerchantId(), order.id);
    message.value = order.delivery_type === "delivery" ? "制作完成，订单进入待配送。" : "制作完成，订单进入待取餐。";
    await loadOrders();
  } catch (err) {
    error.value = err.message;
  } finally {
    operatingId.value = null;
  }
}

onMounted(loadOrders);
</script>

<style scoped>
.merchant-view {
  display: grid;
  gap: 14px;
}

.desk-summary {
  background:
    linear-gradient(135deg, rgba(223, 242, 234, 0.92), rgba(255, 255, 255, 0.96)),
    radial-gradient(circle at 12% 12%, rgba(197, 161, 90, 0.22), transparent 32%);
  display: grid;
  gap: 12px;
  grid-template-columns: repeat(2, 1fr);
  padding: 14px;
}

.desk-summary div {
  background: rgba(255, 255, 255, 0.74);
  border: 1px solid #d6eee4;
  border-radius: 18px;
  display: grid;
  gap: 6px;
  padding: 14px;
}

.desk-summary span {
  color: #0e7a55;
  font-size: 13px;
  font-weight: 900;
}

.desk-summary strong {
  color: #103f34;
  font-size: 32px;
}

.merchant-list {
  display: grid;
  gap: 14px;
}

.merchant-order {
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
  font-size: 18px;
}

.order-head p {
  color: #7a827d;
  margin: 5px 0 0;
}

.order-items {
  background: #fbf7ee;
  border: 1px solid #efe4d4;
  border-radius: 16px;
  display: grid;
  gap: 9px;
  padding: 12px;
}

.order-item-row {
  align-items: center;
  display: grid;
  gap: 8px;
  grid-template-columns: minmax(0, 1fr) auto auto;
}

.order-item-row span {
  display: grid;
  gap: 3px;
  min-width: 0;
}

.order-item-row span strong {
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.order-item-row em {
  color: #0e7a55;
  font-size: 12px;
  font-style: normal;
  font-weight: 900;
}

.order-item-row i {
  color: #7b837e;
  font-style: normal;
}

.order-item-row b,
.order-total strong {
  color: #103f34;
}

.order-total span {
  color: #7a827d;
  font-weight: 800;
}

.order-total strong {
  font-size: 22px;
}

.order-actions {
  display: grid;
}
</style>
