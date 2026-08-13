<template>
  <div class="page-sign-up">
    <div class="columns mt-6">
      <div class="column is-4 is-offset-4">
        <div class="box glass-box p-6">
          <h1 class="title is-2 mb-5 has-text-centered">Create Account</h1>
          <form @submit.prevent="submitForm">
            <div class="field mb-4">
              <label>Username</label>
              <div class="control">
                <input type="text" class="input custom-input" id="username-input" v-model="username">
              </div>
            </div>
            <div class="field mb-4">
              <label>Email</label>
              <div class="control">
                <input type="email" class="input custom-input" id="email-input" v-model="email">
              </div>
            </div>
            <div class="field mb-4">
              <label>Password</label>
              <div class="control">
                <input type="password" class="input custom-input" id="password-input" v-model="password">
              </div>
            </div>

            <div class="field mb-5">
              <label>Repeat password</label>
              <div class="control">
                <input type="password" class="input custom-input" id="password2-input" v-model="password2">
              </div>
            </div>

          <div class="notification is-danger" v-if="errors.length">
            <p v-for="error in errors" v-bind:key="error">{{error}}</p>
          </div>

          <div class="field mt-5">
            <div class="control">
              <button class="button is-primary is-fullwidth submit-btn is-medium">Sign up</button>
            </div>
          </div>
          <hr class="glass-hr">
          <p class="has-text-centered">Already have an account? <router-link to="/login" class="has-text-primary">Log in</router-link></p>
        </form>
        </div>
      </div>
    </div>
  </div>
</template>
<script>

import axios from "axios";
import {toast} from "bulma-toast";

export default {
  name: 'SignupView',
  data() {
    return{
      username: '',
      email:'',
      password: '',
      password2: '',
      errors: []
    }
  },
  methods:{
    submitForm: function (){
      this.errors = []
      if (this.username === ''){
        this.errors.push('The username is missing')
        document.getElementById('username-input').setAttribute('class', 'input is-danger')
      }
      if(this.email === ''){
        this.errors.push('The email is missing')
        document.getElementById('email-input').setAttribute('class', 'input is-danger')
      }
      if(this.password === ''){
        this.errors.push('The password is too short')
        document.getElementById('password-input').setAttribute('class', 'input is-danger')
      }
      if(this.password2 !== this.password){
        this.errors.push("The passwords doesn't match")
        document.getElementById('password-input').setAttribute('class', 'input is-danger')
        document.getElementById('password2-input').setAttribute('class', 'input is-danger')
      }
      if(!this.errors.length){
        const formData = {
          username: this.username,
          email: this.email,
          password: this.password,
        }
        axios
            .post('/api/v1/users/', formData)
            .then(response =>{
              console.log(response)
              toast({
                message: 'Account created, please log in!',
                type:'is-success',
                dismissible: true,
                pauseOnHover: true,
                duration:2000,
                position: "bottom-right",
              })
                this.$router.push('/login')
        })
            .catch(error =>{
              if (error.response){
                for(const property in error.response.data){
                  this.errors.push(
                      `${property.charAt(0).toUpperCase() + property.slice(1)}: ${error.response.data[property]}`
                  )
                  const el = document.getElementById(`${property}-input`);
                  if (el) el.setAttribute('class', 'input is-danger custom-input');
                }
                console.log(JSON.stringify(error.response.data))
              }else if(error.message){
                this.errors.push(`Something went wrong, Please try again`)
                console.log(JSON.stringify(error))
              }
            }
        )

      }
    },
  }
}
</script>

<style scoped>
.page-sign-up {
  padding-bottom: 4rem;
}
.glass-box {
  border-radius: 20px;
  border: 1px solid rgba(255,255,255,0.05);
  box-shadow: 0 10px 25px -5px rgba(0, 0, 0, 0.5);
  background: rgba(255,255,255,0.03);
  backdrop-filter: blur(10px);
}
.custom-input {
  background: rgba(255,255,255,0.05);
  border: 1px solid rgba(255,255,255,0.1);
  color: #fff;
  border-radius: 8px;
}
.custom-input:focus {
  border-color: #00F0FF;
  box-shadow: 0 0 0 2px rgba(0,240,255,0.2);
}
.submit-btn {
  background: linear-gradient(135deg, #00F0FF 0%, #6366F1 100%);
  border: none;
  color: white;
  border-radius: 12px;
  box-shadow: 0 10px 15px -3px rgba(0, 240, 255, 0.3);
}
.submit-btn:hover {
  transform: translateY(-2px);
  box-shadow: 0 15px 20px -3px rgba(0, 240, 255, 0.4);
}
.glass-hr {
  background-color: rgba(255,255,255,0.1);
  height: 1px;
  border: none;
  margin: 1.5rem 0;
}
</style>