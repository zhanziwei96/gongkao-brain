import { createRouter, createWebHistory } from 'vue-router'
import LoginView from '../views/LoginView.vue'
import RegisterView from '../views/RegisterView.vue'
import DashboardView from '../views/DashboardView.vue'
import AptitudeQuestionList from '../views/AptitudeQuestionList.vue'
import AptitudeQuestionForm from '../views/AptitudeQuestionForm.vue'

const router = createRouter({
  history: createWebHistory(),
  routes: [
    { path: '/login', component: LoginView },
    { path: '/register', component: RegisterView },
    { path: '/', component: DashboardView, meta: { requiresAuth: true } },
    { path: '/aptitude/questions', component: AptitudeQuestionList, meta: { requiresAuth: true } },
    { path: '/aptitude/questions/new', component: AptitudeQuestionForm, meta: { requiresAuth: true } },
    { path: '/aptitude/questions/:id/edit', component: AptitudeQuestionForm, meta: { requiresAuth: true } },
  ]
})

router.beforeEach((to, _from, next) => {
  const token = localStorage.getItem('token')
  if (to.meta.requiresAuth && !token) {
    next('/login')
  } else {
    next()
  }
})

export default router
