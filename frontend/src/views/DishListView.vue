<template>
  <section>
    <header class="top-bar">
      <div>
        <p class="eyebrow">花神咖啡馆 · Open until 8:00 PM</p>
        <h2 class="title">点单</h2>
      </div>
      <RouterLink class="ghost-btn" to="/profile">我的</RouterLink>
    </header>

    <button class="store-button" type="button" @click="showStores = !showStores">
      <span>
        <em>当前门店</em>
        <strong>{{ selectedStore?.store_name || "请选择门店" }}</strong>
      </span>
      <b>切换</b>
    </button>

    <section v-if="showStores" class="card store-panel">
      <button
        v-for="store in stores"
        :key="store.id"
        class="store-option"
        :class="{ active: selectedStore?.id === store.id }"
        type="button"
        @click="selectStore(store)"
      >
        <span>
          <strong>{{ store.store_name }}</strong>
          <em>{{ store.store_address }}</em>
        </span>
      </button>
    </section>

    <div class="order-mode-card">
      <span>取餐方式</span>
      <div class="fulfillment-switch" role="group" aria-label="取餐方式">
        <button :class="{ active: fulfillmentType === 'self_pickup' }" @click="selectFulfillment('self_pickup')">
          到店自取
        </button>
        <button :class="{ active: fulfillmentType === 'delivery' }" @click="selectFulfillment('delivery')">
          外送
        </button>
      </div>
    </div>

    <div class="search-card">
      <input v-model="keyword" placeholder="搜索饮品、餐点" />
      <span>筛选</span>
    </div>

    <div class="tabs">
      <button
        v-for="tab in tabs"
        :key="tab.key"
        :class="{ active: activeTab === tab.key }"
        @click="selectTab(tab.key)"
      >
        {{ tab.label }}
      </button>
    </div>

    <p v-if="error" class="danger-text">{{ error }}</p>
    <div v-if="loading" class="loading">正在加载餐品...</div>

    <div v-else class="dish-list">
      <article v-for="dish in filteredDishes" :key="dish.id" class="card dish-card">
        <RouterLink class="item-art" :to="`/dishes/${dish.id}`">
          <span>{{ dish.name.slice(0, 1) }}</span>
        </RouterLink>
        <div class="dish-info">
          <div class="dish-row">
            <span class="status-pill">{{ categoryText(dish.category) }}</span>
            <span class="heart">♡</span>
          </div>
          <RouterLink class="dish-name" :to="`/dishes/${dish.id}`">{{ dish.name }}</RouterLink>
          <p>{{ dish.description || "新鲜制作，适合现在来一杯。" }}</p>
          <small>{{ dish.merchant_store_name || dish.merchant_username }}</small>
          <div class="dish-bottom">
            <strong>{{ money(dish.price) }}</strong>
            <button class="round-btn" :disabled="dish.status !== 'available'" @click="addDish(dish)">+</button>
          </div>
        </div>
      </article>

      <div v-if="filteredDishes.length === 0" class="empty-state">
        <strong>没有找到餐品</strong>
        <p class="muted">换个关键词、分类或门店试试。</p>
      </div>
    </div>

    <RouterLink v-if="cartCount > 0" class="checkout-bar" to="/cart">
      <span class="bag">袋</span>
      <span>
        <strong>{{ cartCount }} 件商品</strong>
        <em>{{ fulfillmentLabel }} · 合计 {{ money(cartTotal) }}</em>
      </span>
      <b>结算</b>
    </RouterLink>
  </section>
</template>

<script setup>
import { computed, onMounted, ref } from "vue";

import { addCartItem, fetchCart, fetchDishesByCategory, fetchStores } from "../api/customer";
import { money } from "../utils/format";
import {
  getCustomerId,
  getFulfillmentType,
  getSelectedStore,
  setFulfillmentType,
  setSelectedStore,
} from "../utils/session";

const dishes = ref([]);
const stores = ref([]);
const selectedStore = ref(getSelectedStore());
const cartCount = ref(0);
const cartTotal = ref(0);
const loading = ref(true);
const error = ref("");
const keyword = ref("");
const showStores = ref(false);
const tabs = [
  { key: "", label: "全部" },
  { key: "coffee", label: "咖啡" },
  { key: "tea", label: "茶饮" },
  { key: "dessert", label: "甜点" },
  { key: "food", label: "轻食" },
];
const activeTab = ref("");
const fulfillmentType = ref(getFulfillmentType());
const fulfillmentLabel = computed(() => (fulfillmentType.value === "delivery" ? "外送" : "到店自取"));

const filteredDishes = computed(() => {
  const query = keyword.value.trim().toLowerCase();
  return dishes.value.filter((dish) => {
    const text = `${dish.name} ${dish.description}`.toLowerCase();
    return !query || text.includes(query);
  });
});

function categoryText(category) {
  const map = {
    coffee: "咖啡",
    tea: "茶饮",
    dessert: "甜点",
    food: "轻食",
  };
  return map[category] || "现做供应";
}

function selectFulfillment(type) {
  fulfillmentType.value = type;
  setFulfillmentType(type);
}

async function selectStore(store) {
  selectedStore.value = store;
  setSelectedStore(store);
  showStores.value = false;
  await loadDishes();
}

async function selectTab(category) {
  activeTab.value = category;
  await loadDishes();
}

async function loadStores() {
  const { data } = await fetchStores();
  stores.value = data.stores;
  if (!selectedStore.value || !stores.value.some((store) => store.id === selectedStore.value.id)) {
    selectedStore.value = stores.value[0] || null;
    if (selectedStore.value) {
      setSelectedStore(selectedStore.value);
    }
  }
}

async function loadCart() {
  const userId = getCustomerId();
  const { data } = await fetchCart(userId);
  cartCount.value = data.items.reduce((sum, item) => sum + item.quantity, 0);
  cartTotal.value = data.total_amount;
}

async function loadDishes() {
  loading.value = true;
  error.value = "";

  try {
    const { data } = await fetchDishesByCategory(activeTab.value, selectedStore.value?.id);
    dishes.value = data.dishes;
    await loadCart();
  } catch (err) {
    error.value = err.message;
  } finally {
    loading.value = false;
  }
}

async function addDish(dish) {
  try {
    await addCartItem(getCustomerId(), dish.id, 1, selectedStore.value?.id);
    await loadCart();
  } catch (err) {
    error.value = err.message;
  }
}

onMounted(async () => {
  await loadStores();
  await loadDishes();
});
</script>

<style scoped>
.store-button {
  align-items: center;
  background: #ffffff;
  border: 1px solid #efe4d6;
  border-radius: 20px;
  display: flex;
  justify-content: space-between;
  margin-bottom: 12px;
  padding: 13px 16px;
  text-align: left;
  width: 100%;
}

.store-button span {
  display: grid;
  gap: 4px;
  min-width: 0;
}

.store-button em {
  color: #6f7b74;
  font-size: 12px;
  font-style: normal;
  font-weight: 900;
}

.store-button strong {
  color: #172821;
  font-size: 17px;
}

.store-button b {
  color: #0e7a55;
}

.store-panel {
  display: grid;
  gap: 8px;
  margin-bottom: 14px;
  padding: 12px;
}

.store-option {
  background: #f8f4ee;
  border: 1px solid transparent;
  border-radius: 16px;
  color: #1c2c25;
  padding: 12px;
  text-align: left;
}

.store-option.active {
  background: #edf7f2;
  border-color: #9ed7bd;
}

.store-option span {
  display: grid;
  gap: 5px;
}

.store-option em {
  color: #758078;
  font-size: 12px;
  font-style: normal;
  font-weight: 800;
}

.order-mode-card {
  background: #ffffff;
  border: 1px solid #efe4d6;
  border-radius: 22px;
  box-shadow: 0 8px 22px rgba(24, 34, 29, 0.05);
  display: grid;
  gap: 12px;
  margin-bottom: 20px;
  padding: 12px;
}

.order-mode-card > span {
  color: #6f7b74;
  font-size: 13px;
  font-weight: 900;
}

.fulfillment-switch {
  background: #ffffff;
  border: 1px solid #eadfce;
  border-radius: 999px;
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  padding: 5px;
}

.fulfillment-switch button {
  background: transparent;
  border-radius: 999px;
  color: #68736d;
  font-weight: 900;
  min-height: 42px;
}

.fulfillment-switch button.active {
  background: #103f34;
  color: #ffffff;
}

.search-card {
  align-items: center;
  background: #ffffff;
  border: 1px solid #ede5dc;
  border-radius: 22px;
  display: flex;
  gap: 12px;
  margin-bottom: 20px;
  padding: 0 16px;
}

.search-card input {
  border: 0;
  flex: 1;
  min-height: 48px;
  outline: none;
}

.search-card span {
  color: #0e7a55;
  font-size: 13px;
  font-weight: 900;
}

.tabs {
  display: flex;
  gap: 8px;
  margin-bottom: 18px;
  overflow-x: auto;
  padding-bottom: 2px;
}

.tabs button {
  background: #ffffff;
  border-radius: 999px;
  color: #7a827d;
  flex: 0 0 auto;
  font-weight: 800;
  min-height: 38px;
  padding: 0 16px;
}

.tabs button.active {
  background: #dff2ea;
  color: #0e7a55;
}

.dish-list {
  display: grid;
  gap: 14px;
}

.dish-card {
  display: grid;
  gap: 14px;
  grid-template-columns: 116px minmax(0, 1fr);
  min-height: 156px;
  padding: 14px;
}

.dish-info {
  display: grid;
  gap: 7px;
  min-width: 0;
}

.dish-row,
.dish-bottom {
  align-items: center;
  display: flex;
  justify-content: space-between;
}

.heart {
  color: #a9b0ab;
  font-size: 24px;
}

.dish-name {
  color: #182923;
  font-size: 19px;
  font-weight: 900;
  text-decoration: none;
}

.dish-info p,
.dish-info small {
  color: #778079;
  font-size: 13px;
  line-height: 1.45;
  margin: 0;
}

.dish-bottom strong {
  color: #103f34;
  font-size: 20px;
}

.checkout-bar {
  align-items: center;
  background: #103f34;
  border-radius: 26px;
  bottom: 88px;
  box-shadow: 0 16px 34px rgba(16, 63, 52, 0.24);
  color: #ffffff;
  display: grid;
  gap: 12px;
  grid-template-columns: 52px 1fr auto;
  left: 18px;
  padding: 12px 14px;
  position: absolute;
  right: 18px;
  text-decoration: none;
  z-index: 18;
}

.bag {
  align-items: center;
  background: #ffffff;
  border-radius: 18px;
  color: #103f34;
  display: flex;
  font-weight: 900;
  height: 52px;
  justify-content: center;
}

.checkout-bar span {
  display: grid;
}

.checkout-bar em {
  color: #d8eee5;
  font-style: normal;
  margin-top: 2px;
}

.checkout-bar b {
  background: #ffffff;
  border-radius: 999px;
  color: #103f34;
  padding: 12px 18px;
}
</style>
