<template>
  <div class="page-product">
    <div class="columns is-multiline">
      <div class="column is-9">
        <h1 class="title">{{product.title}}</h1>
        <figure class="image mb-6">
          <Carousel v-if="Slides" :itemsToShow="2">
            <Slide v-for="(slide, id) in Slides" :key="id">
              <img :src="slide.image" alt="thumbnail for product">
            </Slide>
            <template #addons="{ slidesCount }">
              <Pagination/>
              <Navigation v-if="slidesCount > 1" />
            </template>
          </Carousel>
        </figure>
        <h2 class="subtitle" v-if="product.reviews && product.reviews.length > 0">Reviews</h2>
        <template v-for="(review, index) in product.reviews" :key="index + 'review product'">
          <MediaBox :object-param="review" />
        </template>
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
        <p class="mb-4"><strong>Description: </strong>{{product.description}}</p>
        <div class="dropdown" :class="{'is-active': activeReview}">
          <div class="dropdown-trigger">
            <button class="button is-primary is-outlined" aria-haspopup="true" aria-controls="dropdown-menu3" @click="activeReview = !activeReview">
              <span>Evaluate</span>
              <span class="icon is-small">
                <i class="fas fa-angle-down fa-sm" aria-hidden="true"></i>
              </span>
            </button>
          </div>
          <div class="dropdown-menu" id="dropdown-menu3" role="menu">
            <div class="dropdown-content">
              <div class="field dropdown-item" style="min-width: 30rem;">
                <div class="control has-icons-left has-icons-right mb-1">
                  <input class="input is-small" type="text" placeholder="Leave a message ..." v-model="ratingMessage">
                  <span class="icon is-small is-left">
                    <i class="fa-solid fa-message"></i>
                  </span>
                </div>
                <star-rating v-model:rating="rating" :star-size="15" :show-rating="false" class="mb-1" />
                <p v-if="!validRate" class="help is-danger mb-1 mt-0">Rating is required</p>
                <button class="button is-primary is-small" @click="submitRate">Submit</button>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import axios from "axios";
import 'vue3-carousel/dist/carousel.css';
import { Carousel, Slide, Pagination, Navigation } from 'vue3-carousel';
import MixinFunctions from "@/components/MixinFunctions";
import MediaBox from "@/components/MediaBox";
import StarRating from 'vue-star-rating'
import { toast } from "bulma-toast";

export default {
  name: "ProductView",
  mixins: [MixinFunctions],
  data(){
    return{
      product:[],
      Slides: null,
      quantity: 1,
      activeReview: false,
      ratingMessage: '',
      rating: null,
      validRate: true
    }
  },
  watch: {
    rating(val) {
      if (val && !this.validRate) {
        this.validRate = true
      }
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

    },
    async submitRate() {
      if (!this.rating) {
        this.validRate = false
      } else {
        const formData = {
          content: this.ratingMessage,
          object_id: this.product.id,
          rate: this.rating
        }
        await axios.
          post('/api/v1/reviews/', formData)
              .then(response => 
                {
                  this.product.reviews.unshift(response.data)
                  toast(
                      {
                        message: 'The review was added!',
                        type: 'is-success',
                        dismissible: true,
                        pauseOnHover: true,
                        duration: 2000,
                        position:'bottom-center',
                      }
                  )
                }
              )
              .catch(errors =>
                {
                  console.log(errors)
                } 
              )
      }
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
    MediaBox,
    StarRating
  }
}


</script>

<style scoped>
.image img {
  width: 450px;
  height: 450px;
}
</style>