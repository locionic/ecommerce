<template>
  <div class="modal" :class="{ 'is-active': active }">
    <div class="modal-background"></div>
    <div class="modal-card">
      <header class="modal-card-head">
        <p class="modal-card-title">{{titleParam}}</p>
        <button class="delete" aria-label="close" @click="$emit('unactiveDialog')"></button>
      </header>
      <section class="modal-card-body">
        <!-- Content ... -->
        <div class="content">
          <template v-for="(attribute, index) in listAttribute" v-bind:key="index + '-' + attribute">
            <div class="field is-horizontal">
              <div class="field-label is-normal">
                <label class="label">{{ attribute }}</label>
              </div>
              <div class="field-body">
                <div class="field" :class="{ 'pt-1': attribute == 'avatar' }">
                  <p class="control">
                    <template v-if="attribute == 'email'">
                      <input class="input" type="email" :value="objectParam[attribute]" readonly disabled>
                    </template>
                    <template v-else-if="attribute == 'avatar'">
                      <div v-if="!item.image">
                        <input type="file" @change="onFileChange(item, $event)">
                      </div>
                      <div v-else>
                        <img :src="item.image" width="200" height="200" style="display: block;" />
                        <button @click="removeImage(item)">Remove image</button>
                      </div>
                    </template>
                    <template v-else>
                      <input class="input" type="text" v-model="form[attribute]">
                    </template>
                  </p>
                </div>
              </div>
            </div>
          </template>
        </div>
      </section>
      <footer class="modal-card-foot">
        <button class="button is-success" @click="submit">Save changes</button>
        <button class="button" @click="$emit('unactiveDialog')">Cancel</button>
      </footer>
    </div>
  </div>
</template>
<script>
import axios from "axios";
import {toast} from "bulma-toast";

export default {
  name: "MyDialog",
  props: {
    objectParam: Object,
    listAttribute: Array,
    titleParam: String,
    active: Boolean,
    
  },
  data() {
    return {
      base64regex: /^([0-9a-zA-Z+/]{4})*(([0-9a-zA-Z+/]{2}==)|([0-9a-zA-Z+/]{3}=))?$/,
      item: {
        image: this.objectParam.avatar
      },
      form: {

      }
    }
  },
  mounted() {
    this.initial()
  },
  watch: {
    objectParam() {
      this.initial()
    }
  },
  methods: {
    initial() {
      this.listAttribute.forEach(ele => {
        this.form[ele] = this.objectParam[ele]
      })
    },
    testBase64(value) {
      return this.base64regex.test(value)
    },
    submit() {
      this.form['avatar'] = this.item.image
      let formsubmit = {}
      this.listAttribute.forEach(ele => {
        if (this.form[ele] != this.objectParam[ele]) {
          formsubmit[ele] = this.form[ele]
        }
      })
      if (Object.keys(formsubmit).length !== 0)
      axios
            .patch(`/api/v1/users/${this.objectParam.username}`, formsubmit)
            .then(response =>{
              console.log(response)
              toast({
                message: 'Modify success!',
                type:'is-success',
                dismissible: true,
                pauseOnHover: true,
                duration: 2000,
                position: "bottom-right",
              })
              this.$emit('resetUser')
        })
            .catch(error =>{
              if (error.response){
                // for(const property in error.response.data){
                //   this.errors.push(
                //       `${property.charAt(0).toUpperCase() + property.slice(1)}: ${error.response.data[property]}`
                //   )
                //   document.getElementById(`${property}-input`).setAttribute('class', 'input is-danger')
                // }
                console.log(JSON.stringify(error.response.data))
              }else if(error.message){
                // this.errors.push(`Something went wrong, Please try again`)
                console.log(JSON.stringify(error))
              }
            }
        )
    },
    updateForm(event, attribute) {
      this.form[attribute] = event.target.value
    },
    onFileChange(item, e) {
      var files = e.target.files || e.dataTransfer.files;
      if (!files.length)
        return;
      this.createImage(item, files[0]);
    },
    createImage(item, file) {
      var reader = new FileReader();

      reader.onload = (e) => {
        this.item.image = e.target.result;
      };
      reader.readAsDataURL(file);
    },
    removeImage: function (item) {
      item.image = null;
    }
  }
}
</script>