<template>
  <div class="home">
    <section class="hero mb-6 hero-custom">
      <div class="hero-body">
        <div class="container">
          <div class="columns is-vcentered">
            <div class="column is-6 hero-text-col">
              <span class="tag is-info is-light is-rounded mb-4 premium-badge">
                <span class="icon is-small mr-1"><i class="fas fa-bolt"></i></span>
                Next-Gen Lifestyle
              </span>
              <h1 class="title is-1 has-text-white mb-4 is-spaced hero-title">
                Elevate Your <br/>
                <span class="text-gradient">Digital Reality.</span>
              </h1>
              <p class="subtitle is-5 has-text-grey-light mb-6 hero-subtitle">
                Experience unparalleled aesthetics and premium performance. Step into the future of curated excellence.
              </p>
              <div class="buttons">
                <button class="button is-primary is-medium shop-now-btn">
                  <span>Start Exploring</span>
                  <span class="icon"><i class="fas fa-arrow-right"></i></span>
                </button>
              </div>
            </div>
            <div class="column is-6 is-hidden-mobile">
              <div class="hero-image-wrapper">
                <div class="glowing-backdrop"></div>
                <img src="https://images.unsplash.com/photo-1550745165-9bc0b252726f?auto=format&fit=crop&q=80&w=1480" alt="Futuristic Setup" class="hero-floating-image" />
                <div class="glass-card-floating top-right">
                  <span class="icon has-text-warning"><i class="fas fa-star"></i></span>
                  <div>
                    <p class="has-text-weight-bold has-text-white">5.0/5</p>
                    <p class="is-size-7 has-text-grey-light">Top Rated</p>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </section>

    <div class="container mt-6 px-4" ref="productSection">
      <div class="columns is-multiline">
        <div class="column is-12 text-center-mobile">
          <h2 class="is-size-3 has-text-weight-bold mb-5 section-title">Trending Now</h2>
        </div>
      <ProductBox
          v-for="product in products"
          v-bind:key="product.id"
          v-bind:product="product"
      />
    </div>
    <MyPagination @get-results="(path_param) => getProducts(path_param)" :count="count" :previous="previous" :next="next" :page="page" :default-api-get="defaultApiGet" />
    </div>
  </div>
</template>

<script>
import axios from 'axios'
import ProductBox from "@/components/ProductBox";
import MyPagination from "@/components/MyPagination";

export default {
  name: 'HomeView',
  data(){
    return {
      products:[],
      count: 0,
      next: null,
      previous: null,
      page: 1,
      pageSize: 20,
      defaultApiGet: '/api/v1/products'
    }
  },
  components: {
    ProductBox,
    MyPagination
  },
  mounted() {
    this.getProducts()
    document.title = "Home | iShop"
  },
  methods: {
    getProducts: async function(path_param=null){
      this.$store.commit('setIsLoading', true)
      let path_url = '/api/v1/products'
      if (path_param) {
        path_url = '/api' + path_param.split('/api')[1]
      }
      if (path_url.includes('page=')) {
        this.page = parseInt(path_url.split('page=')[1])
      } else {
        this.page = 1
      }
      await axios.get(path_url).then(response =>{
        this.products = response.data.results
        this.count = response.data.count
        this.next = response.data.next
        this.previous = response.data.previous
        
        // Smooth scroll to product section if it exists
        if (this.$refs.productSection) {
          const y = this.$refs.productSection.getBoundingClientRect().top + window.scrollY - 100;
          window.scrollTo({ top: y, behavior: 'smooth' });
        }
      }).catch(error =>{
        console.log(error)
      })
      this.$store.commit('setIsLoading', false)
    }
  }
}
</script>

<style scoped>
.hero-custom {
  position: relative;
  border-radius: 32px;
  overflow: hidden;
  background: rgba(255, 255, 255, 0.02);
  border: 1px solid rgba(255, 255, 255, 0.05);
  backdrop-filter: blur(10px);
  margin-top: 1rem;
  padding: 2rem 0;
}

.hero-text-col {
  padding-right: 3rem;
  z-index: 2;
}

.premium-badge {
  font-weight: 600;
  letter-spacing: 1px;
  background: rgba(6, 182, 212, 0.1) !important;
  color: #06b6d4 !important;
  border: 1px solid rgba(6, 182, 212, 0.3);
  padding: 0.5rem 1rem;
}

.hero-title {
  font-weight: 900;
  letter-spacing: -1.5px;
  line-height: 1.1;
  font-size: 4.5rem;
}

.text-gradient {
  background: linear-gradient(135deg, #00F0FF 0%, #a855f7 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  font-style: normal;
}

.hero-subtitle {
  font-weight: 400;
  line-height: 1.6;
  max-width: 450px;
}

.shop-now-btn {
  padding: 0 2.5rem;
  font-size: 1.1rem;
}

.hero-image-wrapper {
  position: relative;
  display: flex;
  justify-content: center;
  align-items: center;
}

.glowing-backdrop {
  position: absolute;
  width: 100%;
  height: 100%;
  background: radial-gradient(circle, rgba(99,102,241,0.4) 0%, rgba(0,0,0,0) 70%);
  filter: blur(40px);
  z-index: 0;
}

.hero-floating-image {
  max-width: 85%;
  border-radius: 24px;
  box-shadow: 0 25px 50px -12px rgba(0, 0, 0, 0.5);
  border: 1px solid rgba(255,255,255,0.1);
  animation: float 6s ease-in-out infinite;
  transform: perspective(1000px) rotateY(-5deg);
  z-index: 1;
}

.glass-card-floating {
  position: absolute;
  background: rgba(17, 24, 39, 0.8);
  backdrop-filter: blur(12px);
  border: 1px solid rgba(255, 255, 255, 0.1);
  padding: 1rem 1.5rem;
  border-radius: 16px;
  display: flex;
  align-items: center;
  gap: 12px;
  box-shadow: 0 10px 25px -5px rgba(0, 0, 0, 0.5);
  animation: float 5s ease-in-out infinite reverse;
  z-index: 2;
}

.glass-card-floating.top-right {
  top: -20px;
  right: 0px;
}

@keyframes float {
  0% { transform: translateY(0px) perspective(1000px) rotateY(-5deg); }
  50% { transform: translateY(-15px) perspective(1000px) rotateY(-5deg); }
  100% { transform: translateY(0px) perspective(1000px) rotateY(-5deg); }
}

.section-title {
  font-weight: 800;
  letter-spacing: -0.5px;
  color: #fff;
  position: relative;
  display: inline-block;
  padding-bottom: 0.5rem;
}
.section-title::after {
  content: '';
  position: absolute;
  bottom: 0;
  left: 0;
  width: 40px;
  height: 4px;
  border-radius: 2px;
  background: linear-gradient(90deg, #00F0FF, #6366F1);
}
</style>
