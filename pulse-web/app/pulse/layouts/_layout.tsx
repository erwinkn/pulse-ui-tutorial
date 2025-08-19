import { redirect, type LoaderFunctionArgs } from "react-router";
import { PulseView, type VDOM, type ComponentRegistry, extractServerRouteInfo } from "pulse-ui-client";

// Component imports
import { Link } from "react-router";
import { Outlet } from "react-router";

// Component registry
const externalComponents: ComponentRegistry = {
  // SSR-capable import
  "Link": Link,
  // SSR-capable import
  "Outlet": Outlet,
};

const path = "<layout>";

export async function loader(args: LoaderFunctionArgs) {
  const routeInfo = extractServerRouteInfo(args);
  // Forward inbound headers (cookies, auth, user-agent, etc.) to the Python server
  const fwd = new Headers(args.request.headers);
  // These request-specific headers must be recomputed for the new request
  fwd.delete("content-length");
  // Ensure JSON body content type
  fwd.set("content-type", "application/json");
  const res = await fetch("http://localhost:8001" + "/prerender/" + path, {
    method: "POST",
    headers: fwd,
    body: JSON.stringify(routeInfo),
    redirect: "manual",
  });
  if (res.status === 404) {
    return redirect("/not-found");
  }
  if (res.status === 302 || res.status === 301) {
    const location = res.headers.get("Location");
    if (location) {
      return redirect(location);
    }
  }
  if (!res.ok) {
    throw new Error(
      "Failed to fetch prerender route /"+ path+ ": " + res.status + " " + res.statusText
    );
  }
  const vdom = await res.json();
  return vdom;
}

export default function RouteComponent({ loaderData }: { loaderData: VDOM }) {
  return (
    <PulseView
      key={path}
      initialVDOM={loaderData}
      externalComponents={externalComponents}
      path={path}
    />
  );
}
