<template>
  <div class="page-product container mt-5">
    <div class="columns is-multiline">
      <!-- Image Gallery Column -->
      <div class="column is-7-desktop is-12-tablet">
        <div class="box product-gallery-box">
          <figure class="image product-main-image mb-4">
            <Carousel v-if="Slides" :itemsToShow="1" class="premium-carousel">
              <Slide v-for="(slide, id) in Slides" :key="id">
                <img :src="slide.image" alt="thumbnail for product" class="carousel-img">
              </Slide>
              <template #addons="{ slidesCount }">
                <Pagination/>
                <Navigation v-if="slidesCount > 1" />
              </template>
            </Carousel>
          </figure>
        </div>

        <div class="box mt-5 review-box" v-if="product.reviews && product.reviews.length > 0">
          <h2 class="title is-4 mb-4">Customer Reviews</h2>
          <template v-for="(review, index) in product.reviews" :key="index + 'review product'">
            <MediaBox :object-param="review" />
          </template>
        </div>
      </div>
      
      <!-- Product Info Column -->
      <div class="column is-5-desktop is-12-tablet pl-5-desktop">
        <div class="product-info-sticky">
          <h1 class="title is-2 product-title mb-2">{{product.title}}</h1>
          <p class="is-size-3 has-text-primary has-text-weight-bold mb-4">&dollar;{{product.price}}</p>
          
          <div class="description-block mb-5">
            <p class="has-text-grey-dark is-size-6">{{product.description}}</p>
          </div>
          
          <hr class="premium-hr">

          <div class="field has-addons mb-5 quantity-field">
            <div class="control">
              <button class="button is-light" @click="quantity > 1 ? quantity-- : null">-</button>
            </div>
            <div class="control">
              <input type="number" class="input has-text-centered no-spinners" min="1" v-model="quantity" style="width: 60px;">
            </div>
            <div class="control">
              <button class="button is-light" @click="quantity++">+</button>
            </div>
          </div>
          
          <button class="button is-primary is-medium is-fullwidth add-to-cart-btn mb-4" @click="addToCart(quantity, product)">
            <span class="icon">
              <i class="fas fa-shopping-bag"></i>
            </span>
            <span>Add to Cart</span>
          </button>

          <div class="dropdown is-right" :class="{'is-active': activeReview}" style="width: 100%;">
            <div class="dropdown-trigger" style="width: 100%;">
              <button class="button is-white is-fullwidth has-text-grey" aria-haspopup="true" aria-controls="dropdown-menu3" @click="activeReview = !activeReview">
                <span class="icon is-small">
                  <i class="fas fa-star"></i>
                </span>
                <span>Write a Review</span>
                <span class="icon is-small ml-auto">
                  <i class="fas fa-angle-down" aria-hidden="true"></i>
                </span>
              </button>
            </div>
            <div class="dropdown-menu" id="dropdown-menu3" role="menu" style="width: 100%;">
              <div class="dropdown-content p-4">
                <div class="field mb-3">
                  <div class="control has-icons-left">
                    <input class="input" type="text" placeholder="Share your thoughts..." v-model="ratingMessage">
                    <span class="icon is-small is-left">
                      <i class="fa-solid fa-message"></i>
                    </span>
                  </div>
                </div>
                <div class="is-flex is-align-items-center is-justify-content-space-between">
                  <star-rating v-model:rating="rating" :star-size="20" :show-rating="false" />
                  <button class="button is-primary is-small" @click="submitRate">Submit Review</button>
                </div>
                <p v-if="!validRate" class="help is-danger mt-2">Please select a rating.</p>
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
                  this.activeReview = false;
                  this.ratingMessage = '';
                  this.rating = null;
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
.page-product {
  padding-bottom: 4rem;
}
.product-gallery-box {
  border-radius: 20px;
  padding: 1.5rem;
  box-shadow: 0 10px 25px -5px rgba(0, 0, 0, 0.5);
  background: rgba(255,255,255,0.03);
  backdrop-filter: blur(10px);
  border: 1px solid rgba(255,255,255,0.05);
}
.premium-carousel {
  background-color: #fff;
  border-radius: 12px;
  overflow: hidden;
}
.carousel-img {
  max-width: 100%;
  max-height: 500px;
  object-fit: contain;
  border-radius: 12px;
}
.product-info-sticky {
  position: sticky;
  top: 100px;
}
.product-title {
  letter-spacing: -0.5px;
  font-weight: 700;
  color: #fff;
}
.description-block {
  line-height: 1.6;
}
.description-block p {
  color: #d1d5db !important;
}
.premium-hr {
  background-color: rgba(255,255,255,0.1);
  height: 1px;
  border: none;
  margin: 2rem 0;
}
.add-to-cart-btn {
  border-radius: 12px;
  font-size: 1.1rem;
  padding: 1.5rem;
  background: linear-gradient(135deg, #00F0FF 0%, #6366F1 100%);
  border: none;
  color: #fff;
  box-shadow: 0 10px 15px -3px rgba(0, 240, 255, 0.3);
}
.add-to-cart-btn:hover {
  transform: translateY(-2px);
  box-shadow: 0 15px 20px -3px rgba(0, 240, 255, 0.4);
}
.quantity-field .input {
  border-radius: 0;
  border-left: none;
  border-right: none;
  background: rgba(255,255,255,0.05);
  color: #fff;
  border-color: rgba(255,255,255,0.1);
}
.quantity-field .button:first-child {
  border-top-left-radius: 8px;
  border-bottom-left-radius: 8px;
  background: rgba(255,255,255,0.1);
  color: #fff;
  border-color: rgba(255,255,255,0.1);
}
.quantity-field .button:last-child {
  border-top-right-radius: 8px;
  border-bottom-right-radius: 8px;
  background: rgba(255,255,255,0.1);
  color: #fff;
  border-color: rgba(255,255,255,0.1);
}
.no-spinners::-webkit-outer-spin-button,
.no-spinners::-webkit-inner-spin-button {
  -webkit-appearance: none;
  margin: 0;
}
.review-box {
  border-radius: 20px;
  padding: 1.5rem;
  background: rgba(255,255,255,0.03);
  backdrop-filter: blur(10px);
  border: 1px solid rgba(255,255,255,0.05);
}
.ml-auto {
  margin-left: auto;
}
</style>