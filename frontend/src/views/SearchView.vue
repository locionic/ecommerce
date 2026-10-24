<template>
  <div class="page-search">
    <div class="columns is-multiline">
      <div class="column is-12">
        <h1 class="title">Search</h1>
        <h2 class="is-size-5 has-text-grey">
          Search term: "{{search}}"
        </h2>
      </div>
      <ProductBox
          v-for="product in products"
          v-bind:key="product.id"
          v-bind:product="product"
      />
      <div v-if="searched && products.length === 0" class="column is-12">
        <div class="notification is-warning is-light">
          <p class="has-text-weight-bold is-size-5">No products found matching "{{search}}".</p>
          <div v-if="suggestedTerms && suggestedTerms.length" class="mt-4">
            <p class="has-text-weight-semibold">Suggested search terms:</p>
            <div class="tags mt-2">
              <a
                v-for="term in suggestedTerms"
                :key="term"
                :href="'/search?search=' + encodeURIComponent(term)"
                class="tag is-info is-medium"
              >
                {{term}}
              </a>
            </div>
          </div>
          <div v-if="suggestedCategories && suggestedCategories.length" class="mt-4">
            <p class="has-text-weight-semibold">Suggested categories to explore:</p>
            <div class="tags mt-2">
              <a
                v-for="cat in suggestedCategories"
                :key="cat.id"
                :href="'/' + cat.slug"
                class="tag is-primary is-medium"
              >
                {{cat.name}} ({{cat.count}} items)
              </a>
            </div>
          </div>
        </div>
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
      searched: false,
      suggestedTerms: [],
      suggestedCategories: []
    }
  },
  mounted() {
    document.title = 'Search'
    let uri = window.location.search.substring(1)
    let params = new URLSearchParams(uri)

    if (params.get('search')){
      this.search = params.get('search')
      this.performSearch()
    }
  },
  methods:{
    performSearch: async function (){
      this.$store.commit('setIsLoading', true)

      await axios.get(`api/v1/products/?search=${this.search}`).then(response =>{
        this.products = response.data.results || []
        this.suggestedTerms = response.data.suggested_terms || []
        this.suggestedCategories = response.data.suggested_categories || []
        this.searched = true
      }).catch(error =>{
        console.log(error)
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
