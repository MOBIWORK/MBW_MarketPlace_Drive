import { createRouter, createWebHistory } from "vue-router"
import store from "./store"

function redir404(to, from, next) {
  if (store.getters.isLoggedIn) {
    next()
  } else {
    next("drive/login")
  }
}

function clearStore(to, from) {
  if (from.name === "Document" || to.name === "Document") {
    store.commit("setShowInfo", false)
    return
  } else {
    store.commit("setEntityInfo", [])
    store.commit("setCurrentFolder", [])
    store.commit("setCurrentViewEntites", [])
  }
}

function setRootBreadCrumb(to) {
  if (store.getters.isLoggedIn) {
    document.title = to.name
    store.commit("setCurrentBreadcrumbs", [{ label: to.name, route: to.path }])
  }
}

const routes = [
  {
    path: "/",
    redirect: () => {
      if (store.getters.isLoggedIn) {
        const role = store.state.user?.role
        return role === "Drive Guest" ? "/recents" : "/home"
      }
      return "/login"
    },
  },
  {
    path: "/notifications",
    name: "Notifications",
    component: () => import("@/pages/Notifications.vue"),
    beforeEnter: [setRootBreadCrumb, clearStore],
  },
  {
    path: "/home",
    name: "Home",
    component: () => import("@/pages/Home.vue"),
    beforeEnter: [setRootBreadCrumb, clearStore],
  },
  {
    path: "/file/:entityName",
    name: "File",
    component: () => import("@/pages/File.vue"),
    meta: { sidebar: true, isHybridRoute: true, filePage: true },
    props: true,
  },
  {
    path: "/folder/:entityName",
    name: "Folder",
    component: () => import("@/pages/Folder.vue"),
    meta: { sidebar: true, isHybridRoute: true },
    props: true,
  },
  {
    path: "/document/:entityName",
    name: "Document",
    meta: { sidebar: false, documentPage: true, isHybridRoute: true },
    component: () => import("@/pages/Document.vue"),
    props: true,
    beforeEnter: [clearStore],
  },
  {
    path: "/recents",
    name: "Recents",
    component: () => import("@/pages/Recents.vue"),
    beforeEnter: [setRootBreadCrumb, clearStore],
  },
  {
    path: "/shared",
    name: "Shared",
    component: () => import("@/pages/Shared.vue"),
    beforeEnter: [setRootBreadCrumb, clearStore],
  },
  {
    path: "/favourites",
    name: "Favourites",
    component: () => import("@/pages/Favourites.vue"),
    beforeEnter: [setRootBreadCrumb],
  },
  {
    path: "/trash",
    name: "Trash",
    component: () => import("@/pages/Trash.vue"),
    beforeEnter: [setRootBreadCrumb, clearStore],
  },
  {
    path: "/test",
    name: "Test",
    component: () => import("@/pages/Test.vue"),
  },
  {
    path: "/login",
    name: "Login",
    component: () => import("@/pages/Login.vue")
  },
  {
    path: "/signup",
    name: "SignupPage",
    component: () => import("@/pages/Signup.vue")
  },
  {
    path: "/:pathMatch(.*)*/",
    name: "Error",
    component: () => import("@/pages/Error.vue"),
    beforeEnter: [redir404, clearStore],
    meta: {
      errorPage: true,
    },
    props: true,
  },
]

let router = createRouter({
  history: createWebHistory("/drive"),
  routes,
})

router.beforeEach((to, from, next) => {
  const isLoggedIn = store.getters.isLoggedIn;

  if (!isLoggedIn && to.path !== "/login" && to.path !== "/signup") {
    // Chưa đăng nhập, chuyển hướng đến login nếu không phải route công khai
    next("/login");
  } else if (isLoggedIn && (to.path === "/login" || to.path === "/signup")) {
    // Đã đăng nhập mà truy cập login hoặc signup, chuyển hướng đến home
    if (to.path !== "/home") {
      next("/home");
    } else {
      next(); // Nếu đã ở /home thì không cần chuyển hướng
    }
  } else if (isLoggedIn && to.path === "/") {
    // Nếu người dùng đã đăng nhập và truy cập root "/"
    next("/home");
  } else {
    // Các route hợp lệ khác
    next();
  }
});

router.afterEach((to) => {
  sessionStorage.setItem("currentRoute", to.href)
})

export default router
