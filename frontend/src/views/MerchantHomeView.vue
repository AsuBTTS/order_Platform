<template>
  <section class="merchant-home">
    <header class="top-bar">
      <div>
        <p class="eyebrow">Café de Flore</p>
        <h2 class="title">商家工作台</h2>
      </div>
      <button class="ghost-btn logout-text" @click="logout">退出</button>
    </header>

    <div class="merchant-hero">
      <strong>{{ merchant?.store_name || merchant?.username }}</strong>
      <span>{{ merchant?.store_address || "请在平台端补充门店地址" }}</span>
    </div>

    <section class="card store-info">
      <span>门店管理账户</span>
      <strong>{{ merchant?.username }}</strong>
      <div class="coord-grid">
        <b>纬度 {{ merchant?.store_latitude || "未设置" }}</b>
        <b>经度 {{ merchant?.store_longitude || "未设置" }}</b>
      </div>
    </section>

    <div class="work-grid">
      <RouterLink class="work-card" to="/merchant/inventory">
        <span>进货</span>
        <strong>管理库存</strong>
        <em>查看餐品库存并补货</em>
      </RouterLink>
      <RouterLink class="work-card" to="/merchant/orders">
        <span>接单</span>
        <strong>处理订单</strong>
        <em>接单与完成制作</em>
      </RouterLink>
    </div>

    <section class="card note-card">
      <h3>今日提示</h3>
      <p>顾客选择门店后，只会浏览该门店商品。提交订单时后端会校验购物车商品与当前门店一致。</p>
    </section>
  </section>
</template>

<script setup>
import { onMounted, ref } from "vue";
import { useRouter } from "vue-router";

import { fetchMerchantProfile } from "../api/merchant";
import { clearStoredMerchant, getMerchantId, getStoredMerchant, updateStoredMerchant } from "../utils/session";

const router = useRouter();
const merchant = ref(getStoredMerchant());
const error = ref("");

async function refreshMerchantProfile() {
  error.value = "";
  try {
    const { data } = await fetchMerchantProfile(getMerchantId());
    merchant.value = updateStoredMerchant(data.user);
  } catch (err) {
    error.value = err.message;
  }
}

function logout() {
  clearStoredMerchant();
  router.push("/merchant/login");
}

onMounted(refreshMerchantProfile);
</script>

<style scoped>
.merchant-home {
  display: grid;
  gap: 16px;
}

.merchant-hero {
  align-content: end;
  background:
    linear-gradient(135deg, rgba(16, 63, 52, 0.94), rgba(16, 63, 52, 0.62)),
    url("/hero.png") center / cover;
  border-radius: 30px;
  color: #ffffff;
  display: grid;
  gap: 8px;
  min-height: 220px;
  padding: 24px;
}

.merchant-hero strong {
  font-family: Georgia, "Times New Roman", "Songti SC", serif;
  font-size: 31px;
  line-height: 1.12;
}

.merchant-hero span {
  color: rgba(255, 255, 255, 0.86);
  line-height: 1.5;
}

.store-info {
  background:
    linear-gradient(135deg, rgba(223, 242, 234, 0.9), rgba(255, 255, 255, 0.96)),
    radial-gradient(circle at 18% 14%, rgba(197, 161, 90, 0.22), transparent 32%);
  display: grid;
  gap: 10px;
  padding: 16px;
}

.store-info span {
  color: #6d766f;
  font-size: 13px;
  font-weight: 900;
}

.store-info strong {
  color: #103f34;
  font-size: 20px;
}

.coord-grid {
  display: grid;
  gap: 8px;
  grid-template-columns: repeat(2, 1fr);
}

.coord-grid b {
  background: rgba(255, 255, 255, 0.74);
  border: 1px solid #d6eee4;
  border-radius: 14px;
  color: #103f34;
  font-size: 12px;
  padding: 10px;
}

.work-grid {
  display: grid;
  gap: 12px;
  grid-template-columns: repeat(2, 1fr);
}

.work-card {
  background: #ffffff;
  border-radius: 24px;
  box-shadow: 0 10px 30px rgba(24, 34, 29, 0.08);
  color: #182923;
  display: grid;
  gap: 7px;
  min-height: 152px;
  padding: 18px;
  text-decoration: none;
}

.work-card span {
  color: #0e7a55;
  font-weight: 900;
}

.work-card strong {
  font-size: 22px;
}

.work-card em {
  color: #778079;
  font-style: normal;
  line-height: 1.4;
}

.note-card {
  padding: 16px;
}

.note-card h3 {
  font-family: Georgia, "Times New Roman", "Songti SC", serif;
  margin: 0 0 8px;
}

.note-card p {
  color: #66706a;
  line-height: 1.6;
  margin: 0;
}
</style>
