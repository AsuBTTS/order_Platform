<template>
  <section>
    <header class="top-bar">
      <div>
        <p class="eyebrow">Orders</p>
        <h2 class="title">我的订单</h2>
      </div>
      <RouterLink class="ghost-btn" to="/dishes">继续点单</RouterLink>
    </header>

    <p v-if="error" class="danger-text">{{ error }}</p>
    <div v-if="loading" class="loading">正在加载订单...</div>

    <div v-else-if="orders.length === 0" class="empty-state card">
      <strong>还没有订单</strong>
      <p class="muted">从菜单添加商品后提交订单。</p>
      <RouterLink class="primary-btn" to="/dishes">去点单</RouterLink>
    </div>

    <div v-else class="order-list">
      <RouterLink v-for="order in orders" :key="order.id" class="card order-card" :to="`/orders/${order.id}`">
        <div class="order-head">
          <strong>{{ order.order_no }}</strong>
          <span class="status-pill">{{ statusText(order.status) }}</span>
        </div>
        <p>{{ order.merchant_store_name || order.merchant_username }} · {{ deliveryText(order.delivery_type) }}</p>
        <div class="order-items">
          <div v-for="item in order.items" :key="item.id">
            <span>
              <strong>{{ item.dish_name }}</strong>
              <em v-if="item.customization_label">{{ item.customization_label }}</em>
            </span>
            <i>x{{ item.quantity }}</i>
            <b>{{ money(item.subtotal) }}</b>
          </div>
        </div>
        <div class="order-foot">
          <span>{{ new Date(order.created_at).toLocaleString() }}</span>
          <b>{{ money(order.total_amount) }}</b>
        </div>
      </RouterLink>
    </div>
  </section>
</template>

<script setup>
import { onMounted, ref } from "vue";
import { useRouter } from "vue-router";

import { fetchOrders } from "../api/customer";
import { deliveryText, money, statusText } from "../utils/format";
import { getCustomerId } from "../utils/session";

const router = useRouter();
const orders = ref([]);
const loading = ref(true);
const error = ref("");

async function loadOrders() {
  const userId = getCustomerId();
  if (!userId) {
    router.push("/login");
    return;
  }

  loading.value = true;
  error.value = "";
  try {
    const { data } = await fetchOrders(userId);
    orders.value = data.orders;
  } catch (err) {
    error.value = err.message;
  } finally {
    loading.value = false;
  }
}

onMounted(loadOrders);
</script>

<style scoped>
.order-list {
  display: grid;
  gap: 12px;
}

.order-card {
  color: inherit;
  display: grid;
  gap: 10px;
  padding: 16px;
  text-decoration: none;
}

.order-head,
.order-foot {
  align-items: center;
  display: flex;
  justify-content: space-between;
}

.order-card p {
  color: #717c75;
  margin: 0;
}

.order-items {
  background: #fbf7ee;
  border: 1px solid #efe4d4;
  border-radius: 16px;
  display: grid;
  gap: 8px;
  padding: 10px 12px;
}

.order-items div {
  align-items: center;
  display: grid;
  gap: 8px;
  grid-template-columns: 1fr auto auto;
}

.order-items span {
  display: grid;
  gap: 3px;
  min-width: 0;
}

.order-items strong {
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.order-items em {
  color: #0e7a55;
  font-size: 12px;
  font-style: normal;
  font-weight: 900;
}

.order-items i {
  color: #7b837e;
  font-style: normal;
}

.order-items b {
  color: #103f34;
}

.order-foot span {
  color: #9aa19d;
  font-size: 12px;
}

.order-foot b {
  color: #103f34;
  font-size: 20px;
}
</style>
