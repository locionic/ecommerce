import { createStore } from 'vuex'
// import createPersistedState from "vuex-persistedstate";

export default createStore({
  // plugins: [ createPersistedState() ],
  state: {
    cart:{
      items:[],
    },
    isAuthenticated: false,
    token: '',
    isLoading: false,
    formAddress: null,
    showDetail: ['first_name', 'last_name', 'email', 'phone', 'address', 'zipcode', 'place', 'cash_on_delivery', 'created_at']
  },
  getters: {
  },
  mutations: {
    initializeStore(state){
      if (localStorage.getItem('cart')){
        state.cart = JSON.parse(localStorage.getItem('cart'))
      }else{
        localStorage.setItem('cart', JSON.stringify(state.cart))
      }

      if (localStorage.getItem('token')){
        state.token = localStorage.getItem('token')
        state.isAuthenticated = true
      } else {
        state.token = ''
        state.isAuthenticated = false
      }
    },
    addToCart(state, item){
      const exists = state.cart.items.filter(i => i.product.id === item.product.id)

      if (exists.length){
        exists[0].quantity = parseInt(exists[0].quantity + parseInt(item.quantity))
      }else{
        state.cart.items.push(item)
      }
      localStorage.setItem('cart', JSON.stringify(state.cart))
    },
    setIsLoading(state, status){
      state.isLoading = status
    },
    clearCart(state){
      state.cart = {items: []}
      localStorage.setItem('cart', JSON.stringify(state.cart))
    },
    setFormAddress(state, form) {
      state.formAddress = form
    }
  },
  actions: {
  },
  modules: {
  }
})
