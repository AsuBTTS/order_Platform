<template>
  <section class="platform-login">
    <div class="platform-login-hero">
      <img src="/logo.png" alt="花神咖啡馆" />
      <p class="eyebrow">Platform Console</p>
      <h2>平台管理端</h2>
      <p>管理用户、订单报表和优惠券运营。</p>
    </div>

    <form class="card platform-login-card" @submit.prevent="handleLogin">
      <div class="field">
        <label for="platformUsername">管理员账号</label>
        <input id="platformUsername" v-model="form.username" autocomplete="username" />
      </div>
      <div class="field">
        <label for="platformPassword">密码</label>
        <input id="platformPassword" v-model="form.password" autocomplete="current-password" type="password" />
      </div>
      <button class="primary-btn login-btn" :disabled="loading" type="submit">
        {{ loading ? "登录中..." : "进入平台端" }}
      </button>
      <p v-if="error" class="danger-text">{{ error }}</p>
      <p class="hint">测试账号：admin / 123456</p>
    </form>
  </section>
</template>

<script setup>
import { reactive, ref } from "vue";
import { useRoute, useRouter } from "vue-router";

import { loginPlatformAdmin } from "../api/platform";
import { setStoredPlatformAdmin } from "../utils/session";

const router = useRouter();
const route = useRoute();
const form = reactive({
  username: "admin",
  password: "123456",
});
const loading = ref(false);
const error = ref("");

async function handleLogin() {
  loading.value = true;
  error.value = "";

  try {
    const { data } = await loginPlatformAdmin(form);
    if (!data.user.is_staff && !data.user.is_superuser) {
      error.value = "请使用平台管理员账号登录。";
      return;
    }
    setStoredPlatformAdmin(data.user);
    router.push(route.query.redirect || "/platform/dashboard");
  } catch (err) {
    error.value = err.message;
  } finally {
    loading.value = false;
  }
}
</script>

<style scoped>
.platform-login {
  display: grid;
  gap: 18px;
}

.platform-login-hero {
  background:
    linear-gradient(135deg, rgba(16, 63, 52, 0.92), rgba(16, 63, 52, 0.46)),
    url("/hero.png") center / cover;
  border-radius: 30px;
  color: #ffffff;
  display: grid;
  min-height: 330px;
  padding: 24px;
}

.platform-login-hero img {
  background: rgba(255, 255, 255, 0.92);
  border-radius: 999px;
  height: 72px;
  object-fit: cover;
  width: 72px;
}

.platform-login-hero h2 {
  font-family: Georgia, "Times New Roman", "Songti SC", serif;
  font-size: 40px;
  line-height: 1.05;
  margin: 88px 0 10px;
}

.platform-login-hero .eyebrow,
.platform-login-hero p {
  color: rgba(255, 255, 255, 0.9);
  margin-bottom: 0;
}

.platform-login-card {
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
