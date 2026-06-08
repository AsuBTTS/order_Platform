<template>
  <section class="login-view">
    <div class="login-hero">
      <p class="eyebrow">Fresh coffee and tea</p>
      <h2 class="title">今天喝点什么？</h2>
      <p class="muted">登录顾客账号后开始浏览餐品、加入购物车并完成模拟支付。</p>
    </div>

    <form class="card login-card" @submit.prevent="handleLogin">
      <div class="field">
        <label for="username">账号</label>
        <input id="username" v-model="form.username" autocomplete="username" />
      </div>
      <div class="field">
        <label for="password">密码</label>
        <input id="password" v-model="form.password" autocomplete="current-password" type="password" />
      </div>

      <button class="primary-btn login-btn" :disabled="loading" type="submit">
        {{ loading ? "登录中..." : "登录并开始点餐" }}
      </button>

      <RouterLink class="register-link" to="/register">还没有账号？立即注册</RouterLink>

      <p v-if="error" class="danger-text">{{ error }}</p>
      <p v-if="currentUser" class="success-text">
        当前用户：{{ currentUser.username }} / {{ currentUser.role }}
      </p>
    </form>

    <div class="quick-card">
      <span>测试账号</span>
      <strong>customer / 123456</strong>
    </div>
  </section>
</template>

<script setup>
import { reactive, ref } from "vue";
import { useRoute, useRouter } from "vue-router";

import { login } from "../api/customer";
import { getStoredUser, setStoredUser } from "../utils/session";

const router = useRouter();
const route = useRoute();
const form = reactive({
  username: "customer",
  password: "123456",
});
const loading = ref(false);
const error = ref("");
const currentUser = ref(getStoredUser());

async function handleLogin() {
  loading.value = true;
  error.value = "";

  try {
    const { data } = await login(form);
    if (data.user.role !== "customer") {
      error.value = "顾客端请使用 customer 角色账号登录。";
      return;
    }
    setStoredUser(data.user);
    currentUser.value = data.user;
    router.push(route.query.redirect || "/home");
  } catch (err) {
    error.value = err.message;
  } finally {
    loading.value = false;
  }
}
</script>

<style scoped>
.login-view {
  display: grid;
  gap: 18px;
}

.login-hero {
  background:
    radial-gradient(circle at 88% 20%, rgba(255, 255, 255, 0.9), transparent 24%),
    linear-gradient(150deg, #f7e2c5 0%, #d9b17e 55%, #103f34 56%, #103f34 100%);
  border-radius: 28px;
  color: #17362e;
  min-height: 250px;
  padding: 24px;
}

.login-hero .muted {
  color: #34483f;
  max-width: 250px;
}

.login-card {
  display: grid;
  gap: 10px;
  padding: 18px;
}

.login-btn {
  width: 100%;
}

.register-link {
  color: #0e7a55;
  font-weight: 900;
  text-align: center;
  text-decoration: none;
}

.quick-card {
  align-items: center;
  background: #eef7f2;
  border-radius: 18px;
  color: #0e513c;
  display: flex;
  justify-content: space-between;
  padding: 14px 16px;
}
</style>
