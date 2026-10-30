<template>
  <div class="page-category">
    <h2 class="is-size-2 has-text-centered">{{category.name}}</h2>
    <div v-if="products.length > 0" class="columns is-multiline">
      <ProductBox
          v-for="product in products"
          v-bind:key="product.id"
          v-bind:product="product"
      />
    </div>
    <div v-else class="column is-full has-text-centered">
      <p class="has-text-grey">No products found in this category.</p>
    </div>
  </div>
</template>

<script>
import axios from "axios";
import {toast} from "bulma-toast";
import ProductBox from "@/components/ProductBox";
export default {
  name: 'CategoryView',
  data(){
    return{
      category:{},
      products:[],
      isLoading: false
    }
  },
  components:{
    ProductBox
  },
  mounted() {
    this.getCategory()
  },
  watch:{
    $route(to){
      if (to.name === "category"){
          this.getCategory()
      }
    }
  },
  methods:{
    getCategory: async function (){
      const categorySlug = this.$route.params.category_slug
      this.isLoading = true
      this.products = []
      this.category = {}
      try {
        const response = await axios.get(`api/v1/categories/${categorySlug}/`)
        this.category = response.data.category
        this.products = response.data.products.results || []
        document.title = this.category.name ? `${this.category.name} - iShop` : 'Category - iShop'
        if (response.data.products.is_empty) {
          console.log('Empty category state detected')
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