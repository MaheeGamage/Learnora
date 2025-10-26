import { type RouteConfig, route } from "@react-router/dev/routes";

export default [
  route("/login", "./pages/LoginPage.tsx"),
  // * matches all URLs, the ? makes it optional so it will match / as well
  route("*?", "catchall.tsx"),
] satisfies RouteConfig;
