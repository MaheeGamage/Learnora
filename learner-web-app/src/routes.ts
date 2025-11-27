import { type RouteConfig, layout, route } from "@react-router/dev/routes";

export default [
  layout("./common/layouts/dashboard.tsx", [
    route("/", "./pages/home.tsx"),
    route("/evaluate/:learningPathId?", "./pages/evaluate.tsx"),
    route("/learning-path", "./pages/LearningPath.tsx"),
    route("/content", "./pages/content.tsx"),
  ]),

  // Authentication
  route("/sign-in", "./pages/sign-in.tsx"),
  route("/sign-up", "./pages/sign-up.tsx"),

  // * matches all URLs, the ? makes it optional so it will match / as well
  route("*?", "catchall.tsx"),
] satisfies RouteConfig;
