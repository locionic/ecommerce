<template>
  <div
      ref="scrollTopButton"
      class="fixed w-full flex justify-end bottom-40 pb-3 pr-5 transition z-5"
      style="width: max-content; right: 0;"
  >
      <div
          class="text-gray-400 hover:text-blue-400 transition"
          style="width: max-content;"
      >
          <button @click="scrollToTop" class="button is-rounded is-primary">
            <i v-if="windowScrollY > 0" class="fa fa-arrow-up"></i>
            <i v-else class="fa fa-arrow-down"></i>
          </button>
      </div>
  </div>
</template>
<script>
    import { defineComponent } from "vue";
 
    export default defineComponent({
        data() {
          return {
            windowScrollY: window.scrollY
          }
        },
        mounted() {
            window.addEventListener("scroll", this.handleScroll);
        },
 
        beforeUnmount() {
            window.removeEventListener("scroll", this.handleScroll);
        },
 
        methods: {
            handleScroll() {
                this.windowScrollY = window.scrollY
            },
            scrollToTop() {
                if (window.scrollY > 0) {
                  window.scrollTo({ top: 0, behavior: "smooth" });
                } else {
                  window.scrollTo({ top: document.body.scrollHeight, behavior: 'smooth' });
                }
            },
        },
    });
</script>
<style scoped>
.sticky {
  position: sticky;
}
.w-full {
  width: 100%;
}
.flex {
  display: flex;
}
.justify-end {
  justify-content: flex-end;
}
.bottom-0 {
  bottom: 0;
}
.bottom-40 {
  bottom: 40px;
}
.transition {
  transition-property: background-color, border-color, color, fill, stroke, opacity, box-shadow, transform;

  transition-timing-function: cubic-bezier(0.4, 0, 0.2, 1);

  transition-duration: 300ms;
}
.visible {
  visibility: visible;
}
.invisible {
  visibility: hidden;
}
.fixed {
  position: fixed;
}
.z-5 {
  z-index: 5;
}
</style>