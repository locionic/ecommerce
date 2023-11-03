<template>
  <div class="column is-3">
    <div class="box">
      <figure class="image mb-4">
        <router-link
            v-bind:to="{name: 'product',
                        params: {product_slug: product.slug}}"
        >
          <img :src="product.thumbnail" alt="thumbnail for product">
        </router-link>
      </figure>
      <h3 class="is-size-4 text-overflow-ellipsis">{{product.title}}</h3>
      <div class="display-inline-flex mt-4">
        <p class="is-size-6 has-text-grey-dark vertical-align">&dollar;{{product.price}}</p>
        <button
          class="button is-dark custom-background-color-button"
          @click="addToCart(1, product)"
        >
          Add to cart
        </button>
      </div>
      

    </div>
  </div>
</template>
<script>
import MixinFunctions from "@/components/MixinFunctions";

export default {
  name: 'ProductBox',
  mixins: [MixinFunctions],
  props:{
    product:Object
  }
}
</script>
<style scoped>
.image{
  margin-top: -1.25rem;
  margin-right: -1.25rem;
  margin-left: -1.25rem;
}
img {
  /* width: 400px; */
  height: 300px;
  border-bottom: 1px solid #dedbdb;
}
.button.custom-background-color-button {
  background-color: #23c5dd;
}
.vertical-align {
  padding:4px;
  color: #ffffff;
  font: bold 12px "Helvetica Neue", Helvetica, Arial, sans-serif;
  line-height: 30px;
  margin: 0 4px 0 0;
  width:93%;
}
.display-inline-flex {
  display: flex;
  justify-content: space-between;
}
.text-overflow-ellipsis {
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}
.box {
  border-radius: 10px;
}
</style>