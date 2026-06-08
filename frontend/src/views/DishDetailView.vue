<template>
  <section>
    <RouterLink class="back-link" to="/dishes">返回菜单</RouterLink>

    <div v-if="loading" class="loading">正在加载餐品...</div>
    <p v-else-if="error" class="danger-text">{{ error }}</p>

    <article v-else class="detail-card">
      <div class="detail-art item-art">
        <span>{{ dish.name.slice(0, 1) }}</span>
      </div>

      <div class="detail-body">
        <span class="status-pill">{{ dish.status === "available" ? "现做供应" : "暂不可售" }}</span>
        <h2 class="title">{{ dish.name }}</h2>
        <p class="muted">{{ dish.description || "口感清爽，适合日常点单。" }}</p>
        <p class="store-line">{{ dish.merchant_store_name || dish.merchant_username }}</p>

        <dl class="meta-grid">
          <div>
            <dt>基础价</dt>
            <dd>{{ money(dish.price) }}</dd>
          </div>
          <div>
            <dt>库存</dt>
            <dd>{{ dish.stock }}</dd>
          </div>
        </dl>

        <section class="custom-card">
          <h3>定制</h3>
          <div class="option-group">
            <span>温度</span>
            <div>
              <button
                v-for="option in temperatureOptions"
                :key="option.value"
                :class="{ active: customization.temperature === option.value }"
                @click="customization.temperature = option.value"
              >
                {{ option.label }}
              </button>
            </div>
          </div>
          <div class="option-group">
            <span>冰量</span>
            <div>
              <button
                v-for="option in iceOptions"
                :key="option.value"
                :class="{ active: customization.ice === option.value }"
                @click="customization.ice = option.value"
              >
                {{ option.label }}
              </button>
            </div>
          </div>
          <div class="option-group">
            <span>杯型</span>
            <div>
              <button
                v-for="option in sizeOptions"
                :key="option.value"
                :class="{ active: customization.size === option.value }"
                @click="customization.size = option.value"
              >
                {{ option.label }}
              </button>
            </div>
          </div>
        </section>

        <div class="qty-row">
          <span>数量</span>
          <div class="stepper">
            <button @click="quantity = Math.max(1, quantity - 1)">-</button>
            <strong>{{ quantity }}</strong>
            <button @click="quantity += 1">+</button>
          </div>
        </div>

        <button class="primary-btn add-btn" :disabled="dish.status !== 'available' || submitting" @click="addToCart">
          {{ submitting ? "加入中..." : `加入购物车 · ${money(totalPrice)}` }}
        </button>
        <RouterLink class="secondary-btn add-btn" to="/cart">查看购物车</RouterLink>
        <p v-if="message" class="success-text">{{ message }}</p>
        <p v-if="submitError" class="danger-text">{{ submitError }}</p>
      </div>
    </article>
  </section>
</template>

<script setup>
import { computed, onMounted, reactive, ref } from "vue";
import { useRoute, useRouter } from "vue-router";

import { addCartItem, fetchDish } from "../api/customer";
import { money } from "../utils/format";
import { getCustomerId, getSelectedStoreId, setSelectedStore } from "../utils/session";

const route = useRoute();
const router = useRouter();
const dish = ref(null);
const quantity = ref(1);
const loading = ref(true);
const submitting = ref(false);
const error = ref("");
const submitError = ref("");
const message = ref("");
const customization = reactive({
  temperature: "iced",
  ice: "regular",
  size: "small",
});

const temperatureOptions = [
  { value: "iced", label: "冰" },
  { value: "hot", label: "热" },
];
const iceOptions = [
  { value: "regular", label: "正常冰" },
  { value: "less", label: "少冰" },
  { value: "none", label: "去冰" },
];
const sizeOptions = [
  { value: "small", label: "小杯" },
  { value: "medium", label: "中杯 +¥3" },
  { value: "large", label: "大杯 +¥5" },
];

const unitPrice = computed(() => Number(dish.value?.price || 0) + sizePriceDelta(customization.size));
const totalPrice = computed(() => unitPrice.value * quantity.value);

function sizePriceDelta(size) {
  if (size === "medium") return 3;
  if (size === "large") return 5;
  return 0;
}

async function loadDish() {
  loading.value = true;
  error.value = "";

  try {
    const { data } = await fetchDish(route.params.id);
    dish.value = data.dish;
    if (!getSelectedStoreId() || Number(getSelectedStoreId()) !== Number(data.dish.merchant)) {
      setSelectedStore({
        id: data.dish.merchant,
        store_name: data.dish.merchant_store_name,
        store_address: data.dish.merchant_store_address,
      });
    }
  } catch (err) {
    error.value = err.message;
  } finally {
    loading.value = false;
  }
}

async function addToCart() {
  const userId = getCustomerId();
  if (!userId) {
    router.push("/login");
    return;
  }

  submitting.value = true;
  submitError.value = "";
  message.value = "";

  try {
    await addCartItem(userId, dish.value.id, quantity.value, dish.value.merchant, { ...customization });
    message.value = "已加入购物车";
  } catch (err) {
    submitError.value = err.message;
  } finally {
    submitting.value = false;
  }
}

onMounted(loadDish);
</script>

<style scoped>
.back-link {
  color: #52615a;
  display: inline-flex;
  font-weight: 800;
  margin-bottom: 16px;
  text-decoration: none;
}

.detail-card {
  background: #ffffff;
  border-radius: 28px;
  box-shadow: 0 16px 38px rgba(24, 34, 29, 0.09);
  overflow: hidden;
}

.detail-art {
  border-radius: 0;
  height: 260px;
  width: 100%;
}

.detail-body {
  display: grid;
  gap: 16px;
  padding: 20px;
}

.store-line {
  color: #0e7a55;
  font-size: 13px;
  font-weight: 900;
  margin: -8px 0 0;
}

.meta-grid {
  display: grid;
  gap: 12px;
  grid-template-columns: repeat(2, 1fr);
  margin: 0;
}

.meta-grid div,
.custom-card {
  background: #fbf7ee;
  border: 1px solid #efe4d4;
  border-radius: 18px;
  padding: 14px;
}

.meta-grid dt {
  color: #79837d;
  font-size: 12px;
  font-weight: 800;
}

.meta-grid dd {
  color: #103f34;
  font-size: 20px;
  font-weight: 900;
  margin: 4px 0 0;
}

.custom-card {
  background:
    linear-gradient(135deg, rgba(255, 251, 244, 0.96), rgba(238, 248, 243, 0.9)),
    radial-gradient(circle at 10% 0%, rgba(197, 161, 90, 0.18), transparent 34%);
  border-color: #ead8bd;
  display: grid;
  gap: 16px;
}

.custom-card h3 {
  color: #102b24;
  font-family: Georgia, "Times New Roman", "Songti SC", serif;
  font-size: 22px;
  margin: 0;
}

.option-group {
  display: grid;
  gap: 10px;
}

.option-group > span {
  color: #0e7a55;
  font-size: 13px;
  font-weight: 900;
}

.option-group div {
  display: flex;
  flex-wrap: wrap;
  gap: 9px;
}

.option-group button {
  background:
    linear-gradient(180deg, #ffffff 0%, #fff8ed 100%);
  border: 1px solid #e3cda7;
  border-radius: 999px;
  box-shadow: 0 6px 16px rgba(24, 34, 29, 0.06);
  color: #31423a;
  font-size: 13px;
  font-weight: 900;
  min-height: 40px;
  padding: 0 16px;
  transition:
    background 0.18s ease,
    border-color 0.18s ease,
    box-shadow 0.18s ease,
    color 0.18s ease,
    transform 0.18s ease;
}

.option-group button.active {
  background:
    linear-gradient(135deg, #103f34 0%, #0e7a55 100%);
  border-color: #0e7a55;
  box-shadow: 0 10px 22px rgba(14, 122, 85, 0.24);
  color: #ffffff;
  transform: translateY(-1px);
}

.option-group button.active::after {
  content: "";
  background: rgba(255, 255, 255, 0.55);
  border-radius: 999px;
  display: inline-block;
  height: 6px;
  margin-left: 8px;
  width: 6px;
}

.qty-row {
  align-items: center;
  display: flex;
  font-weight: 900;
  justify-content: space-between;
}

.stepper {
  align-items: center;
  background: #fbf7ee;
  border-radius: 999px;
  display: flex;
  gap: 18px;
  padding: 4px;
}

.stepper button {
  background: #ffffff;
  border-radius: 999px;
  color: #103f34;
  font-size: 22px;
  height: 34px;
  width: 34px;
}

.add-btn {
  width: 100%;
}
</style>
