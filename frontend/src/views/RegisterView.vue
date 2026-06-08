<template>
  <section class="register-view">
    <div class="register-hero">
      <img src="/logo.png" alt="花神咖啡馆" />
      <p class="eyebrow">Join Café de Flore</p>
      <h2 class="title">注册顾客账号</h2>
      <p>注册后即可点单、使用优惠券并查看订单。</p>
    </div>

    <form class="card register-card" @submit.prevent="handleRegister">
      <div class="field">
        <label for="newUsername">账号</label>
        <input id="newUsername" v-model="form.username" autocomplete="username" placeholder="请输入账号" />
      </div>
      <div class="field">
        <label for="newPhone">手机号</label>
        <input id="newPhone" v-model="form.phone" inputmode="tel" placeholder="请输入手机号" />
      </div>
      <div class="field">
        <label for="newPassword">密码</label>
        <input id="newPassword" v-model="form.password" autocomplete="new-password" type="password" placeholder="至少 6 位" />
      </div>
      <button class="primary-btn register-btn" :disabled="loading" type="submit">
        {{ loading ? "注册中..." : "注册并登录" }}
      </button>
      <RouterLink class="login-link" to="/login">已有账号，返回登录</RouterLink>
      <p v-if="error" class="danger-text">{{ error }}</p>
    </form>
  </section>
</template>

<script setup>
import { reactive, ref } from "vue";
import { useRouter } from "vue-router";

import { register } from "../api/customer";
import { setStoredUser } from "../utils/session";

const router = useRouter();
const form = reactive({
  username: "",
  phone: "",
  password: "",
});
const loading = ref(false);
const error = ref("");

async function handleRegister() {
  loading.value = true;
  error.value = "";

  try {
    const { data } = await register(form);
    setStoredUser(data.user);
    router.push("/home");
  } catch (err) {
    error.value = err.message;
  } finally {
    loading.value = false;
  }
}
</script>

<style scoped>
.register-view {
  display: grid;
  gap: 18px;
}

.register-hero {
  background:
    linear-gradient(135deg, rgba(255, 255, 255, 0.74), rgba(16, 63, 52, 0.72)),
    url("/hero.png") center / cover;
  border-radius: 30px;
  color: #103f34;
  display: grid;
  min-height: 270px;
  padding: 24px;
}

.register-hero img {
  background: rgba(255, 255, 255, 0.9);
  border-radius: 999px;
  height: 70px;
  object-fit: cover;
  width: 70px;
}

.register-hero p:last-child {
  color: #3a4d45;
  font-weight: 800;
  margin: 0;
  max-width: 260px;
}

.register-card {
  display: grid;
  gap: 10px;
  padding: 18px;
}

.register-btn {
  width: 100%;
}

.login-link {
  color: #0e7a55;
  font-weight: 900;
  text-align: center;
  text-decoration: none;
}
</style>
