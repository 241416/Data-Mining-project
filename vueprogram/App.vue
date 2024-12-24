<template>
  <!-- <img alt="Vue logo" src="./assets/logo.png"> -->
  <HelloWorld msg="Agent模拟情况可视化"/>
  <TurnGraph/>
  
</template>



<script>
import HelloWorld from './components/HelloWorld.vue'
import TurnGraph from "./components/TurnGraph.vue"; // 引入 Graph 组件
export default {
  name: 'App',
  components: {
    HelloWorld,
    TurnGraph,
  }
}
</script>

<style>
#app {
  font-family: Avenir, Helvetica, Arial, sans-serif;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
  text-align: center;
  color: #2c3e50;
  /* margin-top: 60px; */
}
</style>
