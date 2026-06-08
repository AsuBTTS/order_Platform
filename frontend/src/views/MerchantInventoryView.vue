<template>
  <section class="inventory-view">
    <header class="top-bar">
      <div>
        <p class="eyebrow">Inventory</p>
        <h2 class="title">进货库存</h2>
      </div>
      <button class="ghost-btn" @click="loadDishes">刷新</button>
    </header>

    <section class="inventory-summary">
      <article class="card summary-card">
        <span>商品数</span>
        <strong>{{ dishes.length }}</strong>
      </article>
      <article class="card summary-card">
        <span>总库存</span>
        <strong>{{ totalStock }}</strong>
      </article>
    </section>

    <section class="card create-card">
      <button class="create-toggle" type="button" @click="showCreate = !showCreate">
        <span>
          <strong>添加新商品</strong>
          <small>商家进货前可先建立商品档案</small>
        </span>
        <b>{{ showCreate ? "收起" : "展开" }}</b>
      </button>

      <div v-if="showCreate" class="create-form">
        <div class="field">
          <label for="dishName">商品名</label>
          <input id="dishName" v-model="newDish.name" placeholder="例如：玫瑰拿铁" />
        </div>
        <div class="field">
          <label for="dishCategory">分类</label>
          <select id="dishCategory" v-model="newDish.category">
            <option value="coffee">咖啡</option>
            <option value="tea">茶饮</option>
            <option value="dessert">甜点</option>
            <option value="food">轻食</option>
          </select>
        </div>
        <div class="create-row">
          <div class="field">
            <label for="dishPrice">价格</label>
            <input id="dishPrice" v-model.number="newDish.price" min="1" type="number" />
          </div>
          <div class="field">
            <label for="dishStock">初始库存</label>
            <input id="dishStock" v-model.number="newDish.stock" min="0" type="number" />
          </div>
        </div>
        <div class="field">
          <label for="dishDesc">描述</label>
          <textarea id="dishDesc" v-model="newDish.description" placeholder="商品说明"></textarea>
        </div>
        <button class="primary-btn" :disabled="creating" @click="createDish">
          {{ creating ? "添加中..." : "添加商品" }}
        </button>
      </div>
    </section>

    <p v-if="error" class="danger-text">{{ error }}</p>
    <p v-if="message" class="success-text">{{ message }}</p>
    <div v-if="loading" class="loading">正在加载库存...</div>

    <div v-else class="inventory-list">
      <article v-for="dish in dishes" :key="dish.id" class="card inventory-card">
        <div class="item-art small-art">
          <span>{{ dish.name.slice(0, 1) }}</span>
        </div>
        <div class="inventory-main">
          <div class="item-head">
            <strong>{{ dish.name }}</strong>
            <span class="stock-pill">库存 {{ dish.stock }}</span>
          </div>
          <span class="item-meta">{{ money(dish.price) }} · {{ categoryLabel(dish.category) }} · {{ statusLabel(dish.status) }}</span>
          <div class="restock-panel">
            <label :for="`restock-${dish.id}`">本次进货数量</label>
            <div class="restock-row">
              <input :id="`restock-${dish.id}`" v-model.number="restockMap[dish.id]" min="1" type="number" />
              <button class="primary-btn" :disabled="operatingId === dish.id" @click="restock(dish)">
                {{ operatingId === dish.id ? "进货中..." : "进货" }}
              </button>
            </div>
          </div>
        </div>
      </article>
    </div>
  </section>
</template>

<script setup>
import { computed, onMounted, reactive, ref } from "vue";

import { createMerchantDish, fetchMerchantDishes, restockMerchantDish } from "../api/merchant";
import { money } from "../utils/format";
import { getMerchantId } from "../utils/session";

const dishes = ref([]);
const restockMap = reactive({});
const newDish = reactive({
  name: "",
  category: "coffee",
  price: 20,
  stock: 10,
  description: "",
});
const loading = ref(true);
const creating = ref(false);
const showCreate = ref(false);
const operatingId = ref(null);
const error = ref("");
const message = ref("");

const totalStock = computed(() => dishes.value.reduce((sum, dish) => sum + Number(dish.stock || 0), 0));

function statusLabel(status) {
  const labels = {
    available: "在售",
    sold_out: "售罄",
    off_shelf: "下架",
  };
  return labels[status] || status;
}

function categoryLabel(category) {
  const labels = {
    coffee: "咖啡",
    tea: "茶饮",
    dessert: "甜点",
    food: "轻食",
  };
  return labels[category] || category;
}

async function loadDishes() {
  loading.value = true;
  error.value = "";

  try {
    const { data } = await fetchMerchantDishes(getMerchantId());
    dishes.value = data.dishes;
    data.dishes.forEach((dish) => {
      if (!restockMap[dish.id]) {
        restockMap[dish.id] = 10;
      }
    });
  } catch (err) {
    error.value = err.message;
  } finally {
    loading.value = false;
  }
}

async function createDish() {
  creating.value = true;
  error.value = "";
  message.value = "";
  try {
    await createMerchantDish(getMerchantId(), newDish);
    message.value = "商品已添加。";
    Object.assign(newDish, { name: "", category: "coffee", price: 20, stock: 10, description: "" });
    showCreate.value = false;
    await loadDishes();
  } catch (err) {
    error.value = err.message;
  } finally {
    creating.value = false;
  }
}

async function restock(dish) {
  const quantity = Number(restockMap[dish.id] || 0);
  if (quantity <= 0) {
    error.value = "进货数量必须大于 0。";
    return;
  }

  operatingId.value = dish.id;
  error.value = "";
  message.value = "";
  try {
    await restockMerchantDish(getMerchantId(), dish.id, quantity);
    message.value = `${dish.name} 已进货 ${quantity} 件。`;
    await loadDishes();
  } catch (err) {
    error.value = err.message;
  } finally {
    operatingId.value = null;
  }
}

onMounted(loadDishes);
</script>

<style scoped>
.inventory-view,
.inventory-list {
  display: grid;
  gap: 14px;
}

.inventory-summary {
  display: grid;
  gap: 10px;
  grid-template-columns: repeat(2, 1fr);
}

.summary-card {
  display: grid;
  gap: 8px;
  padding: 16px;
}

.summary-card span {
  color: #728078;
  font-size: 13px;
  font-weight: 800;
}

.summary-card strong {
  color: #103f34;
  font-size: 28px;
}

.create-card {
  overflow: hidden;
}

.create-toggle {
  align-items: center;
  background: #ffffff;
  color: #1f2924;
  display: flex;
  justify-content: space-between;
  padding: 16px;
  text-align: left;
  width: 100%;
}

.create-toggle span {
  display: grid;
  gap: 5px;
}

.create-toggle strong {
  font-size: 18px;
}

.create-toggle small {
  color: #738078;
  font-size: 12px;
  font-weight: 800;
}

.create-toggle b {
  color: #0e7a55;
  font-size: 13px;
}

.create-form {
  border-top: 1px solid #efe8df;
  display: grid;
  gap: 10px;
  padding: 16px;
}

.create-row {
  display: grid;
  gap: 10px;
  grid-template-columns: 1fr 1fr;
}

.inventory-card {
  display: grid;
  gap: 12px;
  grid-template-columns: 76px minmax(0, 1fr);
  padding: 14px;
}

.small-art {
  border-radius: 18px;
  height: 76px;
  width: 76px;
}

.inventory-main {
  display: grid;
  gap: 9px;
  min-width: 0;
}

.item-head {
  align-items: start;
  display: flex;
  gap: 10px;
  justify-content: space-between;
}

.item-head strong {
  font-size: 18px;
  line-height: 1.25;
}

.item-meta {
  color: #778079;
  font-size: 13px;
  font-weight: 800;
}

.stock-pill {
  background: #eef8f3;
  border-radius: 999px;
  color: #0e7a55;
  flex-shrink: 0;
  font-size: 12px;
  font-weight: 900;
  padding: 5px 8px;
}

.restock-panel {
  background: #faf6f0;
  border-radius: 16px;
  display: grid;
  gap: 8px;
  padding: 10px;
}

.restock-panel label {
  color: #738078;
  font-size: 12px;
  font-weight: 900;
}

.restock-row {
  display: grid;
  gap: 8px;
  grid-template-columns: minmax(0, 1fr) auto;
}

.restock-row input {
  border: 1px solid #eadfce;
  border-radius: 999px;
  min-width: 0;
  padding: 0 12px;
}

.restock-row .primary-btn {
  min-width: 86px;
  padding: 0 14px;
}
</style>
