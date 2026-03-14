export const categoryColors = {
  Food: "#FF6B35",
  Transport: "#00D4FF",
  Utilities: "#F59E0B",
  Entertainment: "#8B5CF6",
  Shopping: "#EC4899",
  Healthcare: "#10B981",
  Transfers: "#64748B",
  Income: "#00FFB3",
  Other: "#94A3B8",
};

export const fmt = (amount, currency) => {
  const symbol = currency === "INR" ? "₹" : "$";
  return `${symbol}${Number(amount).toLocaleString("en-IN", { maximumFractionDigits: 0 })}`;
};
