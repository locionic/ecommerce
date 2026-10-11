<template>
  <div class="page-search">
    <div class="columns is-multiline">
      <div class="column is-12">
        <h1 class="title">Search</h1>
        <h2 v-if="search" class="is-size-5 has-text-grey">
          Search term: "{{search}}"
        </h2>
      </div>
      <div class="column is-12" v-if="error">
        <div class="notification is-danger is-light">
          <button class="delete" @click="error = false"></button>
          Something went wrong, Please try again.
        </div>
      </div>
      <div class="column is-12 has-text-centered" v-else-if="!search">
        <p class="is-size-5 has-text-grey">Enter a search term to find products.</p>
      </div>
      <div class="column is-12 has-text-centered" v-else-if="!products.length">
        <p class="is-size-5 has-text-grey">
          No products match "{{search}}". Try a different term or browse a category.
        </p>
      </div>
      <ProductBox
          v-for="product in products"
          v-bind:key="product.id"
          v-bind:product="product"
      />
    </div>
    <MyPagination v-if="products.length" @get-results="(path_param) => performSearch(path_param)"
                  :count="count" :previous="previous" :next="next" :page="page" :default-api-get="defaultApiGet" />
  </div>
</template>

<script>
import axios from "axios";
import ProductBox from "@/components/ProductBox";
import MyPagination from "@/components/MyPagination";
import {toast} from "bulma-toast";
export default {
  name: "SearchView",
  components: {
    ProductBox,
    MyPagination
  },

  data(){
    return{
      products:[],
      count: 0,
      next: null,
      previous: null,
      page: 1,
      search: '',
      error: false,
      defaultApiGet: 'api/v1/products/?search=' + encodeURIComponent(this.$route.query.search || '')
    }
  },
  mounted() {
    document.title = 'Search'
    this.readSearchTerm()
  },
  watch:{
    $route(){
      this.readSearchTerm()
    }
  },
  methods:{
    readSearchTerm: function (){
      this.search = (this.$route.query.search || '').trim()
      this.defaultApiGet = `api/v1/products/?search=${encodeURIComponent(this.search)}`
      this.error = false
      if (this.search){
        this.page = 1
        this.performSearch()
      } else {
        this.products = []
        this.count = 0
        this.next = null
        this.previous = null
      }
    },
    performSearch: async function (path_param=null){
      let path_url = this.defaultApiGet
      if (path_param) {
        // next/previous arrive as absolute API links; strip the origin so axios
        // keeps resolving them against the configured baseURL
        path_url = path_param.replace(/^https?:\/\/[^/]+/, '')
      }
      if (path_url.includes('page=')) {
        this.page = parseInt(path_url.split('page=')[1]) || 1
      }

      this.$store.commit('setIsLoading', true)
      this.error = false
      await axios.get(path_url).then(response =>{
        const data = response.data || {}
        this.products = data.results || []
        this.count = data.count || 0
        this.next = data.next || null
        this.previous = data.previous || null
      }).catch(error =>{
        console.log(error)
        this.products = []
        this.count = 0
        this.next = null
        this.previous = null
        this.error = true
        toast({
          message: 'Something went wrong, Please try again.',
          type: 'is-danger',
          dismissible:true,
          pauseOnHover:true,
          duration:2000,
          position:'bottom-right',
        })
      })

      this.$store.commit('setIsLoading', false)

    }
  }
}
</script>