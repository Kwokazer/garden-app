import { createApp } from "vue";
import { createPinia } from "pinia";
import App from "./App.vue";
import router from "./router";

// Импортируем стили Bootstrap
import "bootstrap/dist/css/bootstrap.min.css";
// При необходимости можно импортировать и JavaScript Bootstrap
// import 'bootstrap/dist/js/bootstrap.bundle.min.js'

const app = createApp(App);

// Инициализируем Pinia ПЕРЕД роутером (важно для authStore в navigation guards)
app.use(createPinia());
app.use(router);

app.mount("#app");
