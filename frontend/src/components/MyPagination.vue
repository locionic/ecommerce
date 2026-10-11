<template>
  <nav class="pagination is-centered is-rounded" role="navigation" aria-label="pagination">
    <a class="pagination-previous" @click.prevent="$emit('getResults', previous)" :class="{ 'is-disabled': !previous }">Previous</a>
    <a class="pagination-next" @click.prevent="$emit('getResults', next)" :class="{ 'is-disabled': !next }">Next page</a>
    <ul class="pagination-list">
      <li v-for="index in Math.ceil(count/pageSize)" :key="index">
        <a class="pagination-link" :class="{ 'is-current': page == index }" :aria-label="'Go to page ' + index" @click.prevent="$emit('getResults', pageUrl(index))"> {{index}} </a>
      </li>
    </ul>
  </nav>
</template>
<script>
export default {
  name: "MyPagination",
  props: {
    next: String,
    previous: String,
    count: Number,
    page: Number,
    defaultApiGet: String
  },
  data() {
    return {
      pageSize: 20
    }
  },
  methods: {
    pageUrl(index) {
      // `defaultApiGet` may already carry query params (a search term, a category
      // filter), so the page number has to be merged rather than appended blindly.
      const separator = this.defaultApiGet.includes('?') ? '&' : '?'
      return `${this.defaultApiGet}${separator}page=${index}`
    }
  }
}
</script>