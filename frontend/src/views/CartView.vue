<template>
  <div class="page-cart container mt-5">
    <div class="columns is-multiline">
      <div class="column is-12">
        <h1 class="title is-2 mb-6 page-title">Shopping Cart</h1>
      </div>
      
      <div class="column is-8">
        <div class="box cart-box p-0">
          <table class="table is-fullwidth is-hoverable cart-table" v-if="cartTotalLength">
            <thead>
            <tr>
              <th>Product</th>
              <th>Price</th>
              <th class="has-text-centered">Quantity</th>
              <th>Total</th>
              <th></th>
            </tr>
            </thead>
            <tbody>
            <CartItem
              v-for="item in cart.items"
              v-bind:key="item.product.id"
              v-bind:initialItem="item"
              v-on:removeFromCart="removeFromCart"
            />
            </tbody>
          </table>
          <div v-else class="empty-cart-message p-6 has-text-centered">
            <span class="icon is-large has-text-grey-light mb-3">
              <i class="fas fa-shopping-cart fa-3x"></i>
            </span>
            <p class="is-size-5 has-text-grey">Your cart is currently empty.</p>
            <router-link to="/" class="button is-primary mt-4 is-rounded">Continue Shopping</router-link>
          </div>
        </div>
      </div>
      
      <div class="column is-4">
        <div class="box summary-box">
          <h2 class="title is-4 summary-title mb-5">Order Summary</h2>
          
          <div class="is-flex is-justify-content-space-between mb-3">
            <span class="has-text-grey">Items ({{cartTotalLength}})</span>
            <span class="has-text-weight-semibold">{{cartTotalPrice.toFixed(2)}} $</span>
          </div>
          
          <div class="is-flex is-justify-content-space-between mb-3">
            <span class="has-text-grey">Shipping</span>
            <span class="has-text-success">Free</span>
          </div>

          <hr class="premium-hr">

          <div class="is-flex is-justify-content-space-between mb-5">
            <span class="is-size-5 has-text-weight-bold">Total</span>
            <span class="is-size-4 has-text-primary has-text-weight-bold">{{cartTotalPrice.toFixed(2)}} $</span>
          </div>
          
          <router-link to="/cart/checkout" class="button is-primary is-fullwidth is-medium checkout-btn" :disabled="!cartTotalLength">
            <span>Proceed to Checkout</span>
            <span class="icon">
              <i class="fas fa-arrow-right"></i>
            </span>
          </router-link>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import CartItem from '@/components/CartItem.vue'
export default{
  name: 'CartView',
  components:{
    CartItem
  },
  data(){
    return{
      cart:{
        items:[]
      }
    }
  },
  mounted() {
    this.cart = this.$store.state.cart
  },
  methods: {
    removeFromCart(item){
      this.cart.items = this.cart.items.filter( i => i.product.id !== item.product.id)
    }
  },
  computed: {
    cartTotalLength: function () {
      return this.cart.items.reduce((acc, curVal) => {
        return acc + curVal.quantity
      }, 0)
    },
    cartTotalPrice: function () {
      return this.cart.items.reduce((acc, curVal) => {
        return acc + curVal.quantity * curVal.product.price
      }, 0)
    },
  }
}
</script>

<style scoped>
.page-cart {
  padding-bottom: 4rem;
}
.page-title {
  letter-spacing: -1px;
  font-weight: 700;
}
.cart-box, .summary-box {
  border-radius: 20px;
  border: 1px solid rgba(255,255,255,0.05);
  box-shadow: 0 10px 25px -5px rgba(0, 0, 0, 0.5);
  background: rgba(255,255,255,0.03);
  backdrop-filter: blur(10px);
}
.summary-box {
  padding: 2rem;
}
.summary-title {
  border-bottom: 1px solid rgba(255,255,255,0.1);
  padding-bottom: 1rem;
}
.premium-hr {
  background-color: rgba(255,255,255,0.1);
  height: 1px;
  border: none;
  margin: 1.5rem 0;
}
.cart-table {
  background: transparent !important;
  color: #fff;
}
.cart-table th {
  border-bottom: 1px solid rgba(255,255,255,0.1);
  padding: 1.5rem 1rem;
  color: #9ca3af;
  font-weight: 600;
  text-transform: uppercase;
  font-size: 0.85rem;
  letter-spacing: 0.5px;
}
.cart-table td {
  vertical-align: middle;
  padding: 1.5rem 1rem;
  border-bottom: 1px solid rgba(255,255,255,0.05);
  color: #fff;
}
.checkout-btn {
  border-radius: 12px;
  background: linear-gradient(135deg, #00F0FF 0%, #6366F1 100%);
  border: none;
  color: #fff;
  box-shadow: 0 10px 15px -3px rgba(0, 240, 255, 0.3);
}
.checkout-btn:hover:not([disabled]) {
  transform: translateY(-2px);
  box-shadow: 0 15px 20px -3px rgba(0, 240, 255, 0.4);
}
</style>