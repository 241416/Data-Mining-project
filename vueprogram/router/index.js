import Vue from 'vue'
import Router from 'vue-router'
import Test from "../components/Test";
Vue.use(Router)
 
export default new Router({
  mode: 'history',
  routes: [
		  {
		      path: '/t',
		      name: 'Test',
		      component: Test,
		      hidden:true
		    },
    	]
    })