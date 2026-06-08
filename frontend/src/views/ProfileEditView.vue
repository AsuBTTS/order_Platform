<template>
  <section class="profile-edit-view">
    <header class="top-bar">
      <div>
        <p class="eyebrow">Profile</p>
        <h2 class="title">修改用户信息</h2>
      </div>
      <RouterLink class="ghost-btn" to="/profile">返回</RouterLink>
    </header>

    <section class="card edit-card">
      <div class="avatar-row">
        <img src="/logo.png" alt="花神咖啡馆" />
        <div>
          <strong>{{ user?.username }}</strong>
          <span>保存后会同步到后端用户资料</span>
        </div>
      </div>

      <div class="field">
        <label for="username">昵称</label>
        <input id="username" v-model="form.username" placeholder="请输入昵称" />
      </div>
      <div class="field">
        <label for="phone">手机号</label>
        <input id="phone" v-model="form.phone" placeholder="请输入手机号" />
      </div>

      <button class="primary-btn" :disabled="saving" @click="saveProfile">
        {{ saving ? "保存中..." : "保存信息" }}
      </button>
      <p v-if="error" class="danger-text">{{ error }}</p>
      <p v-if="message" class="success-text">{{ message }}</p>
    </section>
  </section>
</template>

<script setup>
import { reactive, ref } from "vue";

import { updateProfile } from "../api/customer";
import { getStoredUser, updateStoredUser } from "../utils/session";

const user = ref(getStoredUser());
const saving = ref(false);
const error = ref("");
const message = ref("");
const form = reactive({
  username: user.value?.username || "",
  phone: user.value?.phone || "",
});

async function saveProfile() {
  error.value = "";
  message.value = "";
  const username = form.username.trim();
  if (!username) {
    error.value = "昵称不能为空。";
    return;
  }

  saving.value = true;
  try {
    const { data } = await updateProfile(user.value.id, {
      username,
      phone: form.phone.trim(),
    });
    user.value = updateStoredUser(data.user);
    message.value = "用户信息已更新。";
  } catch (err) {
    error.value = err.message;
  } finally {
    saving.value = false;
  }
}
</script>

<style scoped>
.profile-edit-view {
  display: grid;
  gap: 16px;
}

.edit-card {
  display: grid;
  gap: 14px;
  padding: 18px;
}

.avatar-row {
  align-items: center;
  display: grid;
  gap: 14px;
  grid-template-columns: 64px 1fr;
  margin-bottom: 4px;
}

.avatar-row img {
  border: 1px solid #efe4d4;
  border-radius: 999px;
  height: 64px;
  object-fit: cover;
  width: 64px;
}

.avatar-row div {
  display: grid;
  gap: 5px;
}

.avatar-row strong {
  color: #1c2c25;
  font-size: 20px;
}

.avatar-row span {
  color: #738078;
  font-size: 13px;
  font-weight: 800;
}

.primary-btn {
  width: 100%;
}
</style>
