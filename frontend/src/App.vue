<template>
  <div class="desktop-stage">
    <div
      class="phone-shell"
      :class="{
        'merchant-shell': isMerchantLayout,
        'delivery-shell': isDeliveryLayout,
        'platform-shell': isPlatformLayout,
        'no-nav-shell': !showBottomNav,
      }"
    >
      <main ref="pageRef" class="page" @scroll.passive="handlePageScroll">
        <RouterView />
      </main>

      <button v-if="showBackTop" class="back-top-btn" type="button" aria-label="返回顶部" @click="scrollToTop">
        ↑
      </button>

      <nav v-if="showMerchantNav" class="bottom-nav merchant-nav">
        <RouterLink to="/merchant/home" aria-label="商家工作台">
          <svg viewBox="0 0 24 24" aria-hidden="true">
            <path d="M4 10.5 12 4l8 6.5v8.8a1.4 1.4 0 0 1-1.4 1.4H5.4A1.4 1.4 0 0 1 4 19.3v-8.8Z" />
            <path d="M8 20v-6h8v6" />
          </svg>
          <strong>工作台</strong>
        </RouterLink>
        <RouterLink to="/merchant/inventory" aria-label="商家进货">
          <svg viewBox="0 0 24 24" aria-hidden="true">
            <path d="M5 7.5h14l-1.2 12H6.2L5 7.5Z" />
            <path d="M8 7.5a4 4 0 0 1 8 0" />
            <path d="M12 11v5" />
            <path d="M9.5 13.5h5" />
          </svg>
          <strong>进货</strong>
        </RouterLink>
        <RouterLink to="/merchant/orders" aria-label="商家接单">
          <svg viewBox="0 0 24 24" aria-hidden="true">
            <path d="M6 4h12v18l-3-1.8-3 1.8-3-1.8L6 22V4Z" />
            <path d="M9 8h6" />
            <path d="M9 12h6" />
            <path d="M9 16h4" />
          </svg>
          <strong>接单</strong>
        </RouterLink>
      </nav>

      <nav v-else-if="showCustomerNav" class="bottom-nav">
        <RouterLink to="/home" aria-label="首页">
          <svg viewBox="0 0 24 24" aria-hidden="true">
            <path d="M3.5 10.8 12 3.6l8.5 7.2v9.1a1.4 1.4 0 0 1-1.4 1.4H5.9a1.4 1.4 0 0 1-1.4-1.4v-9.1Z" />
            <path d="M9.2 21.3v-6.5h5.6v6.5" />
          </svg>
          <strong>首页</strong>
        </RouterLink>
        <RouterLink to="/dishes" aria-label="点单">
          <svg viewBox="0 0 24 24" aria-hidden="true">
            <path d="M7.3 3.5h9.4l-.9 16.6a1.7 1.7 0 0 1-1.7 1.6H9.9a1.7 1.7 0 0 1-1.7-1.6L7.3 3.5Z" />
            <path d="M6.4 7h11.2" />
            <path d="M10 11.1h4" />
          </svg>
          <strong>点单</strong>
        </RouterLink>
        <RouterLink to="/cart" aria-label="购物车">
          <svg viewBox="0 0 24 24" aria-hidden="true">
            <path d="M7.5 8.2h13l-1.2 7.1a2 2 0 0 1-2 1.7H9.8a2 2 0 0 1-2-1.6L6.5 4.7H3.7" />
            <circle cx="10" cy="20" r="1.3" />
            <circle cx="17.5" cy="20" r="1.3" />
          </svg>
          <strong>购物车</strong>
        </RouterLink>
        <RouterLink to="/orders" aria-label="订单">
          <svg viewBox="0 0 24 24" aria-hidden="true">
            <path d="M6.2 3.8h11.6v18l-2.4-1.4-2.4 1.4-2.4-1.4-2.4 1.4v-18Z" />
            <path d="M9.2 8.2h5.8" />
            <path d="M9.2 12h5.8" />
            <path d="M9.2 15.8h3.4" />
          </svg>
          <strong>订单</strong>
        </RouterLink>
        <RouterLink to="/profile" aria-label="我的">
          <svg viewBox="0 0 24 24" aria-hidden="true">
            <circle cx="12" cy="7.8" r="4.1" />
            <path d="M4.6 21.2a7.4 7.4 0 0 1 14.8 0" />
          </svg>
          <strong>我的</strong>
        </RouterLink>
      </nav>
    </div>
  </div>
</template>

<script setup>
import { computed, nextTick, ref, watch } from "vue";
import { useRoute } from "vue-router";

const route = useRoute();
const pageRef = ref(null);
const showBackTop = ref(false);
const lastScrollTop = ref(0);
const isMerchantLayout = computed(() => Boolean(route.meta.merchantLayout));
const isDeliveryLayout = computed(() => Boolean(route.meta.deliveryLayout));
const isPlatformLayout = computed(() => Boolean(route.meta.platformLayout));
const showMerchantNav = computed(() => isMerchantLayout.value && route.name !== "merchant-login");
const showCustomerNav = computed(() => !isMerchantLayout.value && !isDeliveryLayout.value && !isPlatformLayout.value);
const showBottomNav = computed(() => showMerchantNav.value || showCustomerNav.value);

function handlePageScroll(event) {
  const target = event.target;
  const currentTop = target.scrollTop;
  const isScrollingUp = currentTop < lastScrollTop.value;
  showBackTop.value = currentTop > target.clientHeight && isScrollingUp;
  lastScrollTop.value = Math.max(currentTop, 0);
}

function scrollToTop() {
  pageRef.value?.scrollTo({ top: 0, behavior: "smooth" });
  showBackTop.value = false;
}

watch(
  () => route.fullPath,
  async () => {
    await nextTick();
    pageRef.value?.scrollTo({ top: 0 });
    lastScrollTop.value = 0;
    showBackTop.value = false;
  },
);
</script>
