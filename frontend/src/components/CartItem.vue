<template>
  <tr>
    <td>
      <router-link v-bind:to="{
        name: 'product',
        params: {product_slug: item.product.slug}
      }" class="has-text-weight-semibold product-link"
      >
      {{item.product.title}}
    </router-link>
    </td>
    <td class="has-text-grey-dark">&dollar;{{item.product.price}}</td>
    <td>
      <div class="field has-addons is-justify-content-center">
        <p class="control">
          <button class="button is-small is-light rounded-left" @click="decrementQuantity(item)">
            <span class="icon is-small">
              <i class="fas fa-minus"></i>
            </span>
          </button>
        </p>
        <p class="control">
          <input class="input is-small has-text-centered no-spinners" type="number" readonly :value="item.quantity" style="width: 50px;">
        </p>
        <p class="control">
          <button class="button is-small is-light rounded-right" @click="incrementQuantity(item)">
            <span class="icon is-small">
              <i class="fas fa-plus"></i>
            </span>
          </button>
        </p>
      </div>
    </td>
    <td class="has-text-weight-bold">&dollar;{{getItemTotal(item).toFixed(2)}}</td>
    <td>
      <button class="button is-white has-text-danger is-small is-rounded delete-btn" @click="removeFromCart(item)">
        <span class="icon is-small">
          <i class="fas fa-trash-alt"></i>
        </span>
      </button>
    </td>
  </tr>
</template>

<script>
export default {
  name:'CartItem',
  props:{
    initialItem: Object
  },
  data(){
    return{
      item: this.initialItem
    }
  },
  methods: {
    getItemTotal(item){
      return item.quantity * item.product.price
    },
    decrementQuantity(item){
      item.quantity -= 1
      if(item.quantity === 0){
        this.$emit('removeFromCart', item)
      }
      this.updateCart()
    },
    incrementQuantity(item){
      item.quantity += 1
      this.updateCart()
    },
    updateCart(){
      localStorage.setItem('cart', JSON.stringify(this.$store.state.cart))
    },
    removeFromCart(item){
      this.$emit('removeFromCart', item)
      this.updateCart()
    }
  },

}
</script>

<style scoped>
.product-link {
  color: #f9fafb;
  font-weight: 600;
  font-size: 1.1rem;
  transition: color 0.2s ease;
}
.product-link:hover {
  color: #6366F1;
}
.no-spinners::-webkit-outer-spin-button,
.no-spinners::-webkit-inner-spin-button {
  -webkit-appearance: none;
  margin: 0;
}
.input.no-spinners {
  border-radius: 0;
  border-left: none;
  border-right: none;
  box-shadow: none;
  background-color: transparent;
}
.rounded-left {
  border-top-left-radius: 6px;
  border-bottom-left-radius: 6px;
}
.rounded-right {
  border-top-right-radius: 6px;
  border-bottom-right-radius: 6px;
}
.delete-btn {
  background: transparent;
  transition: all 0.2s ease;
}
.delete-btn:hover {
  background-color: #FEE2E2;
}
</style>