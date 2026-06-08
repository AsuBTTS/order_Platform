<template>
  <section class="merchant-login">
    <div class="login-panel">
      <img src="/logo.png" alt="花神咖啡馆" />
      <p class="eyebrow">Merchant Portal</p>
      <h2 class="title">花神商家端</h2>
      <p class="muted">独立处理进货、库存、接单与制作。</p>
    </div>

    <form class="card login-card" @submit.prevent="handleLogin">
      <div class="field">
        <label for="merchantUsername">商家账号</label>
        <input id="merchantUsername" v-model="form.username" autocomplete="username" />
      </div>
      <div class="field">
        <label for="merchantPassword">密码</label>
        <input id="merchantPassword" v-model="form.password" autocomplete="current-password" type="password" />
      </div>
      <button class="primary-btn login-btn" :disabled="loading" type="submit">
        {{ loading ? "登录中..." : "进入商家端" }}
      </button>
      <p v-if="error" class="danger-text">{{ error }}</p>
      <p class="hint">测试账号：merchant / 123456</p>
    </form>
  </section>
</template>

<script setup>
import { reactive, ref } from "vue";
import { useRoute, useRouter } from "vue-router";

import { loginMerchant } from "../api/merchant";
import { setStoredMerchant } from "../utils/session";

const router = useRouter();
const route = useRoute();
const form = reactive({
  username: "merchant",
  password: "123456",
});
const loading = ref(false);
const error = ref("");

async function handleLogin() {
  loading.value = true;
  error.value = "";

  try {
    const { data } = await loginMerchant(form);
    if (data.user.role !== "merchant") {
      error.value = "请使用 merchant 角色账号登录。";
      return;
    }
    setStoredMerchant(data.user);
    router.push(route.query.redirect || "/merchant/home");
  } catch (err) {
    error.value = err.message;
  } finally {
    loading.value = false;
  }
}
</script>

<style scoped>
.merchant-login {
  display: grid;
  gap: 18px;
}

.login-panel {
  background:
    linear-gradient(180deg, rgba(16, 63, 52, 0.18), rgba(16, 63, 52, 0.78)),
    url("/hero.png") center / cover;
  border-radius: 30px;
  color: #ffffff;
  min-height: 320px;
  padding: 24px;
}

.login-panel img {
  background: rgba(255, 255, 255, 0.92);
  border-radius: 999px;
  height: 72px;
  object-fit: cover;
  width: 72px;
}

.login-panel .eyebrow,
.login-panel .muted {
  color: rgba(255, 255, 255, 0.9);
}

.login-card {
  padding: 18px;
}

.login-btn {
  width: 100%;
}

.hint {
  color: #778079;
  font-size: 13px;
  margin: 12px 0 0;
}
</style>
