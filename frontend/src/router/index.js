import { createRouter, createWebHistory } from "vue-router";
import LoginPage from "../features/auth/views/LoginPage.vue";
import RegisterPage from "../features/auth/views/RegisterPage.vue";
import DashboardPage from "../features/auth/views/DashboardPage.vue";
import { useAuthStore } from "../features/auth/store/authStore.js"; // Импортируем хранилище

const routes = [
  {
    path: "/",
    redirect: () => {
      // Динамический редирект в зависимости от статуса логина
      // Важно: useAuthStore можно вызывать только внутри setup или lifecycle hook компонента,
      // либо после установки Pinia. Вне компонента, особенно при инициализации роутера,
      // нужно получить экземпляр Pinia и передать его в useAuthStore, или проверить localStorage напрямую.
      // Для простоты здесь можно сделать редирект на /login, а логику показа дашборда оставить в beforeEach
      // Либо, если Pinia уже инициализирована, то можно использовать store.
      // Предположим, что Pinia инициализируется до роутера в main.js
      // Однако, безопаснее проверять localStorage или иметь простой редирект по умолчанию.
      const accessToken = localStorage.getItem("accessToken");
      if (accessToken) {
        return "/dashboard";
      }
      return "/login";
    },
  },
  {
    path: "/login",
    name: "Login",
    component: LoginPage,
    meta: { requiresGuest: true }, // Для страниц, доступных только неавторизованным
  },
  {
    path: "/register",
    name: "Register",
    component: RegisterPage,
    meta: { requiresGuest: true }, // Для страниц, доступных только неавторизованным
  },
  {
    path: "/dashboard",
    name: "Dashboard",
    component: DashboardPage,
    meta: { requiresAuth: true }, // Эта страница требует аутентификации
  },
  // Можно добавить маршрут для 404 страницы
  // { path: '/:pathMatch(.*)*', name: 'NotFound', component: NotFoundComponent }
];

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes,
});

// Навигационный хук для защиты маршрутов
router.beforeEach((to, from, next) => {
  const authStore = useAuthStore(); // Получаем доступ к хранилищу

  const isAuthenticated = authStore.isLoggedIn;

  if (to.meta.requiresAuth && !isAuthenticated) {
    // Если маршрут требует аутентификации, а пользователь не вошел в систему,
    // перенаправляем на страницу входа.
    next({ name: "Login" });
  } else if (to.meta.requiresGuest && isAuthenticated) {
    // Если маршрут для гостей (например, /login, /register),
    // а пользователь уже вошел в систему, перенаправляем на дашборд.
    next({ name: "Dashboard" });
  } else {
    // В остальных случаях разрешаем навигацию.
    next();
  }
});

export default router;
