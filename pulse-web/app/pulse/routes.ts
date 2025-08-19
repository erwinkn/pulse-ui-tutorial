import {
  type RouteConfig,
  route,
  layout,
  index,
} from "@react-router/dev/routes";

export const routes = [
  layout("pulse/_layout.tsx", [
    layout("pulse/layouts/_layout.tsx", [
      index("pulse/routes/index.tsx"),
      route("task/:id", "pulse/routes/task/:id.tsx"),
      route("settings", "pulse/routes/settings.tsx"),
    ]),
  ]),
] satisfies RouteConfig;
