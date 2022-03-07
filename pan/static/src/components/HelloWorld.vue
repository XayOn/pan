<template>
  <div class=form-inline v-for="(pai, key) in pains" v-bind:key="pai.ip">
    <div class=row :id=pai.ip style="margin-right:40px">
      <div class=col><h3 style="margin-top:10px!important; text-align:right">{{key}}</h3></div>
      <div class=col>
        <select class=form-control v-model=pai.status>
          <option value=disabled>Disabled</option>
          <option value=emitter>Sound Source</option>
          <option value=receiver>Speaker</option>
        </select>
      </div>
      <div class=col>
        <select  v-if="pai.status=='receiver'" class=form-control v-on:change=setIp>
          <option data-origpai=pai.ip
                  v-for="(lpai, lkey) in lpains"
                  v-bind:key=lpai.ip value=lpai.ip>
            {{lkey}}
          </option>
        </select>
      </div>
    </div>
  </div>
  <button class="btn btn-success btn-lg" @click=save>Save</button>
</template>

<script>
import axios from 'axios';

export default {
  name: 'MainApp',
  props: {
  },
  computed: {
    lpains(){
      const elems = Object.entries(this.pains)
      return Object.fromEntries(elems.filter((pain) => pain[1].status == 'emitter'));
    }
  },
  mounted () {
    axios
      .get('/api/config')
      .then(response => (this.pains = response.data))
  },
  methods: {
    save() {
      for (let pain in this.pains) {
        // Emitters should have their own ip as remote_ip
        if (pain.status == 'emitter') {
          pain.remote_ip = pain.ip
        }
      }
      axios.post('api/config', this.pains).then(data => console.log(data));
    },
    setIp(event) {
      const value = event.target.value;
      const origpai = event.target.data.origpai;
      console.log(value);
      console.log(origpai);
    }
  },
  data () {
    return {
      pains: []
    }
  }
}
</script>

<!-- Add "scoped" attribute to limit CSS to this component only -->
<style scoped>
h3 {
  margin: 40px 0 0;
}
ul {
  list-style-type: none;
  padding: 0;
}
li {
  display: inline-block;
  margin: 0 10px;
}
a {
  color: #42b983;
}
</style>
