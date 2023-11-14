<template>
  <div class="page-my-account">
    <div class="column is-12">
      <h1 class="title">My orders</h1>
      <h3 class="subtitle"> You have successfully done {{count}} orders</h3>
    </div>
    <div class="section profile-heading">
      <div class="columns is-mobile is-multiline">
        <div class="column is-12">
          <OrderSummary
            v-for="order in orders"
            v-bind:key="order.id"
            v-bind:order="order"
          />
          <MyPagination @get-results="(path_param) => getMyOrders(path_param)" :count="count" :previous="previous" :next="next" :page="page" :default-api-get="defaultApiGet" />
        </div>
      </div>
    </div>

  </div>
</template>

<script>
import axios from "axios";
import OrderSummary from "@/components/OrderSummary.vue"
import MyPagination from "@/components/MyPagination.vue"
export default {
  name: "MyOrdersView",
  components:{
    OrderSummary,
    MyPagination
  },
  data(){
    return{
      orders: [],
      count: 0,
      next: null,
      previous: null,
      page: 1,
      defaultApiGet: '/api/v1/orders/mine/'
    }
  },
  methods:{
    getMyOrders: async function(path_param=null){
      this.$store.commit('setIsLoading', true)
      let path_url = '/api/v1/orders/mine/'
      if (path_param) {
        path_url = '/api' + path_param.split('/api')[1]
      }
      if (path_url.includes('page=')) {
        this.page = parseInt(path_url.split('page=')[1])
      } else {
        this.page = 1
      }
      axios.get(path_url)
          .then(response => {
            this.orders = response.data.results
            // .map(ele => ({...ele, created_at: ele.created_at.split('.')[0]}))
            this.count = response.data.count
            this.next = response.data.next
            this.previous = response.data.previous
          }).catch(error => {
        console.log(error)
      })

      this.$store.commit('setIsLoading', false)
    }
  },
  mounted() {
    if (!axios.defaults.headers.common['Authorization']){
      this.$router.push("/login")
    }
    this.getMyOrders()
  }
}
</script>