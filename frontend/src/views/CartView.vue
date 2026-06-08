<template>
  <section>
    <header class="top-bar">
      <div>
        <p class="eyebrow">Cart</p>
        <h2 class="title">购物车</h2>
      </div>
      <RouterLink class="ghost-btn" to="/dishes">继续点单</RouterLink>
    </header>

    <p v-if="error" class="danger-text">{{ error }}</p>
    <div v-if="loading" class="loading">正在加载购物车...</div>

    <div v-else-if="items.length === 0" class="empty-state card">
      <strong>购物车还是空的</strong>
      <p class="muted">去菜单里加一杯喜欢的饮品。</p>
      <RouterLink class="primary-btn" to="/dishes">去点单</RouterLink>
    </div>

    <div v-else class="cart-list">
      <section class="card store-card">
        <span>下单门店</span>
        <strong>{{ cartStoreName }}</strong>
        <em>{{ cartStoreAddress }}</em>
        <RouterLink to="/dishes">切换门店或继续点单</RouterLink>
      </section>

      <article v-for="item in items" :key="item.id" class="card cart-item">
        <div class="item-art small-art">
          <span>{{ item.dish.name.slice(0, 1) }}</span>
        </div>
        <div class="cart-info">
          <strong>{{ item.dish.name }}</strong>
          <span>{{ money(item.unit_price || item.dish.price) }}</span>
          <em v-if="item.customization_label">{{ item.customization_label }}</em>
          <div class="cart-actions">
            <button @click="changeQuantity(item, item.quantity - 1)">-</button>
            <b>{{ item.quantity }}</b>
            <button @click="changeQuantity(item, item.quantity + 1)">+</button>
            <button class="delete-btn" @click="removeItem(item)">删除</button>
          </div>
        </div>
        <strong class="line-total">{{ money(item.subtotal) }}</strong>
      </article>

      <div class="card delivery-card">
        <span>取餐方式</span>
        <strong>{{ deliveryType === "delivery" ? "外送" : "到店自取" }}</strong>
        <RouterLink to="/dishes">在点单页顶部修改</RouterLink>
        <div v-if="deliveryType === 'delivery'" class="field address-field">
          <label for="address">收货地址</label>
          <input id="address" v-model="address" placeholder="请输入收货地址" />
        </div>
      </div>

      <section class="card coupon-picker">
        <div class="coupon-head">
          <div>
            <span>优惠券</span>
            <strong>{{ selectedCoupon ? selectedCoupon.title : "未使用优惠券" }}</strong>
          </div>
          <button class="ghost-btn" @click="loadCoupons">刷新</button>
        </div>

        <label class="coupon-option" :class="{ active: selectedCouponId === '' }">
          <input v-model="selectedCouponId" value="" type="radio" />
          <span>
            <strong>不使用优惠券</strong>
            <em>保留优惠券到下次使用</em>
          </span>
        </label>

        <label
          v-for="coupon in usableCoupons"
          :key="coupon.id"
          class="coupon-option"
          :class="{ active: Number(selectedCouponId) === coupon.id }"
        >
          <input v-model="selectedCouponId" :value="String(coupon.id)" type="radio" />
          <span>
            <strong>{{ coupon.title }}</strong>
            <em>{{ coupon.code }} · 抵扣 {{ money(coupon.discount_amount) }}</em>
          </span>
          <b>-{{ money(coupon.discount_amount) }}</b>
        </label>

        <p v-if="usableCoupons.length === 0" class="muted">暂无可用优惠券。</p>
      </section>
    </div>

    <div v-if="items.length > 0" class="cart-checkout">
      <div class="checkout-total">
        <span><em>小计</em><strong>{{ money(totalAmount) }}</strong></span>
        <span v-if="discountAmount > 0"><em>优惠</em><strong>-{{ money(discountAmount) }}</strong></span>
        <span><em>实付</em><strong>{{ money(payableAmount) }}</strong></span>
      </div>
      <button class="primary-btn" :disabled="submitting" @click="submitOrder">
        {{ submitting ? "提交中..." : "提交订单" }}
      </button>
    </div>
  </section>
</template>

<script setup>
import { computed, onMounted, ref } from "vue";
import { useRouter } from "vue-router";

import { createOrder, deleteCartItem, fetchCart, fetchUserCoupons, updateCartItem } from "../api/customer";
import { money } from "../utils/format";
import { getCustomerId, getFulfillmentType, getSelectedStore, setSelectedStore } from "../utils/session";

const router = useRouter();
const items = ref([]);
const coupons = ref([]);
const selectedStore = ref(getSelectedStore());
const totalAmount = ref(0);
const deliveryType = ref(getFulfillmentType());
const selectedCouponId = ref("");
const address = ref("");
const loading = ref(true);
const submitting = ref(false);
const error = ref("");

const cartMerchantId = computed(() => items.value[0]?.dish?.merchant || selectedStore.value?.id || null);
const cartStoreName = computed(() => items.value[0]?.dish?.merchant_store_name || selectedStore.value?.store_name || "当前门店");
const cartStoreAddress = computed(() => items.value[0]?.dish?.merchant_store_address || selectedStore.value?.store_address || "");
const usableCoupons = computed(() => coupons.value.filter((coupon) => coupon.is_available));
const selectedCoupon = computed(() => usableCoupons.value.find((coupon) => coupon.id === Number(selectedCouponId.value)));
const discountAmount = computed(() => {
  if (!selectedCoupon.value) {
    return 0;
  }
  return Math.min(Number(selectedCoupon.value.discount_amount || 0), Number(totalAmount.value || 0));
});
const payableAmount = computed(() => Math.max(Number(totalAmount.value || 0) - discountAmount.value, 0));

async function loadCart() {
  loading.value = true;
  error.value = "";
  deliveryType.value = getFulfillmentType();
  selectedStore.value = getSelectedStore();

  try {
    const [{ data: cartData }] = await Promise.all([fetchCart(getCustomerId()), loadCoupons()]);
    items.value = cartData.items;
    totalAmount.value = cartData.total_amount;
    if (items.value[0] && (!selectedStore.value || selectedStore.value.id !== items.value[0].dish.merchant)) {
      selectedStore.value = {
        id: items.value[0].dish.merchant,
        store_name: items.value[0].dish.merchant_store_name,
        store_address: items.value[0].dish.merchant_store_address,
      };
      setSelectedStore(selectedStore.value);
    }
  } catch (err) {
    error.value = err.message;
  } finally {
    loading.value = false;
  }
}

async function loadCoupons() {
  const { data } = await fetchUserCoupons(getCustomerId());
  coupons.value = data.coupons;
  if (selectedCouponId.value && !data.coupons.some((coupon) => coupon.id === Number(selectedCouponId.value) && coupon.is_available)) {
    selectedCouponId.value = "";
  }
  return data;
}

async function changeQuantity(item, quantity) {
  try {
    if (quantity <= 0) {
      await deleteCartItem(getCustomerId(), item.id);
    } else {
      await updateCartItem(getCustomerId(), item.id, quantity);
    }
    await loadCart();
  } catch (err) {
    error.value = err.message;
  }
}

async function removeItem(item) {
  try {
    await deleteCartItem(getCustomerId(), item.id);
    await loadCart();
  } catch (err) {
    error.value = err.message;
  }
}

async function submitOrder() {
  if (deliveryType.value === "delivery" && !address.value.trim()) {
    error.value = "外送订单请先填写收货地址。";
    return;
  }

  submitting.value = true;
  error.value = "";

  try {
    const couponId = selectedCoupon.value ? selectedCoupon.value.id : null;
    const { data } = await createOrder(getCustomerId(), deliveryType.value, couponId, cartMerchantId.value);
    router.push(`/payment/${data.order.id}`);
  } catch (err) {
    error.value = err.message;
  } finally {
    submitting.value = false;
  }
}

onMounted(loadCart);
</script>

<style scoped>
.cart-list {
  display: grid;
  gap: 12px;
  padding-bottom: 136px;
}

.store-card,
.delivery-card,
.coupon-picker {
  display: grid;
  gap: 10px;
  padding: 14px;
}

.store-card span,
.delivery-card > span,
.coupon-head span {
  color: #6d766f;
  font-weight: 900;
}

.store-card strong,
.delivery-card strong,
.coupon-picker strong {
  color: #103f34;
}

.store-card em {
  color: #778079;
  font-size: 13px;
  font-style: normal;
  font-weight: 800;
  line-height: 1.4;
}

.store-card a,
.delivery-card a {
  color: #0e7a55;
  font-weight: 900;
  text-decoration: none;
}

.cart-item {
  align-items: center;
  display: grid;
  gap: 12px;
  grid-template-columns: 78px minmax(0, 1fr) auto;
  padding: 12px;
}

.small-art {
  border-radius: 18px;
  height: 78px;
  width: 78px;
}

.cart-info {
  display: grid;
  gap: 5px;
  min-width: 0;
}

.cart-info strong {
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.cart-info span {
  color: #778079;
  font-size: 13px;
}

.cart-info em {
  color: #0e7a55;
  font-size: 12px;
  font-style: normal;
  font-weight: 900;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.cart-actions {
  align-items: center;
  display: flex;
  gap: 10px;
}

.cart-actions button {
  background: #edf7f2;
  border-radius: 999px;
  color: #0e7a55;
  font-weight: 900;
  height: 30px;
  min-width: 30px;
}

.cart-actions .delete-btn {
  background: #fff1ec;
  color: #b42318;
  font-size: 12px;
  padding: 0 10px;
}

.line-total {
  color: #103f34;
}

.delivery-card strong {
  font-size: 20px;
}

.address-field {
  margin: 6px 0 0;
}

.coupon-head {
  align-items: center;
  display: flex;
  justify-content: space-between;
}

.coupon-head div {
  display: grid;
  gap: 4px;
}

.coupon-option {
  align-items: center;
  background: #f8f4ee;
  border: 1px solid transparent;
  border-radius: 16px;
  display: grid;
  gap: 10px;
  grid-template-columns: auto minmax(0, 1fr) auto;
  padding: 12px;
}

.coupon-option.active {
  background: #edf7f2;
  border-color: #9ed7bd;
}

.coupon-option input {
  accent-color: #0e7a55;
}

.coupon-option span {
  display: grid;
  gap: 4px;
  min-width: 0;
}

.coupon-option em {
  color: #748079;
  font-size: 12px;
  font-style: normal;
  font-weight: 800;
}

.coupon-option b {
  color: #0e7a55;
}

.cart-checkout {
  align-items: center;
  background: #ffffff;
  border-top: 1px solid #ece5dc;
  bottom: 82px;
  display: flex;
  gap: 12px;
  justify-content: space-between;
  left: 0;
  padding: 12px 18px;
  position: absolute;
  right: 0;
  z-index: 17;
}

.checkout-total {
  display: grid;
  gap: 2px;
}

.checkout-total span {
  align-items: baseline;
  display: flex;
  gap: 8px;
}

.checkout-total em {
  color: #828b86;
  font-size: 12px;
  font-style: normal;
  min-width: 28px;
}

.checkout-total strong {
  color: #103f34;
  font-size: 16px;
}

.checkout-total span:last-child strong {
  font-size: 22px;
}
</style>
