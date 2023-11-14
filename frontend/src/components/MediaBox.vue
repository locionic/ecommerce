<template>
  <div class="box">
    <article class="media">
      <div class="media-left">
        <figure class="image is-64x64">
            <img v-if="objectParam.created_by && objectParam.created_by.avatar" :src="objectParam.created_by.avatar" alt="Image">
            <img v-else src="https://bulma.io/images/placeholders/128x128.png" alt="An avatar">
        </figure>
      </div>
      <div class="media-content">
        <div class="content" style="margin-bottom: unset;">
          <p>
            <strong>{{listNames[0]}}</strong> <small>{{listNames[1]}}</small> <small>{{$filters.timeAgo(this.objectParam.created_at)}}</small>
            <br>
            {{objectParam.content}}
          </p>
        </div>
        <star-rating v-model:rating="rating" :star-size="15" :show-rating="false" :read-only="true" />
      </div>
    </article>
  </div>
</template>
<script>
import StarRating from 'vue-star-rating'
export default {
  name: "MediaBox",
  props: {
    objectParam: Object
  },
  components: {
    StarRating
  },
  data() {
    return {
      listNames: this.objectParam.created_by ? [this.objectParam.created_by.first_name + ' ' + this.objectParam.created_by.last_name, '@' + this.objectParam.created_by.email] : ['Anonymous', '@anonymous'],
      rating: this.objectParam.rate,
    }
  },
  methods: {
    initialData() {
      this.listNames = this.objectParam.created_by ? [this.objectParam.created_by.first_name + ' ' + this.objectParam.created_by.last_name, '@' + this.objectParam.created_by.email] : ['Anonymous', '@anonymous']
      this.rating = this.objectParam.rate
    }
  },
  watch: {
    objectParam() {
      this.initialData()
    }
  }
}
</script>