<template>
  <section class="platform-dashboard">
    <header class="top-bar">
      <div>
        <p class="eyebrow">Café de Flore</p>
        <h2 class="title">平台管理</h2>
      </div>
      <button class="ghost-btn logout-text" @click="logout">退出</button>
    </header>

    <section class="platform-hero">
      <div>
        <span>管理员</span>
        <strong>{{ admin?.username }}</strong>
      </div>
      <button class="secondary-btn" type="button" @click="refreshAll">刷新</button>
    </section>

    <nav class="platform-tabs" aria-label="平台功能">
      <button v-for="tab in tabs" :key="tab.key" :class="{ active: activeTab === tab.key }" @click="activeTab = tab.key">
        {{ tab.label }}
      </button>
    </nav>

    <p v-if="error" class="danger-text">{{ error }}</p>
    <p v-if="message" class="success-text">{{ message }}</p>
    <div v-if="loading" class="loading">正在加载平台数据...</div>

    <template v-else>
      <section v-if="activeTab === 'overview'" class="tab-panel">
        <section class="metric-grid">
          <article v-for="metric in metrics" :key="metric.label" class="card metric-card">
            <span>{{ metric.label }}</span>
            <strong>{{ metric.value }}</strong>
          </article>
        </section>
      </section>

      <section v-if="activeTab === 'users'" class="tab-panel">
        <section class="card filter-card">
          <input v-model="userFilters.q" placeholder="搜索用户名" @keyup.enter="loadUsers" />
          <select v-model="userFilters.role" @change="loadUsers">
            <option value="">全部角色</option>
            <option value="customer">顾客</option>
            <option value="merchant">商家</option>
            <option value="driver">骑手</option>
          </select>
          <button class="primary-btn" @click="loadUsers">搜索</button>
        </section>

        <article v-for="item in visibleUsers" :key="item.id" class="card user-card">
          <div class="list-main">
            <strong>{{ item.username }}</strong>
            <span>{{ roleText(item.role) }} · {{ item.phone || "未填写手机号" }}</span>
            <span v-if="item.role === 'merchant'">{{ item.store_name || "未设置门店名" }} · {{ item.store_address || "未设置地址" }}</span>
            <span v-if="item.role === 'merchant'">坐标 {{ item.store_latitude || "?" }}, {{ item.store_longitude || "?" }}</span>
          </div>
          <div class="list-actions">
            <span :class="['state-tag', item.is_active ? 'active' : 'disabled']">
              {{ item.is_active ? "启用中" : "已禁用" }}
            </span>
            <button class="secondary-btn small-btn" :disabled="operatingUserId === item.id || item.id === admin?.id" @click="toggleUser(item)">
              {{ item.is_active ? "禁用用户" : "启用用户" }}
            </button>
          </div>
        </article>
      </section>

      <section v-if="activeTab === 'products'" class="tab-panel">
        <section class="card create-card">
          <div class="section-title">
            <h3>创建商品</h3>
            <span>平台可为指定门店手动创建商品</span>
          </div>
          <div class="field">
            <label for="newDishMerchant">所属门店账号</label>
            <select id="newDishMerchant" v-model="dishForm.merchant">
              <option value="">请选择商家门店</option>
              <option v-for="merchant in merchantUsers" :key="merchant.id" :value="merchant.id">
                {{ merchant.store_name || merchant.username }}
              </option>
            </select>
          </div>
          <div class="field">
            <label for="newDishName">商品名</label>
            <input id="newDishName" v-model="dishForm.name" placeholder="例如：花神拿铁" />
          </div>
          <div class="form-grid">
            <div class="field">
              <label for="newDishCategory">分类</label>
              <select id="newDishCategory" v-model="dishForm.category">
                <option value="coffee">咖啡</option>
                <option value="tea">茶饮</option>
                <option value="dessert">甜点</option>
                <option value="food">轻食</option>
              </select>
            </div>
            <div class="field">
              <label for="newDishStatus">状态</label>
              <select id="newDishStatus" v-model="dishForm.status">
                <option value="available">在售</option>
                <option value="sold_out">售罄</option>
                <option value="off_shelf">下架</option>
              </select>
            </div>
          </div>
          <div class="form-grid">
            <div class="field">
              <label for="newDishPrice">价格</label>
              <input id="newDishPrice" v-model.number="dishForm.price" min="1" type="number" />
            </div>
            <div class="field">
              <label for="newDishStock">库存</label>
              <input id="newDishStock" v-model.number="dishForm.stock" min="0" type="number" />
            </div>
          </div>
          <div class="field">
            <label for="newDishDesc">描述</label>
            <textarea id="newDishDesc" v-model="dishForm.description" placeholder="商品说明"></textarea>
          </div>
          <button class="primary-btn" :disabled="creatingDish" @click="createDish">
            {{ creatingDish ? "创建中..." : "创建商品" }}
          </button>
        </section>

        <section class="card filter-card">
          <input v-model="dishFilters.q" placeholder="按商品名搜索" @keyup.enter="loadDishes" />
          <button class="primary-btn" @click="loadDishes">搜索</button>
        </section>

        <article v-for="dish in dishes" :key="dish.id" class="card product-card">
          <div class="list-main">
            <strong>{{ dish.name }}</strong>
            <span>{{ dish.merchant_store_name || dish.merchant_username }} · 库存 {{ dish.stock }} · {{ money(dish.price) }}</span>
          </div>
          <div class="product-control-stack">
            <label>
              分类
              <select v-model="dish.category">
                <option value="coffee">咖啡</option>
                <option value="tea">茶饮</option>
                <option value="dessert">甜点</option>
                <option value="food">轻食</option>
              </select>
            </label>
            <label>
              状态
              <select v-model="dish.status">
                <option value="available">在售</option>
                <option value="sold_out">售罄</option>
                <option value="off_shelf">下架</option>
              </select>
            </label>
            <label>
              价格
              <input v-model.number="dish.price" min="1" type="number" />
            </label>
            <button class="primary-btn" :disabled="operatingDishId === dish.id" @click="saveDish(dish)">
              {{ operatingDishId === dish.id ? "保存中..." : "保存商品" }}
            </button>
          </div>
        </article>
      </section>

      <section v-if="activeTab === 'stores'" class="tab-panel">
        <section class="card create-card">
          <div class="section-title">
            <h3>分配门店账号</h3>
            <span>可把现有用户转为商家账号，也可输入新账号创建门店</span>
          </div>
          <div class="field">
            <label for="storeUser">选择已有账号</label>
            <select id="storeUser" v-model="storeForm.target_user_id" @change="fillStoreFromUser">
              <option value="">创建新商家账号</option>
              <option v-for="item in users" :key="item.id" :value="item.id">{{ item.username }} · {{ roleText(item.role) }}</option>
            </select>
          </div>
          <div class="form-grid">
            <div class="field">
              <label for="storeUsername">账号名</label>
              <input id="storeUsername" v-model="storeForm.username" placeholder="merchant_new" />
            </div>
            <div class="field">
              <label for="storePassword">密码</label>
              <input id="storePassword" v-model="storeForm.password" placeholder="新账号默认 123456" type="password" />
            </div>
          </div>
          <div class="field">
            <label for="storeName">门店名</label>
            <input id="storeName" v-model="storeForm.store_name" placeholder="花神咖啡馆·某某店" />
          </div>
          <div class="field">
            <label for="storeAddress">文字地址</label>
            <input id="storeAddress" v-model="storeForm.store_address" placeholder="北京市..." />
          </div>
          <div class="form-grid">
            <div class="field">
              <label for="storeLat">纬度</label>
              <input id="storeLat" v-model="storeForm.store_latitude" placeholder="39.992500" />
            </div>
            <div class="field">
              <label for="storeLng">经度</label>
              <input id="storeLng" v-model="storeForm.store_longitude" placeholder="116.337500" />
            </div>
          </div>
          <div class="field">
            <label for="storePhone">联系电话</label>
            <input id="storePhone" v-model="storeForm.phone" placeholder="138..." />
          </div>
          <button class="primary-btn" :disabled="savingStore" @click="saveStoreAccount">
            {{ savingStore ? "保存中..." : "保存门店账号" }}
          </button>
        </section>

        <article v-for="merchant in merchantUsers" :key="merchant.id" class="card user-card">
          <div class="list-main">
            <strong>{{ merchant.store_name || merchant.username }}</strong>
            <span>账号 {{ merchant.username }} · {{ merchant.phone || "未填写电话" }}</span>
            <span>{{ merchant.store_address || "未填写门店地址" }}</span>
            <span>坐标 {{ merchant.store_latitude || "?" }}, {{ merchant.store_longitude || "?" }}</span>
          </div>
          <button class="secondary-btn small-btn" @click="editStore(merchant)">编辑此门店</button>
        </article>
      </section>

      <section v-if="activeTab === 'reports'" class="tab-panel">
        <section class="card ops-card">
          <h3>订单状态报表</h3>
          <div class="status-list">
            <div v-for="item in statusRows" :key="item.key">
              <span>{{ item.label }}</span>
              <b>{{ item.value }}</b>
            </div>
          </div>
        </section>
        <section class="card ops-card">
          <h3>角色分布报表</h3>
          <div class="status-list">
            <div v-for="item in roleRows" :key="item.key">
              <span>{{ item.label }}</span>
              <b>{{ item.value }}</b>
            </div>
          </div>
        </section>
      </section>

      <section v-if="activeTab === 'coupons'" class="tab-panel">
        <form class="card coupon-form" @submit.prevent="issueCoupon">
          <h3>发放优惠券</h3>
          <p class="muted">优惠券仅允许发放给顾客角色。</p>
          <div class="field">
            <label for="couponUser">发放对象</label>
            <select id="couponUser" v-model="couponForm.issued_to">
              <option value="">请选择顾客</option>
              <option v-for="item in couponTargets" :key="item.id" :value="item.id">{{ item.username }}</option>
            </select>
          </div>
          <div class="field">
            <label for="couponTitle">券名称</label>
            <input id="couponTitle" v-model="couponForm.title" placeholder="例如：新客咖啡券" />
          </div>
          <div class="coupon-row">
            <div class="field">
              <label for="couponAmount">优惠金额</label>
              <input id="couponAmount" v-model.number="couponForm.discount_amount" min="1" type="number" />
            </div>
            <div class="field">
              <label for="couponDate">有效期</label>
              <input id="couponDate" v-model="couponForm.valid_until" type="date" />
            </div>
          </div>
          <button class="primary-btn" :disabled="issuingCoupon" type="submit">
            {{ issuingCoupon ? "发放中..." : "发放优惠券" }}
          </button>
        </form>

        <article v-for="coupon in coupons" :key="coupon.id" class="card coupon-card">
          <div class="list-main">
            <strong>{{ coupon.title }}</strong>
            <span>{{ coupon.code }} · 发给 {{ coupon.issued_to_username }}</span>
          </div>
          <div class="coupon-meta">
            <b>{{ money(coupon.discount_amount) }}</b>
            <span :class="['state-tag', coupon.is_available ? 'active' : 'disabled']">
              {{ coupon.is_available ? "可用" : "不可用" }}
            </span>
          </div>
        </article>
      </section>
    </template>
  </section>
</template>

<script setup>
import { computed, onMounted, reactive, ref } from "vue";
import { useRouter } from "vue-router";

import {
  createPlatformDish,
  fetchPlatformCoupons,
  fetchPlatformDashboard,
  fetchPlatformDishes,
  fetchPlatformUsers,
  issuePlatformCoupon,
  savePlatformStoreAccount,
  updatePlatformDish,
  updatePlatformUserStatus,
} from "../api/platform";
import { money, roleText, statusText } from "../utils/format";
import { clearStoredPlatformAdmin, getPlatformAdminId, getStoredPlatformAdmin } from "../utils/session";

const router = useRouter();
const admin = ref(getStoredPlatformAdmin());
const loading = ref(true);
const error = ref("");
const message = ref("");
const activeTab = ref("overview");
const operatingUserId = ref(null);
const operatingDishId = ref(null);
const issuingCoupon = ref(false);
const creatingDish = ref(false);
const savingStore = ref(false);
const users = ref([]);
const dishes = ref([]);
const coupons = ref([]);
const dashboard = ref({ metrics: {}, role_counts: {}, status_counts: {}, recent_orders: [] });
const userFilters = reactive({ role: "", q: "" });
const dishFilters = reactive({ q: "" });
const dishForm = reactive({
  merchant: "",
  name: "",
  category: "coffee",
  status: "available",
  price: 20,
  stock: 10,
  description: "",
});
const storeForm = reactive({
  target_user_id: "",
  username: "",
  password: "",
  phone: "",
  store_name: "",
  store_address: "",
  store_latitude: "",
  store_longitude: "",
});
const couponForm = reactive({ issued_to: "", title: "花神咖啡优惠券", description: "", discount_amount: 5, valid_until: "" });

const tabs = [
  { key: "overview", label: "总览" },
  { key: "users", label: "用户" },
  { key: "products", label: "商品" },
  { key: "stores", label: "门店" },
  { key: "reports", label: "报表" },
  { key: "coupons", label: "优惠券" },
];

const metrics = computed(() => [
  { label: "用户", value: dashboard.value.metrics.users || 0 },
  { label: "禁用", value: dashboard.value.metrics.disabled_users || 0 },
  { label: "商品", value: dashboard.value.metrics.dishes || 0 },
  { label: "订单", value: dashboard.value.metrics.orders || 0 },
  { label: "优惠券", value: dashboard.value.metrics.coupons || 0 },
  { label: "营收", value: money(dashboard.value.metrics.revenue) },
]);

const statusRows = computed(() =>
  ["pending_payment", "paid", "preparing", "waiting_pickup", "waiting_delivery", "delivering", "completed", "cancelled"].map((key) => ({
    key,
    label: statusText(key),
    value: dashboard.value.status_counts[key] || 0,
  })),
);

const roleRows = computed(() =>
  [
    { key: "customer", label: "顾客" },
    { key: "merchant", label: "商家" },
    { key: "driver", label: "骑手" },
  ].map((role) => ({ ...role, value: dashboard.value.role_counts[role.key] || 0 })),
);

const visibleUsers = computed(() => {
  const query = userFilters.q.trim().toLowerCase();
  return users.value.filter((item) => {
    const roleMatched = !userFilters.role || item.role === userFilters.role;
    const queryMatched = !query || item.username.toLowerCase().includes(query);
    return roleMatched && queryMatched;
  });
});
const merchantUsers = computed(() => users.value.filter((item) => item.role === "merchant"));
const couponTargets = computed(() => users.value.filter((item) => item.role === "customer" && item.is_active && !item.is_staff && !item.is_superuser));

async function refreshAll() {
  loading.value = true;
  error.value = "";
  message.value = "";
  try {
    await Promise.all([loadDashboard(), loadUsers(), loadDishes(), loadCoupons()]);
  } catch (err) {
    error.value = err.message;
  } finally {
    loading.value = false;
  }
}

async function loadDashboard() {
  const { data } = await fetchPlatformDashboard(getPlatformAdminId());
  dashboard.value = data;
}

async function loadUsers() {
  const { data } = await fetchPlatformUsers(getPlatformAdminId());
  users.value = data.users;
}

async function loadDishes() {
  const { data } = await fetchPlatformDishes(getPlatformAdminId(), {
    ...(dishFilters.q ? { q: dishFilters.q } : {}),
  });
  dishes.value = data.dishes;
}

async function loadCoupons() {
  const { data } = await fetchPlatformCoupons(getPlatformAdminId());
  coupons.value = data.coupons;
}

async function toggleUser(item) {
  operatingUserId.value = item.id;
  error.value = "";
  message.value = "";
  try {
    await updatePlatformUserStatus(getPlatformAdminId(), item.id, !item.is_active);
    message.value = `${item.username} 已${item.is_active ? "禁用" : "启用"}。`;
    await Promise.all([loadUsers(), loadDashboard()]);
  } catch (err) {
    error.value = err.message;
  } finally {
    operatingUserId.value = null;
  }
}

async function createDish() {
  creatingDish.value = true;
  error.value = "";
  message.value = "";
  try {
    await createPlatformDish(getPlatformAdminId(), { ...dishForm, merchant: Number(dishForm.merchant) });
    message.value = "商品已创建。";
    Object.assign(dishForm, { merchant: "", name: "", category: "coffee", status: "available", price: 20, stock: 10, description: "" });
    await Promise.all([loadDishes(), loadDashboard()]);
  } catch (err) {
    error.value = err.message;
  } finally {
    creatingDish.value = false;
  }
}

async function saveDish(dish) {
  operatingDishId.value = dish.id;
  error.value = "";
  message.value = "";
  try {
    await updatePlatformDish(getPlatformAdminId(), dish.id, {
      category: dish.category,
      status: dish.status,
      price: dish.price,
    });
    message.value = `${dish.name} 已更新。`;
    await loadDishes();
  } catch (err) {
    error.value = err.message;
  } finally {
    operatingDishId.value = null;
  }
}

function fillStoreFromUser() {
  const selected = users.value.find((item) => Number(item.id) === Number(storeForm.target_user_id));
  if (!selected) {
    Object.assign(storeForm, { username: "", password: "", phone: "", store_name: "", store_address: "", store_latitude: "", store_longitude: "" });
    return;
  }
  Object.assign(storeForm, {
    username: selected.username,
    password: "",
    phone: selected.phone || "",
    store_name: selected.store_name || "",
    store_address: selected.store_address || "",
    store_latitude: selected.store_latitude || "",
    store_longitude: selected.store_longitude || "",
  });
}

function editStore(merchant) {
  activeTab.value = "stores";
  Object.assign(storeForm, {
    target_user_id: merchant.id,
    username: merchant.username,
    password: "",
    phone: merchant.phone || "",
    store_name: merchant.store_name || "",
    store_address: merchant.store_address || "",
    store_latitude: merchant.store_latitude || "",
    store_longitude: merchant.store_longitude || "",
  });
}

async function saveStoreAccount() {
  savingStore.value = true;
  error.value = "";
  message.value = "";
  try {
    await savePlatformStoreAccount(getPlatformAdminId(), { ...storeForm });
    message.value = "门店账号已保存。";
    Object.assign(storeForm, { target_user_id: "", username: "", password: "", phone: "", store_name: "", store_address: "", store_latitude: "", store_longitude: "" });
    await Promise.all([loadUsers(), loadDashboard()]);
  } catch (err) {
    error.value = err.message;
  } finally {
    savingStore.value = false;
  }
}

async function issueCoupon() {
  if (!couponForm.issued_to) {
    error.value = "请选择顾客。";
    return;
  }
  issuingCoupon.value = true;
  error.value = "";
  message.value = "";
  try {
    await issuePlatformCoupon(getPlatformAdminId(), { ...couponForm, issued_to: Number(couponForm.issued_to) });
    message.value = "优惠券已发放。";
    couponForm.issued_to = "";
    await Promise.all([loadCoupons(), loadDashboard()]);
  } catch (err) {
    error.value = err.message;
  } finally {
    issuingCoupon.value = false;
  }
}

function logout() {
  clearStoredPlatformAdmin();
  router.push("/platform/login");
}

onMounted(refreshAll);
</script>

<style scoped>
.platform-dashboard,
.tab-panel {
  display: grid;
  gap: 14px;
}

.platform-hero {
  align-items: end;
  background:
    linear-gradient(135deg, rgba(16, 63, 52, 0.94), rgba(16, 63, 52, 0.58)),
    url("/hero.png") center / cover;
  border-radius: 30px;
  color: #ffffff;
  display: flex;
  justify-content: space-between;
  min-height: 180px;
  padding: 20px;
}

.platform-hero span {
  color: rgba(255, 255, 255, 0.82);
  display: block;
  font-size: 13px;
  font-weight: 800;
  margin-bottom: 6px;
}

.platform-hero strong {
  font-family: Georgia, "Times New Roman", "Songti SC", serif;
  font-size: 34px;
}

.platform-tabs {
  background: #ffffff;
  border: 1px solid #e8ded0;
  border-radius: 18px;
  display: flex;
  gap: 6px;
  overflow-x: auto;
  padding: 6px;
  scrollbar-width: none;
}

.platform-tabs::-webkit-scrollbar {
  display: none;
}

.platform-tabs button {
  background: transparent;
  border-radius: 14px;
  color: #68736d;
  flex: 0 0 auto;
  font-size: 13px;
  font-weight: 900;
  min-height: 40px;
  min-width: 68px;
  padding: 0 12px;
}

.platform-tabs button.active {
  background: #dff2ea;
  color: #0e7a55;
}

.metric-grid,
.form-grid {
  display: grid;
  gap: 10px;
  grid-template-columns: repeat(2, 1fr);
}

.metric-card,
.ops-card,
.coupon-form,
.create-card,
.filter-card {
  padding: 16px;
}

.metric-card,
.create-card {
  display: grid;
  gap: 12px;
}

.metric-card span,
.list-main span,
.coupon-meta span,
.section-title span {
  color: #6d766f;
  font-size: 13px;
  font-weight: 800;
}

.metric-card strong {
  color: #103f34;
  font-size: 28px;
}

.section-title {
  display: grid;
  gap: 5px;
}

.section-title h3,
.ops-card h3,
.coupon-form h3 {
  font-family: Georgia, "Times New Roman", "Songti SC", serif;
  margin: 0;
}

.filter-card {
  display: grid;
  gap: 10px;
}

.filter-card input,
.filter-card select,
.product-control-stack select,
.product-control-stack input {
  background: #ffffff;
  border: 1px solid #eadfce;
  border-radius: 13px;
  min-height: 42px;
  min-width: 0;
  padding: 0 10px;
}

.status-list {
  display: grid;
  gap: 9px;
}

.status-list div {
  align-items: center;
  background: #fbf7ee;
  border: 1px solid #efe4d4;
  border-radius: 14px;
  display: flex;
  justify-content: space-between;
  padding: 10px 12px;
}

.user-card,
.product-card,
.coupon-card {
  display: grid;
  gap: 14px;
  padding: 16px;
}

.list-main {
  display: grid;
  gap: 6px;
  min-width: 0;
}

.list-main strong {
  color: #1c2c25;
  font-size: 18px;
  line-height: 1.25;
}

.list-main span {
  line-height: 1.45;
}

.list-actions,
.coupon-meta {
  align-items: center;
  display: flex;
  gap: 10px;
  justify-content: space-between;
}

.state-tag {
  border-radius: 999px;
  font-size: 12px;
  font-weight: 900;
  padding: 6px 10px;
}

.state-tag.active {
  background: #dff2ea;
  color: #0e7a55;
}

.state-tag.disabled {
  background: #fce6e0;
  color: #b42318;
}

.small-btn {
  font-size: 13px;
  min-height: 38px;
  padding: 0 14px;
}

.product-control-stack {
  background: #fbf7ee;
  border: 1px solid #efe4d4;
  border-radius: 18px;
  display: grid;
  gap: 10px;
  padding: 12px;
}

.product-control-stack label {
  color: #6d766f;
  display: grid;
  font-size: 12px;
  font-weight: 900;
  gap: 6px;
}

.product-control-stack .primary-btn,
.coupon-form .primary-btn,
.create-card .primary-btn,
.filter-card .primary-btn {
  width: 100%;
}

.coupon-row {
  display: grid;
  gap: 10px;
  grid-template-columns: 1fr 1fr;
}

.coupon-meta b {
  color: #103f34;
  font-size: 20px;
}
</style>
