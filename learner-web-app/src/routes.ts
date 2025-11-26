import {layout, route, type RouteConfig} from "@react-router/dev/routes";

export default [
    layout("./common/layouts/dashboard.tsx", [
        route("/", "./pages/home.tsx"),
        route("/evaluate/:learningPathId?", "./pages/evaluate.tsx"),
        route("/learning-path", "./pages/LearningPath.tsx"),
        route("/content", "./pages/content.tsx"),
    ]),

    // Authentication
    route("/sign-in", "./pages/sign-in.tsx"),
    route("/register", "./pages/register.tsx"),
    route("/forgot-password", "./pages/forget-password.tsx"),

    // * matches all URLs, the ? makes it optional so it will match / as well
    route("*?", "catchall.tsx"),
] satisfies RouteConfig;
