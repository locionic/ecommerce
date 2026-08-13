<template>
  <div id="wrapper">
    <nav class="navbar custom-blur-down" style="position: sticky; top: 0;">
      <div class="navbar-brand">
        <router-link to="/" class="navbar-item"><strong>iShop</strong></router-link>
        <a class="navbar-burger" aria-label="menu" aria-expanded="false" data-target="navbar-menu" @click="showMobileMenu = !showMobileMenu">
          <span aria-hidden="true"></span>
          <span aria-hidden="true"></span>
          <span aria-hidden="true"></span>
        </a>
      </div>
        <div class="navbar-menu" id="navbar-menu" v-bind:class="{'is-active': showMobileMenu}">
          <div class="navbar-start">
            <!-- <router-link class="navbar-item" to="/">
              Home
            </router-link>

            <router-link class="navbar-item" to="/about">
              About
            </router-link> -->

            <div class="navbar-item has-dropdown is-hoverable">
              <a class="navbar-link">
                Categories
              </a>

              <div class="navbar-dropdown">
                  <router-link
                      v-for="category in Categories"
                      v-bind:key="category.slug"
                      v-bind:to="{
                        name: 'category',
                        params: {category_slug: category.slug}
                      }"
                     class="navbar-item"
                  >
                    {{category.name}}
                  </router-link>
              </div>
            </div>
            <div class="navbar-item">
              <form action="/search" method="get">
                <div class="field has-addons">
                  <div class="control">
                    <input type="text" class="input" placeholder="What are you looking for?" name="search">
                  </div>
                  <div class="control">
                    <button class="button is-primary">
                      <span class="icon">
                        <i class="fas fa-search"></i>
                      </span>
                    </button>
                  </div>
                </div>
              </form>
            </div>
          </div>
          <div class="navbar-end">
            <div class="navbar-item">
              <div class="buttons">
                <template v-if="$store.state.isAuthenticated">
                  <router-link to="/my-account" class="button is-primary">My account</router-link>
                </template>
                <template v-else>
                <router-link to="/signup" class="button is-primary">Sign up</router-link>
                <router-link to="/login" class="button is-primary is-outlined" style="background: transparent;">Log in</router-link>
                </template>
                <router-link to="/cart" class="button is-primary">
                  <span class="icon"><i class="fas fa-shopping-cart"></i></span>
                  <span>Cart ({{cartTotalLength}})</span>
                </router-link>
              </div>
            </div>
          </div>
        </div>
    </nav>
    <ScrollTopButton />
    <div class="is-loading-bar has-text-centered" v-bind:class="{'is-loading': $store.state.isLoading}">
      <div class="lds-dual-ring">

      </div>
    </div>
    
    <!-- Render Demo Notice Modal -->
    <div class="modal" :class="{'is-active': showDemoModal}">
      <div class="modal-background" @click="showDemoModal = false"></div>
      <div class="modal-content">
        <div class="box p-6 has-text-centered" style="background: rgba(17,24,39,0.9); border: 1px solid rgba(255,255,255,0.1); backdrop-filter: blur(20px); border-radius: 20px;">
          <span class="icon is-large mb-4" style="color: #00F0FF;">
            <i class="fas fa-info-circle fa-3x"></i>
          </span>
          <h2 class="title is-3 mb-4">Welcome to the Demo!</h2>
          <p class="mb-5" style="color: #d1d5db; line-height: 1.6;">This frontend is connected to a backend hosted on <strong>Render's free tier</strong>. If the backend has been inactive, it may take <strong>up to 50 seconds</strong> to spin back up on your first request.</p>
          <p class="mb-6" style="color: #d1d5db;">Please be patient while the products load!</p>
          <button class="button is-medium is-fullwidth" @click="dismissDemo" style="background: linear-gradient(135deg, #00F0FF 0%, #6366F1 100%); border: none; color: white; border-radius: 12px; font-weight: 600;">I Understand</button>
        </div>
      </div>
      <button class="modal-close is-large" aria-label="close" @click="dismissDemo"></button>
    </div>

    <main class="main-content">
      <router-view/>
    </main>
  </div>
  <footer class="footer">
    <p class="has-text-centered">Copyright Loc 2023</p>
  </footer>
</template>
<script>
import axios from "axios";
import ScrollTopButton from "@/components/ScrollTopButton";

export default {
  components: {
    ScrollTopButton
  },
  data(){
    return{
      Categories: [],
      showMobileMenu: false,
      showDemoModal: false,
      cart:{
        items:[]
      }
    }
  },
  beforeCreate() {
    this.$store.commit('initializeStore')
    const token = this.$store.state.token

    if (token){
      axios.defaults.headers.common['Authorization'] = "Token " + token
    } else{
      axios.defaults.headers.common['Authorization'] = ""
    }
  },
  mounted() {
    if (!sessionStorage.getItem('demo_dismissed')) {
      this.showDemoModal = true;
    }
    
    this.cart = this.$store.state.cart
    axios.get('/api/v1/categories/').then(response =>{
      this.Categories = response.data.results
    }).catch(error =>{
      console.log(error)
    })
  },
  methods: {
    dismissDemo() {
      this.showDemoModal = false;
      sessionStorage.setItem('demo_dismissed', 'true');
    }
  },
  watch: {
    '$store.state.cart' (val) {
      this.cart = val
    }
  },
  computed:{
    cartTotalLength(){
      let totalLength = 0
      for(let i=0; i<this.cart.items.length; i++){
        totalLength += this.cart.items[i].quantity
      }
      return totalLength
    }
  }
}
</script>
<style lang="scss">
@import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;500;700;900&display=swap');

$family-primary: 'Outfit', sans-serif;
$primary: #6366F1;
$primary-light: #818CF8;
$info: #06b6d4;
$success: #10B981;
$background: #030712;
$text: #f9fafb;

@import "../node_modules/bulma";

body {
  background-color: $background;
  color: $text;
  font-family: $family-primary;
  overflow-x: hidden;
  position: relative;
}

/* Global Bulma Overrides for Dark Theme */
h1, h2, h3, h4, h5, h6, .title, .subtitle, strong {
  color: #f9fafb !important;
}

.box {
  background-color: rgba(255, 255, 255, 0.03);
  color: $text;
}

/* Global Table Overrides */
.table {
  background-color: transparent !important;
  color: #fff !important;
}
.table th {
  color: #9ca3af !important;
  border-color: rgba(255, 255, 255, 0.1) !important;
}
.table td {
  border-color: rgba(255, 255, 255, 0.05) !important;
  color: #fff !important;
}
.table.is-hoverable tbody tr:not(.is-selected):hover {
  background-color: rgba(255, 255, 255, 0.05) !important;
}
.table thead td, .table thead th {
  color: #9ca3af !important;
}

/* Background glowing orbs */
body::before, body::after {
  content: "";
  position: fixed;
  border-radius: 50%;
  filter: blur(120px);
  z-index: -1;
  opacity: 0.5;
  pointer-events: none;
}
body::before {
  top: -10%;
  left: -10%;
  width: 50vw;
  height: 50vw;
  background: radial-gradient(circle, rgba(99,102,241,0.2) 0%, rgba(3,7,18,0) 70%);
}
body::after {
  bottom: -10%;
  right: -10%;
  width: 40vw;
  height: 40vw;
  background: radial-gradient(circle, rgba(168,85,247,0.15) 0%, rgba(3,7,18,0) 70%);
}

#wrapper {
  display: flex;
  min-height: 100vh;
  flex-direction: column;
}

.main-content {
  flex: 1;
}

/* Floating Glassmorphism Navbar */
.navbar {
  background-color: rgba(17, 24, 39, 0.6);
  backdrop-filter: blur(20px);
  -webkit-backdrop-filter: blur(20px);
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 100px;
  margin: 1rem 2rem;
  padding: 0 1rem;
  box-shadow: 0 10px 30px -10px rgba(0, 0, 0, 0.5);
  transition: all 0.3s ease;
  z-index: 100;
}
@media (max-width: 768px) {
  .navbar { margin: 0; border-radius: 0; }
}

.navbar-brand .navbar-item strong {
  font-family: $family-primary;
  font-size: 1.8rem;
  letter-spacing: 1px;
  background: linear-gradient(135deg, #00F0FF 0%, #6366F1 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  font-weight: 900;
}

.navbar-item, .navbar-link {
  color: #d1d5db !important;
  font-weight: 500;
}
.navbar-item:hover, .navbar-link:hover,
.navbar-item.has-dropdown:hover .navbar-link,
.navbar-item.has-dropdown.is-active .navbar-link {
  color: #fff !important;
  background-color: transparent !important;
}

/* Dropdown Menu */
.navbar-dropdown {
  background-color: rgba(17, 24, 39, 0.95) !important;
  border: 1px solid rgba(255, 255, 255, 0.1) !important;
  border-radius: 12px !important;
  backdrop-filter: blur(20px) !important;
  padding: 0.5rem 0;
}
.navbar-dropdown .navbar-item {
  color: #d1d5db !important;
  transition: all 0.3s ease;
}
.navbar-dropdown .navbar-item:hover {
  background-color: rgba(255, 255, 255, 0.05) !important;
  color: #00F0FF !important;
}

/* Premium Buttons */
.button {
  border-radius: 100px;
  font-weight: 600;
  letter-spacing: 0.5px;
  transition: all 0.4s cubic-bezier(0.175, 0.885, 0.32, 1.275);
  border: none;
}
.button:hover {
  transform: translateY(-2px);
  box-shadow: 0 10px 20px -10px rgba(99, 102, 241, 0.5);
}
.button.is-primary {
  background: linear-gradient(135deg, #6366F1 0%, #a855f7 100%);
  color: #fff;
  border: 1px solid rgba(255, 255, 255, 0.2);
}
.button.is-primary:hover {
  background: linear-gradient(135deg, #818CF8 0%, #c084fc 100%);
}
.button.is-primary.is-outlined {
  background: rgba(255,255,255,0.05) !important;
  color: #fff !important;
  border: 1px solid rgba(255, 255, 255, 0.2) !important;
}

/* Inputs */
.input {
  border-radius: 100px;
  border: 1px solid rgba(255,255,255,0.2);
  background-color: rgba(255,255,255,0.05);
  color: #fff;
  transition: all 0.3s ease;
}
.input:focus {
  border-color: #6366F1;
  background-color: rgba(255,255,255,0.1);
  box-shadow: 0 0 0 3px rgba(99, 102, 241, 0.2);
}
.input::placeholder {
  color: #9ca3af;
}
.input.is-danger {
  border-color: #f14668 !important;
}
.field.has-addons .control:first-child .input {
  border-bottom-left-radius: 100px;
  border-top-left-radius: 100px;
}
.field.has-addons .control:last-child .button {
  border-bottom-right-radius: 100px;
  border-top-right-radius: 100px;
}

/* Pagination Overrides */
.pagination-link, .pagination-next, .pagination-previous {
  background-color: rgba(255, 255, 255, 0.05) !important;
  border-color: rgba(255, 255, 255, 0.1) !important;
  color: #d1d5db !important;
  transition: all 0.3s ease;
}
.pagination-link:hover, .pagination-next:hover, .pagination-previous:hover {
  background-color: rgba(255, 255, 255, 0.1) !important;
  color: #fff !important;
}
.pagination-link.is-current {
  background: linear-gradient(135deg, #00F0FF 0%, #6366F1 100%) !important;
  border-color: transparent !important;
  color: #fff !important;
}
.pagination-link.is-disabled, .pagination-next.is-disabled, .pagination-previous.is-disabled {
  opacity: 0.5;
  pointer-events: none;
}

/* Loading Ring */
.lds-dual-ring{
  display: inline-block;
  width: 80px;
  height: 80px;
}
.lds-dual-ring:after{
  content: ' ';
  display: block;
  width: 64px;
  margin: 8px;
  border-radius: 50%;
  border: 4px solid;
  border-color: $primary transparent $primary transparent;
  animation: lds-dual-ring 1.2s linear infinite;
}
@keyframes lds-dual-ring {
  0%{ transform: rotate(0deg); }
  100%{ transform: rotate(360deg); }
}
/* Fixed Top Loading Bar */
.is-loading-bar{
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  height: 0;
  background: rgba(3,7,18,0.8);
  backdrop-filter: blur(5px);
  overflow: hidden;
  transition: all 0.3s;
  z-index: 1000;
  display: flex;
  justify-content: center;
  align-items: center;
}
.is-loading-bar.is-loading{
  height: 100vh;
}

/* Footer */
.footer {
  background-color: rgba(17, 24, 39, 0.5);
  backdrop-filter: blur(20px);
  color: #9ca3af;
  padding: 1.5rem;
  border-top: 1px solid rgba(255,255,255,0.05);
  margin-top: auto;
}
</style>
