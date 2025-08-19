import {
  type RouteConfig,
  route,
  layout,
  index,
} from "@react-router/dev/routes";

export const routes = [
  layout("pulse/_layout.tsx", [
    index("pulse/routes/index.tsx"),
  ]),
] satisfies RouteConfig;
