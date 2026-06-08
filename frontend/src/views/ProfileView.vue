<template>
  <section class="profile-view">
    <div class="profile-card">
      <div class="profile-top">
        <img src="/logo.png" alt="花神咖啡馆" />
        <div>
          <strong>{{ user?.username }}</strong>
          <span>花神顾客 · {{ roleText(user?.role) }}</span>
        </div>
        <b>0.6 ★</b>
      </div>
      <div class="profile-meta">
        <span>
          手机号
          <strong>{{ user?.phone || "未填写" }}</strong>
        </span>
        <span>
          可用券
          <strong>{{ availableCoupons.length }} 张</strong>
        </span>
      </div>
    </div>

    <section class="card coupon-section">
      <div class="section-head">
        <h2>我的优惠券</h2>
        <button class="ghost-btn" @click="loadCoupons">刷新</button>
      </div>
      <nav class="coupon-tabs" aria-label="优惠券分类">
        <button v-for="tab in couponTabs" :key="tab.key" :class="{ active: couponTab === tab.key }" @click="couponTab = tab.key">
          {{ tab.label }}
        </button>
      </nav>
      <p v-if="couponError" class="danger-text">{{ couponError }}</p>
      <div v-if="visibleCoupons.length === 0" class="coupon-empty">
        {{ couponTab === "available" ? "暂无可用优惠券" : "暂无此类优惠券" }}
      </div>
      <article v-for="coupon in visibleCoupons" :key="coupon.id" class="coupon-ticket" :class="{ disabled: !coupon.is_available }">
        <div class="ticket-value">
          <strong>{{ money(coupon.discount_amount) }}</strong>
          <span>抵扣券</span>
        </div>
        <div class="ticket-main">
          <strong>{{ coupon.title }}</strong>
          <span>{{ coupon.code }} · {{ coupon.valid_until || "长期有效" }}</span>
          <em>{{ couponStateText(coupon) }}</em>
        </div>
      </article>
    </section>

    <section class="profile-menu">
      <RouterLink to="/profile/edit">修改用户信息</RouterLink>
      <RouterLink to="/profile/password">修改密码</RouterLink>
      <RouterLink to="/dishes">继续点单</RouterLink>
      <RouterLink to="/cart">查看购物车并用券</RouterLink>
      <RouterLink to="/orders">我的订单</RouterLink>
      <RouterLink to="/orders">已完成订单评价</RouterLink>
      <button class="logout-text" @click="logout">退出登录</button>
    </section>
  </section>
</template>

<script setup>
import { computed, onMounted, ref } from "vue";
import { useRouter } from "vue-router";

import { fetchUserCoupons } from "../api/customer";
import { money, roleText } from "../utils/format";
import { clearStoredUser, getCustomerId, getStoredUser } from "../utils/session";

const router = useRouter();
const user = ref(getStoredUser());
const coupons = ref([]);
const couponTab = ref("available");
const couponError = ref("");

const availableCoupons = computed(() => coupons.value.filter((coupon) => coupon.is_available));
const usedCoupons = computed(() => coupons.value.filter((coupon) => coupon.used_at));
const unavailableCoupons = computed(() => coupons.value.filter((coupon) => !coupon.is_available && !coupon.used_at));
const couponTabs = computed(() => [
  { key: "available", label: `可用 ${availableCoupons.value.length}` },
  { key: "used", label: `已用 ${usedCoupons.value.length}` },
  { key: "unavailable", label: `失效 ${unavailableCoupons.value.length}` },
]);
const visibleCoupons = computed(() => {
  if (couponTab.value === "used") return usedCoupons.value;
  if (couponTab.value === "unavailable") return unavailableCoupons.value;
  return availableCoupons.value;
});

function couponStateText(coupon) {
  if (coupon.is_available) return "可在购物车提交订单时使用";
  if (coupon.used_at) return "已使用";
  return "已失效";
}

async function loadCoupons() {
  couponError.value = "";
  try {
    const { data } = await fetchUserCoupons(getCustomerId());
    coupons.value = data.coupons;
  } catch (err) {
    couponError.value = err.message;
  }
}

function logout() {
  clearStoredUser();
  router.push("/login");
}

onMounted(loadCoupons);
</script>

<style scoped>
.profile-view {
  display: grid;
  gap: 16px;
}

.profile-card {
  background:
    linear-gradient(135deg, rgba(255, 255, 255, 0.76), rgba(201, 220, 229, 0.78)),
    url("/hero.png") center / cover;
  border-radius: 30px;
  box-shadow: 0 16px 38px rgba(24, 34, 29, 0.1);
  display: grid;
  gap: 26px;
  min-height: 238px;
  padding: 20px;
}

.profile-top {
  align-items: center;
  display: grid;
  gap: 12px;
  grid-template-columns: 62px 1fr auto;
}

.profile-top img {
  border: 2px solid rgba(255, 255, 255, 0.72);
  border-radius: 999px;
  height: 62px;
  object-fit: cover;
  width: 62px;
}

.profile-top div,
.profile-meta span,
.ticket-main {
  display: grid;
  gap: 6px;
}

.profile-top strong {
  font-size: 22px;
}

.profile-top span {
  color: #4b5a54;
  font-weight: 800;
}

.profile-top b {
  color: #1c2c25;
  font-size: 28px;
}

.profile-meta {
  display: grid;
  gap: 12px;
  grid-template-columns: repeat(2, 1fr);
}

.profile-meta span {
  background: rgba(255, 255, 255, 0.72);
  border-radius: 18px;
  color: #5d6963;
  padding: 12px;
}

.profile-meta strong {
  color: #1c2c25;
  font-size: 22px;
}

.coupon-section {
  display: grid;
  gap: 14px;
  padding: 16px;
}

.section-head {
  align-items: center;
  display: flex;
  justify-content: space-between;
}

.section-head h2 {
  font-family: Georgia, "Times New Roman", "Songti SC", serif;
  margin: 0;
}

.coupon-tabs {
  background: #f8f4ee;
  border-radius: 16px;
  display: grid;
  gap: 5px;
  grid-template-columns: repeat(3, 1fr);
  padding: 5px;
}

.coupon-tabs button {
  background: transparent;
  border-radius: 12px;
  color: #68736d;
  font-size: 13px;
  font-weight: 900;
  min-height: 38px;
}

.coupon-tabs button.active {
  background: #dff2ea;
  color: #0e7a55;
}

.coupon-empty {
  color: #7a827d;
  font-weight: 800;
  padding: 10px 0;
}

.coupon-ticket {
  background: linear-gradient(90deg, #103f34 0 30%, #ffffff 30% 100%);
  border: 1px solid #e8ded0;
  border-radius: 18px;
  display: grid;
  grid-template-columns: 30% 1fr;
  min-height: 112px;
  overflow: hidden;
}

.coupon-ticket.disabled {
  filter: grayscale(0.8);
  opacity: 0.64;
}

.ticket-value {
  align-content: center;
  color: #ffffff;
  display: grid;
  justify-items: center;
  padding: 12px 6px;
}

.ticket-value strong {
  font-size: 22px;
}

.ticket-value span,
.ticket-main em {
  font-size: 12px;
  font-weight: 900;
}

.ticket-main {
  align-content: center;
  min-width: 0;
  padding: 14px;
}

.ticket-main strong,
.ticket-main span,
.ticket-main em {
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.ticket-main strong {
  color: #103f34;
  font-size: 18px;
}

.ticket-main span {
  color: #6d766f;
  font-size: 13px;
  font-weight: 800;
}

.ticket-main em {
  color: #0e7a55;
  font-style: normal;
}

.profile-menu {
  background: #ffffff;
  border-radius: 24px;
  overflow: hidden;
}

.profile-menu a,
.profile-menu button {
  align-items: center;
  background: #ffffff;
  border-bottom: 1px solid #f0ebe4;
  color: #1f2924;
  display: flex;
  font-size: 17px;
  font-weight: 800;
  justify-content: space-between;
  min-height: 58px;
  padding: 0 18px;
  text-align: left;
  text-decoration: none;
  width: 100%;
}

.profile-menu a::after,
.profile-menu button::after {
  color: #a0a8a3;
  content: ">";
  font-size: 22px;
}
</style>
