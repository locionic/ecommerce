<template>
  <div class="dropdown" :class="{ 'is-active': active }">
    <div class="dropdown-trigger">
      <button class="button" aria-haspopup="true" aria-controls="dropdown-menu2" @click="active = !active">
        <span>View detail</span>
        <span class="icon is-small">
          <i class="fas fa-angle-down" aria-hidden="true"></i>
        </span>
      </button>
    </div>
    <div class="dropdown-menu" id="dropdown-menu2" role="menu">
      <div class="dropdown-content">
        <table class="table is-bordered dropdown-item">
          <thead>
            <tr>
              <th v-for="(detail, index) in $store.state.showDetail" :key="index + 'th'">{{ detail }}</th>
            </tr>
          </thead>
          <tbody>
            <tr>
              <td v-for="(detail, index) in $store.state.showDetail" :key="index + 'td'">
                <template v-if="detail == 'created_at'">
                  {{ $filters.yyyymmddthhmmsszToNormal(order[detail]) }}
                </template>
                <template v-else>
                  {{ order[detail] }}
                </template>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>
  </div>
</template>
<script>
export default {
  name: "MyDropdown",
  props:{
    order:Object
  },
  data() {
    return {
      active: false
    }
  }
}
</script>