export function money(value) {
  const amount = Number(value || 0);
  return `¥${amount.toFixed(2)}`;
}

export function statusText(status) {
  const map = {
    pending_payment: "待支付",
    paid: "已支付",
    preparing: "制作中",
    waiting_pickup: "待取餐",
    waiting_delivery: "待配送",
    delivering: "配送中",
    completed: "已完成",
    cancelled: "已取消",
  };
  return map[status] || status;
}

export function deliveryText(type) {
  return type === "delivery" ? "外送配送" : "到店自取";
}

export function roleText(role) {
  const map = {
    customer: "顾客",
    merchant: "商家",
    driver: "骑手",
  };
  return map[role] || role;
}
