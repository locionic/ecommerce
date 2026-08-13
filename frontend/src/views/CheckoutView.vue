<template>
  <div class="page-checkout container mt-5">
    <div class="columns is-multiline">
      <div class="column is-12">
        <h1 class="title is-2 mb-6 page-title">Secure Checkout</h1>
      </div>
      
      <!-- Order Summary -->
      <div class="column is-5 is-offset-0 order-first-mobile">
        <div class="box summary-box">
          <h2 class="title is-4 mb-5 summary-title">Order Summary</h2>
          <table class="table is-fullwidth is-hoverable summary-table">
            <thead>
              <tr>
                <th>Product</th>
                <th class="has-text-centered">Qty</th>
                <th class="has-text-right">Total</th>
              </tr>
            </thead>
            <tbody>
              <tr
                v-for="item in cart.items"
                v-bind:key="item.product.id"
              >
                <td><span class="has-text-weight-medium text-overflow-ellipsis inline-block" style="max-width: 150px;">{{item.product.title}}</span></td>
                <td class="has-text-centered">{{item.quantity}}</td>
                <td class="has-text-right has-text-weight-bold">&dollar;{{getItemTotal(item).toFixed(2)}}</td>
              </tr>
            </tbody>
          </table>
          
          <hr class="premium-hr">
          
          <div class="is-flex is-justify-content-space-between mb-3">
            <span class="has-text-grey">Subtotal ({{cartTotalLength}} items)</span>
            <span class="has-text-weight-semibold">&dollar;{{cartTotalPrice.toFixed(2)}}</span>
          </div>
          <div class="is-flex is-justify-content-space-between mb-3">
            <span class="has-text-grey">Shipping</span>
            <span class="has-text-success">Free</span>
          </div>
          <div class="is-flex is-justify-content-space-between mb-3" v-if="cash_on_delivery">
            <span class="has-text-grey">Cash on Delivery Fee</span>
            <span class="has-text-weight-semibold">&dollar;10.00</span>
          </div>

          <hr class="premium-hr">

          <div class="is-flex is-justify-content-space-between mb-2">
            <span class="is-size-4 has-text-weight-bold">Total</span>
            <span class="is-size-3 has-text-primary has-text-weight-bold">&dollar;{{ (cartTotalPrice + (cash_on_delivery ? 10 : 0)).toFixed(2) }}</span>
          </div>
        </div>
      </div>

      <!-- Shipping & Payment Details -->
      <div class="column is-7">
        <div class="box checkout-box mb-5">
          <h2 class="title is-4 mb-4">Shipping Information</h2>
          <p class="has-text-grey-light mb-5 is-size-7">* All fields are required</p>
          
          <div class="columns is-multiline">
            <div class="column is-6 pb-2">
              <div class="field">
                <label class="label has-text-weight-medium">First Name</label>
                <div class="control has-icons-left">
                  <input id='first_name-input' type="text" class="input" v-model="first_name" placeholder="John">
                  <span class="icon is-small is-left"><i class="fas fa-user"></i></span>
                </div>
              </div>
            </div>

            <div class="column is-6 pb-2">
              <div class="field">
                <label class="label has-text-weight-medium">Last Name</label>
                <div class="control has-icons-left">
                  <input id='last_name-input' type="text" class="input" v-model="last_name" placeholder="Doe">
                  <span class="icon is-small is-left"><i class="far fa-user"></i></span>
                </div>
              </div>
            </div>

            <div class="column is-6 pb-2">
              <div class="field">
                <label class="label has-text-weight-medium">E-mail</label>
                <div class="control has-icons-left">
                  <input id='email-input' type="email" class="input" v-model="email" placeholder="john@example.com">
                  <span class="icon is-small is-left"><i class="fas fa-envelope"></i></span>
                </div>
              </div>
            </div>

            <div class="column is-6 pb-2">
              <div class="field">
                <label class="label has-text-weight-medium">Phone</label>
                <div class="control has-icons-left">
                  <input id='phone-input' type="text" class="input" v-model="phone" placeholder="+1 (555) 000-0000">
                  <span class="icon is-small is-left"><i class="fas fa-phone"></i></span>
                </div>
              </div>
            </div>

            <div class="column is-12 pb-2">
              <div class="field">
                <label class="label has-text-weight-medium">Address</label>
                <div class="control has-icons-left">
                  <input id='address-input' type="text" class="input" v-model="address" placeholder="123 Main St, Apt 4B">
                  <span class="icon is-small is-left"><i class="fas fa-map-marker-alt"></i></span>
                </div>
              </div>
            </div>

            <div class="column is-6 pb-2">
              <div class="field">
                <label class="label has-text-weight-medium">Zip Code</label>
                <div class="control has-icons-left">
                  <input id='zipcode-input' type="number" class="input" v-model="zipcode" placeholder="10001">
                  <span class="icon is-small is-left"><i class="fas fa-map-pin"></i></span>
                </div>
              </div>
            </div>

            <div class="column is-6 pb-2">
              <div class="field">
                <label class="label has-text-weight-medium">City / Place</label>
                <div class="control has-icons-left">
                  <input id='place-input' type="text" class="input" v-model="place" placeholder="New York">
                  <span class="icon is-small is-left"><i class="fas fa-city"></i></span>
                </div>
              </div>
            </div>
          </div>
        </div>

        <div class="box checkout-box">
          <h2 class="title is-4 mb-4">Payment Method</h2>
          
          <div class="payment-methods mb-5">
            <label class="payment-option">
              <input type="radio" id="online" name="payment_method" value="online" v-model="payment_method" @click="setThePayment">
              <div class="payment-card">
                <span class="icon is-medium has-text-primary"><i class="fas fa-credit-card fa-lg"></i></span>
                <span class="has-text-weight-semibold">Online Payment (PayPal/Card)</span>
              </div>
            </label>
            
            <label class="payment-option mt-3">
              <input type="radio" id="cash" name="payment_method" value="cash" v-model="payment_method" @click="setThePayment">
              <div class="payment-card">
                <span class="icon is-medium has-text-info"><i class="fas fa-truck fa-lg"></i></span>
                <span class="has-text-weight-semibold">Cash on Delivery (+&dollar;10 USD)</span>
              </div>
            </label>
          </div>

          <div class="notification is-danger is-light mb-4" v-if="errors.length">
            <button class="delete" @click="errors = []"></button>
            <p v-for="error in errors" v-bind:key="error">{{error}}</p>
          </div>

          <template v-if="cartTotalLength">
            <hr class="premium-hr">
            
            <button id="pay-now" class="button is-primary is-medium is-fullwidth checkout-btn mb-4" @click="submitForm">
              <span class="icon"><i class="fas fa-lock"></i></span>
              <span>Pay now!</span>
            </button>
          </template>

          <div id="payment-card" class="mt-4">
            <div id="paypal-button-container"></div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import axios from "axios";
export default {
  name:"CheckoutView",
  data(){
    return{
      cart:{
        items:[]
      },
      paypal:{},
      card:{},
      first_name:"",
      last_name:"",
      email:"",
      phone:"",
      address:"",
      zipcode: null,
      place:"",
      cash_on_delivery: false,
      errors: [],
      payment_method: 'online'
    }
  },
  mounted() {
    document.title = "Checkout"
    this.cart = this.$store.state.cart
    if (this.$store.state.formAddress) {
      this.first_name = this.$store.state.formAddress.first_name
      this.last_name = this.$store.state.formAddress.last_name
      this.email = this.$store.state.formAddress.email
      this.phone = this.$store.state.formAddress.phone
      this.address = this.$store.state.formAddress.address
      this.zipcode = this.$store.state.formAddress.zipcode
      this.place = this.$store.state.formAddress.place
    }
  },
  methods: {
    getItemTotal(item){
      return item.quantity * item.product.price
    },
    submitForm(){
      this.errors = []
      if (this.first_name === ''){
        this.errors.push('The first name field is missing!')
        document.getElementById('first_name-input').setAttribute('class', 'input is-danger')
      }
      if (this.last_name === ''){
        this.errors.push('The last name field is missing!')
        document.getElementById('last_name-input').setAttribute('class', 'input is-danger')

      }
      if (this.email === ''){
        this.errors.push('The email field is missing!')
        document.getElementById('email-input').setAttribute('class', 'input is-danger')

      }
      if (this.phone === ''){
        this.errors.push('The email field is missing!')
        document.getElementById('phone-input').setAttribute('class', 'input is-danger')

      }
      if (this.address === ''){
        this.errors.push('The address field is missing!')
        document.getElementById('address-input').setAttribute('class', 'input is-danger')
      }
      if (this.place === ''){
        this.errors.push('The place field is missing')
        document.getElementById('place-input').setAttribute('class', 'input is-danger')
      }
      if (this.errors.length === 0){
        document.getElementById('pay-now').disabled=true
        document.getElementById('first_name-input').disabled=true
        document.getElementById('last_name-input').disabled=true
        document.getElementById('email-input').disabled=true
        document.getElementById('phone-input').disabled=true
        document.getElementById('address-input').disabled=true
        document.getElementById('place-input').disabled=true
        document.getElementById('online').disabled=true
        document.getElementById('cash').disabled=true
      }
      if (!this.errors.length){
        this.submitData()
      }
    },
    setThePayment: function (){
      if (document.getElementById("online").checked){
        document.getElementById('pay-now').innerHTML = "Pay now!"
        this.cash_on_delivery = false
      }
      else if (document.getElementById("cash").checked){
        document.getElementById('pay-now').innerHTML = "Pay later!"
        this.cash_on_delivery = true
      }
    },
    submitData: async function(){
      const items = []
      for(let i=0; i<this.cart.items.length; i++){
        const item = this.cart.items[i]
        const obj = {
          product: item.product.id,
          quantity: item.quantity,
          price: item.product.price
        }
        items.push(obj)
      }
      const formData = {
        first_name: this.first_name,
        last_name: this.last_name,
        email: this.email,
        zipcode: this.zipcode,
        address: this.address,
        place: this.place,
        phone: this.phone,
        return_url: `${window.location.origin}/cart/success/`,
        cancel_url: document.URL,
        cash_on_delivery: this.cash_on_delivery,
        items: items
      }
      this.$store.commit('setIsLoading', true)
      this.$store.commit('setFormAddress', formData)
      await axios.
      post('/api/v1/orders/', formData)
          .then(response => {
            if(response.data.paypal){
              const data = response.data
              window.open(data.paypal[0].links[1].href)
            }
            this.$store.commit('clearCart')
            this.$router.push('/my-orders')
          }).catch(errors =>{
            console.log(errors)
          }
      )
      this.$store.commit('setIsLoading', false)
    }
  },
  computed:{
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
  },
}
</script>

<style scoped>
.page-checkout {
  padding-bottom: 4rem;
}
.page-title {
  letter-spacing: -1px;
  font-weight: 700;
}
.checkout-box, .summary-box {
  border-radius: 20px;
  border: 1px solid rgba(255,255,255,0.05);
  box-shadow: 0 10px 25px -5px rgba(0, 0, 0, 0.5);
  padding: 2rem;
  background: rgba(255,255,255,0.03);
  backdrop-filter: blur(10px);
}
.summary-title {
  border-bottom: 1px solid rgba(255,255,255,0.1);
  padding-bottom: 1rem;
}
.summary-table {
  background: transparent !important;
  color: #fff;
}
.summary-table th {
  border-bottom: 1px solid rgba(255,255,255,0.1);
  color: #9ca3af;
  font-size: 0.85rem;
  text-transform: uppercase;
}
.summary-table td {
  border-bottom: 1px solid rgba(255,255,255,0.05);
  vertical-align: middle;
  color: #fff;
}
.premium-hr {
  background-color: rgba(255,255,255,0.1);
  height: 1px;
  border: none;
  margin: 1.5rem 0;
}
.inline-block {
  display: inline-block;
}
.text-overflow-ellipsis {
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}
.checkout-btn {
  border-radius: 12px;
  background: linear-gradient(135deg, #00F0FF 0%, #6366F1 100%);
  border: none;
  color: #fff;
  box-shadow: 0 10px 15px -3px rgba(0, 240, 255, 0.3);
}
.checkout-btn:hover {
  transform: translateY(-2px);
  box-shadow: 0 15px 20px -3px rgba(0, 240, 255, 0.4);
}

/* Payment Radio Cards */
.payment-methods input[type="radio"] {
  display: none;
}
.payment-option {
  display: block;
  cursor: pointer;
}
.payment-card {
  display: flex;
  align-items: center;
  padding: 1rem 1.5rem;
  border: 1px solid rgba(255,255,255,0.1);
  border-radius: 12px;
  transition: all 0.2s ease;
  background: rgba(255,255,255,0.05);
  color: #d1d5db;
}
.payment-card .icon {
  margin-right: 1rem;
}
.payment-methods input[type="radio"]:checked + .payment-card {
  border-color: #00F0FF;
  background-color: rgba(0, 240, 255, 0.1);
  box-shadow: 0 0 0 2px rgba(0, 240, 255, 0.2);
  color: #fff;
}

@media screen and (max-width: 768px) {
  .order-first-mobile {
    order: -1;
    margin-bottom: 2rem;
  }
}
</style>