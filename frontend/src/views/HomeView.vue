<template>
  <div class="home">
    <section class="hero is-medium mb-6" style="background-image: url(https://websitedemos.net/be-bold-beauty-store-04/wp-content/uploads/sites/1117/2022/08/hero.jpg); border-radius: 1rem;">
      <div class="hero-body has-text-centered">
        <p class="title mb-6">
          Welcome to eCommerce!
        </p>
        <p class="subtitle">
          The online shopping store.
        </p>
      </div>
    </section>
    <div class="columns is-multiline">
      <div class="column is-12">
        <h2 class="is-size-2">Latest products</h2>
      </div>
      <ProductBox
          v-for="product in products"
          v-bind:key="product.id"
          v-bind:product="product"
      />
    </div>
    <MyPagination @get-results="(path_param) => getProducts(path_param)" :count="count" :previous="previous" :next="next" :page="page" :default-api-get="defaultApiGet" />
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
    document.title = "Home | eCommerce"
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
      }).catch(error =>{
        console.log(error)
      })
      this.$store.commit('setIsLoading', false)
    }
  }
}
</script>
