<template>
  <div class="page-search">
    <div class="columns is-multiline">
      <div class="column is-12">
        <h1 class="title">Search</h1>
        <h2 class="is-size-5 has-text-grey">
          Search term: "{{search}}"
        </h2>
      </div>
      <div v-if="products.length > 0" class="column is-12">
        <ProductBox
            v-for="product in products"
            v-bind:key="product.id"
            v-bind:product="product"
        />
      </div>
      <div v-else class="column is-12 has-text-centered">
        <p v-if="search && !isLoading" class="has-text-grey">No products found for "{{search}}".</p>
      </div>
    </div>
  </div>
</template>

<script>
import axios from "axios";
import ProductBox from "@/components/ProductBox";
import {toast} from "bulma-toast";
export default {
  name: "SearchView",
  components: {
    ProductBox
  },

  data(){
    return{
      products:[],
      search: '',
      isLoading: false
    }
  },
  mounted() {
    document.title = 'Search'
    let uri = window.location.search.substring(1)
    let params = new URLSearchParams(uri)

    if (params.get('search')){
      this.search = params.get('search').trim()
      if (this.search) {
        this.performSearch()
      }
    }
  },
  methods:{
    performSearch: async function (){
      if (!this.search) return

      this.isLoading = true
      this.products = []

      try {
        const response = await axios.get(`api/v1/products/?search=${encodeURIComponent(this.search)}`)
        this.products = response.data.results || []
        if (response.data.is_empty) {
          console.log('Empty search results state detected')
        }
      } catch(error ){
        console.log(error)
        toast({
          message: 'Something went wrong, Please try again.',
          type: 'is-danger',
          dismissible:true,
          pauseOnHover:true,
          duration:2000,
          position:'bottom-right',
        })
      }

      this.isLoading = false

    }
  }
}
</script>