<template>
    <div class="progress-circle" :style="circleStyle">
    <span class="progress-value">{{ progress }}%</span>
  </div>
</template>
<script>
export default {
  name: "CircularProgressBar",
  props: {
    progress: {
      type: Number,
      required: true,
      default: 0, // Giá trị phần trăm mặc định
    },
  },
  computed: {
    circleStyle() {
      return {
        background: `conic-gradient(
          #4caf50 0% ${this.progress}%, 
          #ddd ${this.progress}% 100%
        )`,
      };
    },
  },
};
</script>
<style scoped>
.progress-circle {
  position: relative;
  width: 90px;
  height: 90px;
  border-radius: 50%;
  display: flex;
  justify-content: center;
  align-items: center;
  background: conic-gradient(#355ee2 0% 0%, #ddd 0% 100%);
}

.progress-circle::before {
  content: "";
  position: absolute;
  width: 80px;
  height: 80px;
  background: #fff;
  border-radius: 50%;
}

.progress-value {
  position: absolute;
  font-size: 24px;
  font-weight: bold;
  color: #355ee2;
}
</style>