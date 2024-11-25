# TASK:
I am using plasmic.app to create a frontend for this app, it can be used in a react frontend. Based on the development information create a page that is accesable trough fly.io on port 443, so it is the index of the server.





# DEVELOPMENT INFO
Public token: 
i7Mll1LDifAnPmAQNw1D0OqOKCU98ESyuwoodLdUuYvshgwsX5SZ3mIY00C30UASzJl6A9HjfcAduzFQBvvw



Overview
This covers integrating Plasmic into your existing React codebase.


Want to quickly generate a new codebase with Plasmic already integrated? Use create-plasmic-app instead, or just press the Publish button in your project to push a new repo to GitHub!

Want to generate source code into your codebase (warning: advanced)? Learn about codegen.

Note that the plain React docs assume a single-page application with client-side rendering, and not server-side rendering or static rendering. Unlike with metaframeworks such as Next.js, how this is done is different for different environments—even the routing system can vary. If you’d like help more direct help integrating in your stack, please get in touch.

Installation
Copy
npm install @plasmicapp/loader-react
# or yarn add @plasmicapp/loader-react
Initialization
Initialize Plasmic with the project ID and public API token. Define this in its own module to make it available globally.

src/plasmic-init.tsCopy
import { initPlasmicLoader } from "@plasmicapp/loader-react";
export const PLASMIC = initPlasmicLoader({
  projects: [
    {
      id: "p41xhVExBoDuAHBPkXb1p1",  // ID of a project you are using
      token: "i7Mll1LDifAnPmAQNw1D0OqOKCU98ESyuwoodLdUuYvshgwsX5SZ3mIY00C30UASzJl6A9HjfcAduzFQBvvw"  // API token for that project
    }
  ],
  // Fetches the latest revisions, whether or not they were unpublished!
  // Disable for production to ensure you render only published changes.
  preview: true,
})

Auto load all Plasmic pages
To automatically render all Plasmic-defined pages at the routes specified in Plasmic, create a catch-all route for your specific routing framework.

Here is an example for react-router, both v5 and v6:


React Router v6

React Router v5
Copy
import {
  initPlasmicLoader,
  PlasmicRootProvider,
  PageParamsProvider,
  PlasmicComponent,
  ComponentRenderData
} from '@plasmicapp/loader-react';
import { BrowserRouter as Router, Routes, Route, Link, useLocation, useSearchParams } from 'react-router-dom';
import { useEffect, useState } from 'react';
import { PLASMIC } from './plasmic-init';

function AppRoot() {
  return (
    <PlasmicRootProvider loader={PLASMIC}>
      <Router>
        <Routes>
          <Route path="/" element={CatchAllPage()} />
        </Routes>
      </Router>
    </PlasmicRootProvider>
  );
}

// We try loading the Plasmic page for the current route.
// If it doesn't exist, then return "Not found."
export function CatchAllPage() {
  const [loading, setLoading] = useState(true);
  const [pageData, setPageData] = useState<ComponentRenderData | null>(null);
  const location = useLocation();
  const searchParams = useSearchParams();

  useEffect(() => {
    async function load() {
      const pageData = await PLASMIC.maybeFetchComponentData(location.pathname);
      setPageData(pageData);
      setLoading(false);
    }
    load();
  }, []);

  if (loading) {
    return <div>Loading...</div>;
  }
  if (!pageData) {
    return <div>Not found</div>;
  }
  // The page will already be cached from the `load` call above.
  return (
    <PageParamsProvider
      route={location.pathname}
      query={Object.fromEntries(searchParams)}
    >
      <PlasmicComponent component={location.pathname} />
    </PageParamsProvider>
  );
}