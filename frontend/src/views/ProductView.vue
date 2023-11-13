<template>
  <div class="page-product">
    <div class="columns is-multiline">
      <div class="column is-9">
        <h1 class="title">{{product.title}}</h1>
        <figure class="image mb-6">
          <Carousel v-if="Slides">
            <Slide v-for="(slide, id) in Slides" :key="id">
              <img :src="slide.image" alt="thumbnail for product" width="450" height="450">
            </Slide>

            <template #addons="{ slidesCount }">
              <Pagination/>
              <Navigation v-if="slidesCount > 1" />
            </template>
          </Carousel>
        </figure>
        
      </div>
      <div class="column is-3">
        <h2 class="subtitle">Information</h2>
        <p><strong>Price: </strong>{{product.price}}</p>
        <div class="field has-addons mb-4">
          <div class="control">
            <input type="number" class="input" min="1" v-model="quantity">
          </div>
          <div class="control">
            <a class="button is-dark" @click="addToCart(quantity, product)">Add to cart</a>
          </div>
        </div>
        <p><strong>Description: </strong>{{product.description}}</p>
      </div>
    </div>
  </div>
</template>

<script>
import axios from "axios";
import 'vue3-carousel/dist/carousel.css';
import { Carousel, Slide, Pagination, Navigation } from 'vue3-carousel';
import MixinFunctions from "@/components/MixinFunctions";

export default {
  name: "ProductView",
  mixins: [MixinFunctions],
  data(){
    return{
      product:[],
      Slides: null,
      quantity: 1
    }
  },
  methods:{
     getProduct : async function (){
      this.$store.commit('setIsLoading', true)
      const product_slug = this.$route.params.product_slug

      await axios.get(`/api/v1/products/${product_slug}`).then(
          response => {
            this.product = response.data
            this.Slides = this.product.images
            document.title = this.product.title
          }
      ).catch( error =>{
        console.log(error)
      })
      this.$store.commit('setIsLoading', false)

    }
  },
  mounted() {
    this.getProduct()
  },
  components: {
    Carousel,
    Slide,
    Pagination,
    Navigation,
  }
}


</script>

<style scoped>
.image img {
  width: unset;
}
</style>