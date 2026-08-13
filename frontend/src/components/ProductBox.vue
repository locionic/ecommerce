<template>
  <div class="column is-3">
    <div class="box product-box p-0">
      <figure class="image product-image-container">
        <router-link
            v-bind:to="{name: 'product', params: {product_slug: product.slug}}"
        >
          <img :src="product.thumbnail" alt="thumbnail" class="product-image">
          <div class="product-overlay">
            <span class="view-details-text">View Details</span>
          </div>
        </router-link>
        <div class="product-badge" v-if="product.is_active">
          <span class="icon is-small mr-1"><i class="fas fa-fire"></i></span> HOT
        </div>
      </figure>
      <div class="product-info">
        <p class="is-size-7 has-text-grey category-text">{{ product.category_name || 'Trending' }}</p>
        <h3 class="is-size-5 text-overflow-ellipsis product-title mt-1 mb-2">
          <router-link v-bind:to="{name: 'product', params: {product_slug: product.slug}}" class="product-title-link">
            {{product.title}}
          </router-link>
        </h3>
        <div class="display-inline-flex mt-auto">
          <p class="is-size-5 price-tag">&dollar;{{product.price}}</p>
          <button
            class="button is-primary is-small add-to-cart-btn"
            @click="addToCart(1, product)"
          >
            <span class="icon is-small">
              <i class="fas fa-shopping-bag"></i>
            </span>
          </button>
        </div>
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
.product-box {
  border-radius: 20px;
  height: 100%;
  display: flex;
  flex-direction: column;
  transition: all 0.4s cubic-bezier(0.175, 0.885, 0.32, 1.275);
  border: 1px solid rgba(255,255,255,0.05);
  box-shadow: 0 10px 25px -5px rgba(0, 0, 0, 0.5);
  background: rgba(255,255,255,0.03);
  backdrop-filter: blur(10px);
  overflow: hidden;
  position: relative;
}

.product-box::before {
  content: "";
  position: absolute;
  top: 0; left: 0; right: 0; bottom: 0;
  border-radius: 20px;
  padding: 2px;
  background: linear-gradient(135deg, rgba(255,255,255,0.1), rgba(255,255,255,0));
  -webkit-mask: linear-gradient(#fff 0 0) content-box, linear-gradient(#fff 0 0);
  -webkit-mask-composite: xor;
  mask-composite: exclude;
  pointer-events: none;
}

.product-box:hover {
  transform: translateY(-8px);
  box-shadow: 0 20px 40px -10px rgba(99, 102, 241, 0.3);
  background: rgba(255,255,255,0.05);
}

.product-image-container {
  overflow: hidden;
  background-color: #fff; /* White background to blend product images */
  position: relative;
  aspect-ratio: 1 / 1;
}

.product-image {
  width: 100%;
  height: 100%;
  object-fit: cover;
  transition: transform 0.6s cubic-bezier(0.175, 0.885, 0.32, 1.275);
}

.product-box:hover .product-image {
  transform: scale(1.08);
}

.product-overlay {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(17, 24, 39, 0.6);
  backdrop-filter: blur(4px);
  display: flex;
  justify-content: center;
  align-items: center;
  opacity: 0;
  transition: opacity 0.4s ease;
}

.product-box:hover .product-overlay {
  opacity: 1;
}

.view-details-text {
  color: #fff;
  font-weight: 600;
  font-size: 0.85rem;
  letter-spacing: 1px;
  text-transform: uppercase;
  padding: 10px 24px;
  border: 1px solid rgba(255,255,255,0.2);
  border-radius: 100px;
  background: rgba(255,255,255,0.1);
  transform: translateY(15px);
  transition: all 0.4s cubic-bezier(0.175, 0.885, 0.32, 1.275);
}

.product-box:hover .view-details-text {
  transform: translateY(0);
}
.view-details-text:hover {
  background: #fff;
  color: #000;
  transform: scale(1.05);
}

.product-badge {
  position: absolute;
  top: 12px;
  left: 12px;
  background: linear-gradient(135deg, #ef4444 0%, #f97316 100%);
  color: #fff;
  font-weight: 700;
  font-size: 0.65rem;
  padding: 6px 12px;
  border-radius: 100px;
  letter-spacing: 1px;
  text-transform: uppercase;
  box-shadow: 0 4px 10px rgba(239, 68, 68, 0.4);
}

.product-info {
  padding: 1.5rem;
  display: flex;
  flex-direction: column;
  flex: 1;
}

.category-text {
  text-transform: uppercase;
  letter-spacing: 1px;
  font-size: 0.7rem;
  color: #9ca3af !important;
  font-weight: 600;
}

.product-title {
  line-height: 1.4;
  letter-spacing: -0.5px;
  font-weight: 700;
}

.product-title-link {
  color: #f3f4f6 !important;
  transition: color 0.3s ease;
}

.product-box:hover .product-title-link {
  color: #00F0FF !important;
}

.price-tag {
  font-weight: 700;
  letter-spacing: -0.5px;
  color: #00F0FF !important;
}

.display-inline-flex {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-top: auto;
  padding-top: 1.5rem;
  border-top: 1px solid rgba(255,255,255,0.05);
}

.add-to-cart-btn {
  height: 42px;
  width: 42px;
  padding: 0;
  display: flex;
  justify-content: center;
  align-items: center;
  border-radius: 12px;
  background: rgba(255,255,255,0.05);
  border: 1px solid rgba(255,255,255,0.1);
  color: #fff;
  transition: all 0.3s cubic-bezier(0.175, 0.885, 0.32, 1.275);
}

.add-to-cart-btn:hover {
  background: linear-gradient(135deg, #00F0FF 0%, #6366F1 100%);
  border-color: transparent;
  color: #fff;
  transform: scale(1.1) rotate(5deg);
  box-shadow: 0 5px 15px rgba(0, 240, 255, 0.4);
}

.text-overflow-ellipsis {
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}
</style>