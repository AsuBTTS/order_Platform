<template>
  <section class="home-view">
    <div class="hero-panel">
      <div class="brand-row">
        <img src="/logo.png" alt="花神咖啡馆" />
        <span>花神咖啡馆</span>
      </div>
      <h1>一杯花香，一点从容</h1>
      <p>手作咖啡与茶饮，适合今天的每一次停留。</p>
    </div>

    <button class="card member-strip" type="button" @click="showStores = !showStores">
      <div>
        <span>当前门店</span>
        <strong>{{ selectedStore?.store_name || "正在选择最近门店" }}</strong>
        <em>{{ selectedStore?.store_address || locationHint }}</em>
      </div>
      <b>{{ selectedDistanceText }}</b>
    </button>

    <section v-if="showStores" class="card store-panel">
      <div class="store-head">
        <strong>选择门店</strong>
        <button class="ghost-btn" type="button" @click="detectLocation">重新定位</button>
      </div>
      <p v-if="locationHint" class="muted">{{ locationHint }}</p>
      <button
        v-for="store in sortedStores"
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
        <b>{{ formatDistance(store) }}</b>
      </button>
    </section>

    <div class="entry-grid">
      <button class="entry-card pickup" @click="choose('self_pickup')">
        <span class="entry-icon">⌂</span>
        <strong>到店自取</strong>
        <em>到店取餐更从容</em>
      </button>
      <button class="entry-card delivery" @click="choose('delivery')">
        <span class="entry-icon">↗</span>
        <strong>配送到家</strong>
        <em>附近区域可配送</em>
      </button>
    </div>

    <section class="card coupon-card">
      <div class="coupon-art">7折</div>
      <div>
        <p class="eyebrow">惊喜好礼</p>
        <h2>手工调制饮品券</h2>
        <span>下单时可使用，今日推荐先从菜单开始。</span>
      </div>
    </section>

    <section>
      <div class="section-head">
        <h2>今日推荐</h2>
        <RouterLink to="/dishes">查看菜单</RouterLink>
      </div>
      <div class="recommend-grid">
        <article class="recommend-card">
          <img src="/hero.png" alt="咖啡与茶" />
          <strong>花神拿铁</strong>
          <span>柔和奶香，浅焙咖啡。</span>
        </article>
        <article class="recommend-card">
          <img src="/logo.png" alt="花神咖啡馆标志" />
          <strong>花茶轻饮</strong>
          <span>清爽茶香，适合午后。</span>
        </article>
      </div>
    </section>
  </section>
</template>

<script setup>
import { computed, onMounted, ref } from "vue";
import { useRouter } from "vue-router";

import { fetchStores } from "../api/customer";
import { distanceKm, nearestStore, requestCurrentLocation } from "../utils/location";
import {
  getSelectedStore,
  getUserLocation,
  setFulfillmentType,
  setSelectedStore,
  setUserLocation,
} from "../utils/session";

const router = useRouter();
const stores = ref([]);
const selectedStore = ref(getSelectedStore());
const userLocation = ref(getUserLocation());
const locationHint = ref("");
const showStores = ref(false);

const sortedStores = computed(() =>
  [...stores.value].sort((a, b) => {
    const aDistance = distanceKm(userLocation.value, a) ?? Number.MAX_SAFE_INTEGER;
    const bDistance = distanceKm(userLocation.value, b) ?? Number.MAX_SAFE_INTEGER;
    return aDistance - bDistance;
  }),
);

const selectedDistanceText = computed(() => {
  if (!selectedStore.value) return "选择";
  return formatDistance(selectedStore.value);
});

function formatDistance(store) {
  const distance = distanceKm(userLocation.value, store);
  if (distance === null) return "门店";
  if (distance < 1) return `${Math.round(distance * 1000)}m`;
  return `${distance.toFixed(1)}km`;
}

function selectStore(store) {
  if (!store) {
    return;
  }
  selectedStore.value = store;
  setSelectedStore(store);
  showStores.value = false;
}

async function loadStores() {
  const { data } = await fetchStores();
  stores.value = data.stores;
  if (!selectedStore.value || !stores.value.some((store) => store.id === selectedStore.value.id)) {
    const nearest = nearestStore(stores.value, userLocation.value);
    if (nearest) {
      selectStore(nearest);
    }
  }
}

async function detectLocation() {
  locationHint.value = "正在获取当前位置...";
  try {
    const location = await requestCurrentLocation();
    userLocation.value = location;
    setUserLocation(location);
    locationHint.value = "已根据当前位置选择最近门店。";
    const nearest = nearestStore(stores.value, location);
    if (nearest) {
      selectStore(nearest);
    }
  } catch (err) {
    locationHint.value = err.message;
  }
}

function choose(type) {
  setFulfillmentType(type);
  router.push("/dishes");
}

onMounted(async () => {
  await loadStores();
  await detectLocation();
});
</script>

<style scoped>
.home-view {
  display: grid;
  gap: 16px;
}

.hero-panel {
  background:
    linear-gradient(180deg, rgba(16, 63, 52, 0.1), rgba(16, 63, 52, 0.58)),
    url("/hero.png") center / cover;
  border-radius: 30px;
  color: #ffffff;
  display: flex;
  flex-direction: column;
  justify-content: flex-end;
  min-height: 286px;
  overflow: hidden;
  padding: 22px;
}

.brand-row {
  align-items: center;
  background: rgba(255, 255, 255, 0.92);
  border-radius: 999px;
  color: #173f33;
  display: inline-flex;
  font-weight: 900;
  gap: 8px;
  margin-bottom: auto;
  padding: 7px 12px 7px 7px;
  width: fit-content;
}

.brand-row img {
  border-radius: 999px;
  height: 34px;
  width: 34px;
}

.hero-panel h1 {
  font-family: Georgia, "Times New Roman", "Songti SC", serif;
  font-size: 36px;
  letter-spacing: 0;
  line-height: 1.08;
  margin: 58px 0 8px;
}

.hero-panel p {
  color: rgba(255, 255, 255, 0.88);
  margin: 0;
}

.member-strip {
  align-items: center;
  display: flex;
  justify-content: space-between;
  padding: 16px;
  text-align: left;
  width: 100%;
}

.member-strip div {
  display: grid;
  gap: 4px;
  min-width: 0;
}

.member-strip span,
.member-strip em {
  color: #7a827d;
  font-size: 12px;
  font-style: normal;
  font-weight: 800;
}

.member-strip strong {
  font-size: 18px;
}

.member-strip b {
  background: #edf7f2;
  border-radius: 999px;
  color: #0e7a55;
  flex-shrink: 0;
  padding: 7px 10px;
}

.store-panel {
  display: grid;
  gap: 10px;
  padding: 14px;
}

.store-head {
  align-items: center;
  display: flex;
  justify-content: space-between;
}

.store-option {
  align-items: center;
  background: #f8f4ee;
  border: 1px solid transparent;
  border-radius: 16px;
  color: #1c2c25;
  display: grid;
  gap: 10px;
  grid-template-columns: minmax(0, 1fr) auto;
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

.store-option b {
  color: #0e7a55;
}

.entry-grid {
  display: grid;
  gap: 12px;
  grid-template-columns: 1fr 1fr;
}

.entry-card {
  border-radius: 24px;
  color: #17362e;
  display: grid;
  gap: 8px;
  justify-items: start;
  min-height: 136px;
  padding: 18px;
  text-align: left;
}

.entry-card.pickup {
  background: #f6e7d2;
}

.entry-card.delivery {
  background: #dff2ea;
}

.entry-icon {
  align-items: center;
  background: #ffffff;
  border-radius: 18px;
  display: flex;
  font-size: 26px;
  height: 46px;
  justify-content: center;
  width: 46px;
}

.entry-card strong {
  font-size: 20px;
}

.entry-card em {
  color: #62736b;
  font-style: normal;
  line-height: 1.4;
}

.coupon-card {
  align-items: center;
  display: grid;
  gap: 14px;
  grid-template-columns: 74px 1fr;
  padding: 16px;
}

.coupon-art {
  align-items: center;
  background: #c5a15a;
  border-radius: 22px;
  color: #ffffff;
  display: flex;
  font-family: Georgia, "Times New Roman", "Songti SC", serif;
  font-size: 24px;
  font-weight: 900;
  height: 74px;
  justify-content: center;
}

.coupon-card h2,
.section-head h2 {
  font-family: Georgia, "Times New Roman", "Songti SC", serif;
  margin: 0;
}

.coupon-card span {
  color: #7a827d;
  display: block;
  line-height: 1.4;
}

.section-head {
  align-items: center;
  display: flex;
  justify-content: space-between;
  margin: 6px 0 12px;
}

.section-head a {
  color: #0e7a55;
  font-weight: 900;
  text-decoration: none;
}

.recommend-grid {
  display: grid;
  gap: 12px;
  grid-template-columns: repeat(2, minmax(0, 1fr));
}

.recommend-card {
  background: #ffffff;
  border-radius: 22px;
  display: grid;
  gap: 8px;
  overflow: hidden;
  padding-bottom: 12px;
}

.recommend-card img {
  aspect-ratio: 1;
  object-fit: cover;
  width: 100%;
}

.recommend-card strong,
.recommend-card span {
  padding: 0 12px;
}

.recommend-card span {
  color: #7a827d;
  font-size: 13px;
  line-height: 1.4;
}
</style>
