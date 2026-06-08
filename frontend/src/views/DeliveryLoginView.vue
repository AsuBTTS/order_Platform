<template>
  <section class="driver-login">
    <div class="driver-login-hero">
      <div class="online-pill">骑手端</div>
      <h2>花神配送</h2>
      <p>登录后接单、取餐、配送和完成订单。</p>
    </div>

    <form class="card driver-login-card" @submit.prevent="handleLogin">
      <div class="field">
        <label for="driverUsername">骑手账号</label>
        <input id="driverUsername" v-model="form.username" autocomplete="username" />
      </div>
      <div class="field">
        <label for="driverPassword">密码</label>
        <input id="driverPassword" v-model="form.password" autocomplete="current-password" type="password" />
      </div>
      <button class="rider-btn" :disabled="loading" type="submit">
        {{ loading ? "登录中..." : "进入骑手端" }}
      </button>
      <p v-if="error" class="danger-text">{{ error }}</p>
      <p class="hint">测试账号：driver / 123456</p>
    </form>
  </section>
</template>

<script setup>
import { reactive, ref } from "vue";
import { useRoute, useRouter } from "vue-router";

import { loginDriver } from "../api/delivery";
import { setStoredDriver } from "../utils/session";

const router = useRouter();
const route = useRoute();
const form = reactive({
  username: "driver",
  password: "123456",
});
const loading = ref(false);
const error = ref("");

async function handleLogin() {
  loading.value = true;
  error.value = "";

  try {
    const { data } = await loginDriver(form);
    if (data.user.role !== "driver") {
      error.value = "请使用 driver 角色账号登录。";
      return;
    }
    setStoredDriver(data.user);
    router.push(route.query.redirect || "/delivery/orders");
  } catch (err) {
    error.value = err.message;
  } finally {
    loading.value = false;
  }
}
</script>

<style scoped>
.driver-login {
  display: grid;
  gap: 18px;
}

.driver-login-hero {
  align-content: end;
  background:
    linear-gradient(180deg, rgba(16, 63, 52, 0.08), rgba(16, 63, 52, 0.72)),
    url("/hero.png") center / cover;
  border-radius: 30px;
  color: #ffffff;
  display: grid;
  min-height: 360px;
  padding: 24px;
}

.online-pill {
  align-self: start;
  background: #dfeee7;
  border-radius: 999px;
  color: #103f34;
  display: inline-flex;
  font-size: 13px;
  font-weight: 900;
  padding: 7px 12px;
  width: max-content;
}

.driver-login-hero h2 {
  font-size: 42px;
  line-height: 1;
  margin: 130px 0 10px;
}

.driver-login-hero p {
  color: rgba(255, 255, 255, 0.88);
  line-height: 1.5;
  margin: 0;
}

.driver-login-card {
  padding: 18px;
}

.rider-btn {
  background: #103f34;
  border-radius: 999px;
  color: #ffffff;
  font-weight: 900;
  min-height: 48px;
  width: 100%;
}

.hint {
  color: #778079;
  font-size: 13px;
  margin: 12px 0 0;
}
</style>
