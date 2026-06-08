<template>
  <section>
    <RouterLink class="back-link" :to="`/orders/${route.params.orderId}`">返回订单</RouterLink>

    <div class="payment-hero">
      <p class="eyebrow">Payment</p>
      <h2 class="title">模拟支付</h2>
      <p class="muted">MVP 阶段不接入真实支付，可模拟成功或失败。</p>
    </div>

    <p v-if="error" class="danger-text">{{ error }}</p>
    <p v-if="message" class="success-text">{{ message }}</p>

    <div v-if="loading" class="loading">正在加载订单...</div>

    <div v-else-if="order" class="card pay-card">
      <div class="pay-total">
        <span>应付金额</span>
        <strong>{{ money(order.total_amount) }}</strong>
      </div>

      <div class="bill-lines">
        <div>
          <span>商品小计</span>
          <b>{{ money(order.subtotal_amount || order.total_amount) }}</b>
        </div>
        <div v-if="Number(order.discount_amount || 0) > 0">
          <span>优惠券抵扣</span>
          <b>-{{ money(order.discount_amount) }}</b>
        </div>
      </div>

      <div class="field">
        <label for="paymentType">支付方式</label>
        <select id="paymentType" v-model="paymentType">
          <option value="mock_wechat">模拟微信支付</option>
          <option value="mock_alipay">模拟支付宝支付</option>
          <option value="mock_balance">模拟余额支付</option>
        </select>
      </div>

      <button class="primary-btn pay-btn" :disabled="submitting || order.status !== 'pending_payment'" @click="handlePaySuccess">
        {{ submitting ? "支付中..." : "确认模拟支付" }}
      </button>
      <button class="secondary-btn pay-btn" :disabled="submitting || order.status !== 'pending_payment'" @click="handlePayFail">
        模拟支付失败
      </button>

      <RouterLink v-if="order.status !== 'pending_payment'" class="secondary-btn pay-btn" :to="`/orders/${order.id}`">
        查看订单
      </RouterLink>
    </div>
  </section>
</template>

<script setup>
import { onMounted, ref } from "vue";
import { useRoute, useRouter } from "vue-router";

import { createPayment, fetchOrder, payFail, paySuccess } from "../api/customer";
import { money } from "../utils/format";
import { getCustomerId } from "../utils/session";

const route = useRoute();
const router = useRouter();
const order = ref(null);
const paymentType = ref("mock_wechat");
const loading = ref(true);
const submitting = ref(false);
const error = ref("");
const message = ref("");

async function loadOrder() {
  loading.value = true;
  error.value = "";
  try {
    const { data } = await fetchOrder(getCustomerId(), route.params.orderId);
    order.value = data.order;
  } catch (err) {
    error.value = err.message;
  } finally {
    loading.value = false;
  }
}

async function createPendingPayment() {
  const { data } = await createPayment(getCustomerId(), order.value.id, paymentType.value);
  return data.payment;
}

async function handlePaySuccess() {
  submitting.value = true;
  error.value = "";
  message.value = "";
  try {
    const payment = await createPendingPayment();
    await paySuccess(getCustomerId(), payment.id);
    router.push(`/orders/${order.value.id}`);
  } catch (err) {
    error.value = err.message;
  } finally {
    submitting.value = false;
  }
}

async function handlePayFail() {
  submitting.value = true;
  error.value = "";
  message.value = "";
  try {
    const payment = await createPendingPayment();
    await payFail(getCustomerId(), payment.id);
    message.value = "模拟支付失败，订单仍为待支付，可重新支付。";
  } catch (err) {
    error.value = err.message;
  } finally {
    submitting.value = false;
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

.payment-hero {
  background: linear-gradient(150deg, #103f34 0%, #176a50 58%, #eacfa8 59%, #f6e4c8 100%);
  border-radius: 28px;
  color: #ffffff;
  margin-bottom: 16px;
  min-height: 210px;
  padding: 22px;
}

.payment-hero .eyebrow,
.payment-hero .muted {
  color: rgba(255, 255, 255, 0.86);
}

.pay-card {
  display: grid;
  gap: 18px;
  padding: 18px;
}

.pay-total {
  display: grid;
  gap: 6px;
}

.pay-total span {
  color: #7b837e;
  font-weight: 800;
}

.pay-total strong {
  color: #103f34;
  font-size: 34px;
}

.bill-lines {
  background: #f7f1e8;
  border-radius: 16px;
  display: grid;
  gap: 8px;
  padding: 12px;
}

.bill-lines div {
  display: flex;
  justify-content: space-between;
}

.bill-lines span {
  color: #6d766f;
  font-weight: 800;
}

.bill-lines b {
  color: #103f34;
}

.pay-btn {
  width: 100%;
}
</style>
