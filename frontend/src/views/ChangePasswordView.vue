<template>
  <section class="password-view">
    <header class="top-bar">
      <div>
        <p class="eyebrow">Security</p>
        <h2 class="title">修改密码</h2>
      </div>
      <RouterLink class="ghost-btn" to="/profile">返回</RouterLink>
    </header>

    <section class="card password-card">
      <div class="field">
        <label for="oldPassword">原密码</label>
        <input id="oldPassword" v-model="form.oldPassword" type="password" autocomplete="current-password" />
      </div>
      <div class="field">
        <label for="newPassword">新密码</label>
        <input id="newPassword" v-model="form.newPassword" type="password" autocomplete="new-password" placeholder="至少 6 位" />
      </div>
      <button class="primary-btn" :disabled="submitting" @click="submitPassword">
        {{ submitting ? "修改中..." : "确认修改" }}
      </button>
      <p v-if="error" class="danger-text">{{ error }}</p>
      <p v-if="message" class="success-text">{{ message }}</p>
    </section>
  </section>
</template>

<script setup>
import { reactive, ref } from "vue";

import { changePassword } from "../api/customer";
import { getCustomerId } from "../utils/session";

const submitting = ref(false);
const error = ref("");
const message = ref("");
const form = reactive({
  oldPassword: "",
  newPassword: "",
});

async function submitPassword() {
  error.value = "";
  message.value = "";
  if (form.newPassword.length < 6) {
    error.value = "新密码至少需要 6 位。";
    return;
  }

  submitting.value = true;
  try {
    await changePassword(getCustomerId(), form.oldPassword, form.newPassword);
    form.oldPassword = "";
    form.newPassword = "";
    message.value = "密码已修改，请妥善保存新密码。";
  } catch (err) {
    error.value = err.message;
  } finally {
    submitting.value = false;
  }
}
</script>

<style scoped>
.password-view {
  display: grid;
  gap: 16px;
}

.password-card {
  display: grid;
  gap: 14px;
  padding: 18px;
}

.primary-btn {
  width: 100%;
}
</style>
