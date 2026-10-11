<template>
  <div class="page-category">
    <h2 class="is-size-2 has-text-centered">{{category.name}}</h2>
    <div class="columns is-multiline">
      <div class="column is-12" v-if="error">
        <div class="notification is-danger is-light">
          <button class="delete" @click="error = false"></button>
          Something went wrong, Please try again.
        </div>
      </div>
      <div class="column is-12 has-text-centered" v-else-if="!products.length">
        <p class="is-size-5 has-text-grey">
          {{search ? `No products in this category match "${search}".` : 'There are no products in this category yet.'}}
        </p>
      </div>
      <ProductBox
          v-for="product in products"
          v-bind:key="product.id"
          v-bind:product="product"
      />
    </div>
    <MyPagination v-if="products.length" @get-results="(path_param) => getCategory(path_param)"
                  :count="count" :previous="previous" :next="next" :page="page" :default-api-get="defaultApiGet" />
  </div>
</template>

<script>
import axios from "axios";
import {toast} from "bulma-toast";
import ProductBox from "@/components/ProductBox";
import MyPagination from "@/components/MyPagination";
export default {
  name: 'CategoryView',
  data(){
    return{
      category:{},
      products:[],
      count: 0,
      next: null,
      previous: null,
      page: 1,
      search: '',
      error: false,
      defaultApiGet: ''
  }
  },
  components:{
    ProductBox,
    MyPagination
  },
  mounted() {
    this.getCategory()
  },
  watch:{
    $route(to){
      if (to.name === "category"){
          this.page = 1
          this.getCategory()
      }
    }
  },
  methods:{
    getCategory: async function (path_param=null){
      const categorySlug = this.$route.params.category_slug
      let path_url
      if (path_param) {
        // next/previous arrive as absolute API links; strip the origin so axios
        // keeps resolving them against the configured baseURL
        path_url = path_param.replace(/^https?:\/\/[^/]+/, '')
      } else {
        this.search = (this.$route.query.search || '').trim()
        this.defaultApiGet = `api/v1/categories/${categorySlug}/` + (this.search ? `?search=${encodeURIComponent(this.search)}` : '')
        path_url = this.defaultApiGet
      }
      if (path_url.includes('page=')) {
        this.page = parseInt(path_url.split('page=')[1]) || 1
      }

      this.$store.commit('setIsLoading', true)
      this.error = false
      await axios.get(path_url).then(response =>{
        const data = response.data || {}
        this.category = data.category || {}
        const products = data.products || {}
        this.products = products.results || []
        this.count = products.count || 0
        this.next = products.next || null
        this.previous = products.previous || null
        document.title = this.category.name || 'Category'

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