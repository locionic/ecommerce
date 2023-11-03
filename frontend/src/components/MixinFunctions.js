import {toast} from "bulma-toast"

export default {
  data() {
    return { /* data */ }
  },
  methods: {
    addToCart: function (quantity_arg, product){
      let quantity = quantity_arg
      if (isNaN(quantity) || quantity < 1){
        quantity = 1
      }
      const item = {
        product: product,
        quantity: quantity
      }
      this.$store.commit('addToCart', item)
      toast(
          {
            message: 'The product was added to the cart',
            type: 'is-success',
            dismissible: true,
            pauseOnHover: true,
            duration: 2000,
            position:'bottom-center',
          }
      )
    }
  }
}