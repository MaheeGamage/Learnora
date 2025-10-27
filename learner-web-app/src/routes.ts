import { type RouteConfig, layout, route } from "@react-router/dev/routes";

export default [
  layout("./common/layouts/dashboard.tsx", [
    route("/", "./pages/home.tsx"),
    route("/orders", "./pages/orders.tsx"),
  ]),

  // Temp for development
  route("/temp/signin", "./other/SignIn.tsx"),

  // * matches all URLs, the ? makes it optional so it will match / as well
  route("*?", "catchall.tsx"),
] satisfies RouteConfig;
