<template>
  <section>
    <RouterLink class="back-link" to="/orders">返回订单</RouterLink>

    <p v-if="error" class="danger-text">{{ error }}</p>
    <div v-if="loading" class="loading">正在加载订单详情...</div>

    <article v-else-if="order" class="order-detail">
      <div class="card summary-card">
        <span class="status-pill">{{ statusText(order.status) }}</span>
        <h2>{{ statusTitle }}</h2>
        <p class="muted">{{ order.merchant_store_name || order.merchant_username }} · {{ deliveryText(order.delivery_type) }}</p>
        <p class="muted">{{ order.order_no }}</p>
      </div>

      <div class="card">
        <div v-for="item in order.items" :key="item.id" class="detail-item">
          <div class="item-art tiny-art">
            <span>{{ item.dish_name.slice(0, 1) }}</span>
          </div>
          <div>
            <strong>{{ item.dish_name }}</strong>
            <em v-if="item.customization_label">{{ item.customization_label }}</em>
            <p>{{ money(item.dish_price) }} x {{ item.quantity }}</p>
          </div>
          <b>{{ money(item.subtotal) }}</b>
        </div>
      </div>

      <div class="card total-card">
        <div>
          <span>商品小计</span>
          <b>{{ money(order.subtotal_amount || order.total_amount) }}</b>
        </div>
        <div v-if="Number(order.discount_amount || 0) > 0">
          <span>优惠券抵扣</span>
          <b>-{{ money(order.discount_amount) }}</b>
        </div>
        <div class="payable-line">
          <span>订单金额</span>
          <strong>{{ money(order.total_amount) }}</strong>
        </div>
      </div>

      <div class="detail-actions">
        <RouterLink
          v-if="order.status === 'pending_payment'"
          class="primary-btn"
          :to="`/payment/${order.id}`"
        >
          去支付
        </RouterLink>
        <button
          v-if="order.status === 'waiting_pickup'"
          class="primary-btn"
          :disabled="submitting"
          @click="markComplete"
        >
          {{ submitting ? "确认中..." : "确认取餐" }}
        </button>
        <RouterLink class="secondary-btn" to="/orders">订单列表</RouterLink>
      </div>

      <form v-if="order.status === 'completed'" class="card review-card" @submit.prevent="sendReview">
        <h3>评价本次订单</h3>
        <div class="field">
          <label for="score">评分</label>
          <select id="score" v-model="review.score">
            <option :value="5">5 分 · 非常满意</option>
            <option :value="4">4 分 · 满意</option>
            <option :value="3">3 分 · 一般</option>
            <option :value="2">2 分 · 不太满意</option>
            <option :value="1">1 分 · 不满意</option>
          </select>
        </div>
        <div class="field">
          <label for="content">文字评价</label>
          <textarea id="content" v-model="review.content" placeholder="写下本次点餐体验"></textarea>
        </div>
        <button class="primary-btn" :disabled="reviewing" type="submit">
          {{ reviewing ? "提交中..." : "提交评价" }}
        </button>
        <p v-if="reviewMessage" class="success-text">{{ reviewMessage }}</p>
      </form>
    </article>
  </section>
</template>

<script setup>
import { computed, onMounted, reactive, ref } from "vue";
import { useRoute } from "vue-router";

import { completeOrder, fetchOrder, submitReview } from "../api/customer";
import { deliveryText, money, statusText } from "../utils/format";
import { getCustomerId } from "../utils/session";

const route = useRoute();
const order = ref(null);
const loading = ref(true);
const submitting = ref(false);
const reviewing = ref(false);
const error = ref("");
const reviewMessage = ref("");
const review = reactive({
  score: 5,
  content: "",
});

const statusTitle = computed(() => {
  if (!order.value) {
    return "";
  }
  const map = {
    pending_payment: "订单已创建，等待支付",
    paid: "支付成功，等待商家接单",
    preparing: "商家正在制作",
    waiting_pickup: "餐品已备好，可到店取餐",
    waiting_delivery: "等待配送员取餐",
    delivering: "配送中",
    completed: "订单已完成",
    cancelled: "订单已取消",
  };
  return map[order.value.status] || "订单状态";
});

async function loadOrder() {
  loading.value = true;
  error.value = "";
  try {
    const { data } = await fetchOrder(getCustomerId(), route.params.id);
    order.value = data.order;
  } catch (err) {
    error.value = err.message;
  } finally {
    loading.value = false;
  }
}

async function markComplete() {
  submitting.value = true;
  error.value = "";
  try {
    await completeOrder(getCustomerId(), order.value.id);
    await loadOrder();
  } catch (err) {
    error.value = err.message;
  } finally {
    submitting.value = false;
  }
}

async function sendReview() {
  reviewing.value = true;
  error.value = "";
  reviewMessage.value = "";
  try {
    await submitReview(getCustomerId(), order.value.id, review.score, review.content);
    reviewMessage.value = "评价已提交，感谢反馈。";
  } catch (err) {
    error.value = err.message;
  } finally {
    reviewing.value = false;
  }
}

onMounted(loadOrder);
</script>

<style scoped>
.back-link {
  color: #52615a;
  display: inline-flex;
  font-weight: 800;
  margin-bottom: 16px;
  text-decoration: none;
}

.order-detail {
  display: grid;
  gap: 14px;
}

.summary-card {
  display: grid;
  gap: 8px;
  padding: 20px;
}

.summary-card h2 {
  font-size: 24px;
  margin: 0;
}

.detail-item {
  align-items: center;
  border-bottom: 1px solid #f1ebe3;
  display: grid;
  gap: 12px;
  grid-template-columns: 62px 1fr auto;
  padding: 14px;
}

.detail-item:last-child {
  border-bottom: 0;
}

.tiny-art {
  border-radius: 16px;
  height: 62px;
  width: 62px;
}

.detail-item div:nth-child(2) {
  display: grid;
  gap: 4px;
  min-width: 0;
}

.detail-item em {
  color: #0e7a55;
  font-size: 12px;
  font-style: normal;
  font-weight: 900;
}

.detail-item p {
  color: #7b837e;
  margin: 0;
}

.detail-item b,
.total-card strong {
  color: #103f34;
}

.total-card {
  display: grid;
  gap: 10px;
  padding: 16px;
}

.total-card div {
  display: flex;
  justify-content: space-between;
}

.total-card span {
  color: #7a827d;
  font-weight: 800;
}

.payable-line {
  border-top: 1px solid #f1ebe3;
  padding-top: 10px;
}

.detail-actions,
.review-card {
  display: grid;
  gap: 10px;
}

.review-card {
  padding: 16px;
}

.review-card h3 {
  font-family: Georgia, "Times New Roman", "Songti SC", serif;
  margin: 0;
}
</style>
